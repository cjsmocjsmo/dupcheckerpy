import os
from concurrent.futures import ThreadPoolExecutor

from PIL import Image, UnidentifiedImageError

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'}
MAX_WORKERS = 2

class CorruptFiles:
    def __init__(self, directory):
        self.root_dir = directory


    def inspect_image(self, image_path, size_threshold=(128, 128)):
        """
        Checks if an image file at the given path is corrupted or invalid.
        Also flags likely icons based on small dimensions or transparency.
        """
        if not os.path.exists(image_path):
            return True, False, "File path does not exist."

        try:
            with Image.open(image_path) as img:
                img.load()

                is_icon = False
                if img.width <= size_threshold[0] and img.height <= size_threshold[1]:
                    is_icon = True
                elif img.mode in ("RGBA", "LA") or (img.mode == "P" and 'transparency' in img.info):
                    alpha = img.convert("RGBA").getchannel("A")
                    if alpha.getextrema()[0] < 255:
                        is_icon = True

                return False, is_icon, "Image loaded successfully."
        except (UnidentifiedImageError, OSError) as e:
            return True, False, f"Image could not be decoded: {e}"
        except Exception as e:
            return True, False, f"An unexpected error occurred during processing: {e}"

    def iter_image_paths(self):
        for dirpath, _, filenames in os.walk(self.root_dir):
            for filename in filenames:
                if os.path.splitext(filename)[1].lower() in IMAGE_EXTENSIONS:
                    yield os.path.join(dirpath, filename)

    def check_directory_for_corrupted_images_recursive(self):
        """
        Recursively walks through a directory and its subdirectories, 
        checks for images, and reports on their status and count.
        """
        corrupted_images = []
        possible_icons = []
        total_files_checked = 0

        print(f"--- Checking Images Recursively in: {self.root_dir} ---")

        def process_image(image_path):
            is_corrupt, is_icon, message = self.inspect_image(image_path)
            if is_corrupt:
                print(f"Corrupted: {image_path} -> {message}")
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"Failed to delete {image_path}: {e}")
                return image_path, True, False
            if is_icon:
                return image_path, False, True
            return image_path, False, False

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            for image_path, is_corrupt, is_icon in executor.map(process_image, self.iter_image_paths()):
                total_files_checked += 1
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


    def corruptfiles_main(self):
        if not os.path.isdir(self.root_dir):
                print(f"Error: Directory not found at {self.root_dir}")
        else:
            corrupted_images, possible_icons = self.check_directory_for_corrupted_images_recursive()

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

if __name__ == "__main__":
    target_directory = "/media/piir/PiTB/PICTURES/NewPics"  # Replace with the path to your target directory
    CorruptFiles(target_directory).corruptfiles_main()
