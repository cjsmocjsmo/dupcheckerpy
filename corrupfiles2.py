import os
from PIL import Image, UnidentifiedImageError

def Is_image_corrupt(image_path, size_threshold=(128, 128)):
    """
    Checks if an image file is corrupted, truncated, or likely an icon (small or transparent).
    Returns a tuple: (is_corrupt, message, is_icon, is_truncated)
    """
    if not os.path.exists(image_path):
        return True, "File path does not exist.", False, False
    try:
        with Image.open(image_path) as img:
            # Try to verify and load the image fully
            try:
                img.verify()
            except Exception as verify_e:
                return True, f"Image verify failed: {verify_e}", False, False
        # Reopen to actually access pixel data (verify() leaves file in unusable state)
        try:
            with Image.open(image_path) as img:
                try:
                    img.load()
                except Exception as load_e:
                    # Check for truncated JPEG error
                    if hasattr(load_e, 'args') and any('Corrupt JPEG data' in str(arg) for arg in load_e.args):
                        return True, f"Corrupt JPEG data: {load_e}", False, True
                    if hasattr(load_e, 'args') and any('Premature end of JPEG file' in str(arg) for arg in load_e.args):
                        return True, f"Premature end of JPEG file: {load_e}", False, True
                    return True, f"Image load failed: {load_e}", False, False
                # Check icon criteria
                is_icon = False
                if img.size[0] <= size_threshold[0] and img.size[1] <= size_threshold[1]:
                    is_icon = True
                elif img.mode in ("RGBA", "LA") or (img.mode == "P" and 'transparency' in img.info):
                    alpha = img.convert("RGBA").getchannel("A")
                    if alpha.getextrema()[0] < 255:
                        is_icon = True
                return False, "Image loaded successfully.", is_icon, False
        except Exception as e:
            return True, f"An unexpected error occurred during processing: {e}", False, False
    except Exception as e:
        return True, f"An unexpected error occurred during processing: {e}", False, False

    # Function removed: logic merged into Is_image_corrupt

def check_directory_for_corrupted_images_recursive(root_directory):
    """
    Recursively walks through a directory and its subdirectories, 
    checks for images, and reports on their status and count.
    """
    # Define common image file extensions to look for (lowercase for comparison)
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']
    
    import concurrent.futures
    corrupted_images = []
    possible_icons = []
    image_paths = []
    total_files_checked = 0

    print(f"--- Checking Images Recursively in: {root_directory} ---")

    # Collect all image paths first
    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in IMAGE_EXTENSIONS:
                image_path = os.path.join(dirpath, filename)
                image_paths.append(image_path)

    total_files_checked = len(image_paths)

    def process_image(image_path):
        is_corrupt, message, is_icon, is_truncated = Is_image_corrupt(image_path)
        if is_corrupt:
            print(f"❌ Corrupted: {image_path} -> {message}")
            try:
                os.remove(image_path)
                print(f"Deleted: {image_path}")
            except Exception as e:
                print(f"Failed to delete {image_path}: {e}")
            return (image_path, True, False)
        if is_truncated:
            print(f"❌ Corrupted (Premature end of JPEG file): {image_path}")
            try:
                os.remove(image_path)
                print(f"Deleted: {image_path}")
            except Exception as e:
                print(f"Failed to delete {image_path}: {e}")
            return (image_path, True, False)
        if is_icon:
            return (image_path, False, True)
        return (image_path, False, False)

    # Use ThreadPoolExecutor for I/O bound tasks
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(process_image, image_paths))
    for image_path, is_corrupt, is_icon in results:
        if is_corrupt:
            corrupted_images.append(image_path)
        if is_icon:
            possible_icons.append(image_path)

    print(f"\n--- Summary 📊 ---")
    print(f"Total image files checked: **{total_files_checked}**")
    valid_count = total_files_checked - len(corrupted_images)
    print(f"Valid images found: **{valid_count}**")
    if corrupted_images:
        print(f"Corrupted images found and deleted: **{len(corrupted_images)}**.")
        print("\nCorrupted image list (Full Path):")
        for path in corrupted_images:
            print(f"- {path}")
    else:
        print("No corrupted images were found.")
    if possible_icons:
        print(f"\nPossible icons found: **{len(possible_icons)}**.")
        print("Possible icon image list (Full Path):")
        for path in possible_icons:
            print(f"- {path}")
    else:
        print("No possible icons were found.")
    return corrupted_images, possible_icons

# --- Example Usage ---
# CHANGE THIS PATH to the root directory you want to check recursively
target_directory = "/media/piir/PiTB/PICTURES/NewPics" 

if __name__ == "__main__":
    if not os.path.isdir(target_directory):
        print(f"Error: Directory not found at {target_directory}")
    else:
        corrupted_files, possible_icons = check_directory_for_corrupted_images_recursive(target_directory)

        # Move possible icons to ./possible_icons
        import shutil
        icon_dir = os.path.join(os.getcwd(), "possible_icons")
        if not os.path.exists(icon_dir):
            os.makedirs(icon_dir)
        import stat
        for icon_path in possible_icons:
            dest_path = os.path.join(icon_dir, os.path.basename(icon_path))
            try:
                shutil.move(icon_path, dest_path)
                print(f"Moved icon: {icon_path} -> {dest_path}")
            except PermissionError:
                try:
                    os.chmod(icon_path, stat.S_IWUSR | stat.S_IRUSR)
                    shutil.move(icon_path, dest_path)
                    print(f"Changed permissions and moved icon: {icon_path} -> {dest_path}")
                except Exception as e:
                    print(f"Failed to move icon {icon_path} after changing permissions: {e}")
            except Exception as e:
                print(f"Failed to move icon {icon_path}: {e}")
