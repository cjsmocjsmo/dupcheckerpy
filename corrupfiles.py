import cv2
import os
import numpy as np

def is_image_corrupted(image_path):
    """
    Checks if an image file at the given path is corrupted or invalid 
    by attempting to load it with OpenCV.
    """
    # Check if the file exists before attempting to read
    if not os.path.exists(image_path):
        return True, "File path does not exist."
        
    try:
        # Attempt to read the image with OpenCV
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        # Check 1: Check if the image array is None (failure to decode/corrupted data)
        if img is None:
            return True, "Image could not be decoded (likely corrupted or unsupported format)."
        # Check 2: Check if the resulting array has zero size
        if img.size == 0:
            return True, "Loaded image array has zero size."
        # Additional check for JPEGs: use PIL to fully load image data
        ext = os.path.splitext(image_path)[1].lower()
        if ext in ['.jpg', '.jpeg']:
            try:
                import warnings
                from PIL import Image, UnidentifiedImageError
                with warnings.catch_warnings():
                    warnings.simplefilter('error')  # Treat warnings as errors
                    with Image.open(image_path) as pil_img:
                        pil_img.load()  # Force loading all image data
            except Exception as pil_e:
                return True, f"PIL load failed or warning: {pil_e}"
        return False, "Image loaded successfully."
    except Exception as e:
        # Catch unexpected errors during the file read process
        return True, f"An unexpected error occurred during processing: {e}"

def is_possible_icon(image_path, size_threshold=(128, 128)):
    """
    Checks if an image is likely an icon by filtering on size and transparency.
    Returns True if the image is below the size threshold or has transparency.
    """
    try:
        from PIL import Image, UnidentifiedImageError
        with Image.open(image_path) as img:
            # Check size
            if img.size[0] <= size_threshold[0] and img.size[1] <= size_threshold[1]:
                return True, False
            # Check transparency
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and 'transparency' in img.info):
                alpha = img.convert("RGBA").getchannel("A")
                if alpha.getextrema()[0] < 255:
                    return True, False
            return False, False
    except Exception as e:
        # Check for truncated JPEG error
        if hasattr(e, 'args') and any('Premature end of JPEG file' in str(arg) for arg in e.args):
            return False, True
        return False, False

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
        is_corrupt, message = is_image_corrupted(image_path)
        if is_corrupt:
            print(f"❌ Corrupted: {image_path} -> {message}")
            try:
                os.remove(image_path)
                print(f"Deleted: {image_path}")
            except Exception as e:
                print(f"Failed to delete {image_path}: {e}")
            return (image_path, True, False)
        else:
            is_icon, is_truncated = is_possible_icon(image_path)
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
target_directory = "/media/piir/PiTB/PICTURES/oldcrap" 

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
