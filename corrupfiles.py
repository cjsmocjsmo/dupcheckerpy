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
        # Attempt to read the image
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        
        # Check 1: Check if the image array is None (failure to decode/corrupted data)
        if img is None:
            return True, "Image could not be decoded (likely corrupted or unsupported format)."
        
        # Check 2: Check if the resulting array has zero size
        if img.size == 0:
            return True, "Loaded image array has zero size."
            
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
        from PIL import Image
        img = Image.open(image_path)
        # Check size
        if img.size[0] <= size_threshold[0] and img.size[1] <= size_threshold[1]:
            return True
        # Check transparency
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and 'transparency' in img.info):
            alpha = img.convert("RGBA").getchannel("A")
            if alpha.getextrema()[0] < 255:
                return True
        return False
    except Exception:
        return False

def check_directory_for_corrupted_images_recursive(root_directory):
    """
    Recursively walks through a directory and its subdirectories, 
    checks for images, and reports on their status and count.
    """
    # Define common image file extensions to look for (lowercase for comparison)
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']
    
    corrupted_images = []
    possible_icons = []
    total_files_checked = 0
    
    print(f"--- Checking Images Recursively in: {root_directory} ---")
    
    # os.walk yields (dirpath, dirnames, filenames) for each directory it visits
    for dirpath, _, filenames in os.walk(root_directory):
        
        for filename in filenames:
            # Get the file extension and convert to lowercase for robust comparison
            ext = os.path.splitext(filename)[1].lower()
            
            # Check if the file is an image based on its extension
            if ext in IMAGE_EXTENSIONS:
                
                # Construct the full file path
                image_path = os.path.join(dirpath, filename)
                
                # Increment the counter for every file processed
                total_files_checked += 1
                
                is_corrupt, message = is_image_corrupted(image_path)
                if is_corrupt:
                    print(f"❌ Corrupted: {image_path} -> {message}")
                    corrupted_images.append(image_path)
                else:
                    if is_possible_icon(image_path):
                        possible_icons.append(image_path)

    print(f"\n--- Summary 📊 ---")
    print(f"Total image files checked: **{total_files_checked}**")
    valid_count = total_files_checked - len(corrupted_images)
    print(f"Valid images found: **{valid_count}**")
    if corrupted_images:
        print(f"Corrupted images found: **{len(corrupted_images)}**.")
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
target_directory = "/media/piir/PiTB/PICTURES/" 

if __name__ == "__main__":
    if not os.path.isdir(target_directory):
        print(f"Error: Directory not found at {target_directory}")
    else:
        corrupted_files, possible_icons = check_directory_for_corrupted_images_recursive(target_directory)
        if corrupted_files:
            answer = input("\nDo you want to delete the corrupted files listed above? (y/N): ").strip().lower()
            if answer == 'y':
                for path in corrupted_files:
                    try:
                        os.remove(path)
                        print(f"Deleted: {path}")
                    except Exception as e:
                        print(f"Failed to delete {path}: {e}")
                print("All selected corrupted files have been deleted.")
            else:
                print("No files were deleted.")
