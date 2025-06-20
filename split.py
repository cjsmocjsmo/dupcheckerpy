import os
import shutil
import math

def organize_images_by_size(source_folder, destination_base_folder, max_folder_size_gb):
    """
    Organizes images from a source folder into subfolders,
    with each subfolder containing a maximum specified size of images.

    Args:
        source_folder (str): The path to the folder containing all images.
        destination_base_folder (str): The base path where new subfolders will be created.
        max_folder_size_gb (float): The maximum size (in GB) for each subfolder.
    """

    # Convert max_folder_size_gb to bytes for calculations
    max_folder_size_bytes = max_folder_size_gb * 1024 * 1024 * 1024

    # Ensure the source folder exists
    if not os.path.isdir(source_folder):
        print(f"Error: Source folder '{source_folder}' does not exist.")
        return

    # Create the base destination folder if it doesn't exist
    os.makedirs(destination_base_folder, exist_ok=True)

    # Initialize variables for tracking folder size and count
    current_subfolder_size_bytes = 0
    subfolder_count = 0
    current_subfolder_path = ""

    # Get a list of all files in the source folder
    # We'll sort them by name to ensure consistent behavior
    all_files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]
    all_files.sort() # Sort to process files in a consistent order

    print(f"Starting to organize images from '{source_folder}'...")
    print(f"Each subfolder will contain a maximum of {max_folder_size_gb} GB of images.")

    # Iterate through each file in the source folder
    for i, filename in enumerate(all_files):
        file_path = os.path.join(source_folder, filename)

        try:
            file_size = os.path.getsize(file_path)
        except OSError as e:
            print(f"Warning: Could not get size of '{filename}'. Skipping. Error: {e}")
            continue

        # Check if adding this file would exceed the current subfolder's size limit
        # Or if it's the very first file, create the first subfolder
        if current_subfolder_size_bytes + file_size > max_folder_size_bytes or current_subfolder_path == "":
            subfolder_count += 1
            current_subfolder_name = f"images_part_{subfolder_count:03d}" # e.g., images_part_001
            current_subfolder_path = os.path.join(destination_base_folder, current_subfolder_name)
            os.makedirs(current_subfolder_path, exist_ok=True) # Create the new subfolder
            current_subfolder_size_bytes = 0 # Reset size for the new folder
            print(f"\n--- Creating new subfolder: '{current_subfolder_name}' ---")

        # Define the destination path for the current file
        destination_file_path = os.path.join(current_subfolder_path, filename)

        try:
            # Move the file to the current subfolder
            shutil.copy2(file_path, destination_file_path)
            current_subfolder_size_bytes += file_size
            print(f"Copied '{filename}' to\n\t'{current_subfolder_name}'\n\tCurrent size: {current_subfolder_size_bytes / (1024 * 1024 * 1024):.2f} GB")
        except shutil.Error as e:
            print(f"Error moving '{filename}' to '{current_subfolder_name}'. Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred with '{filename}': {e}")

    print(f"\nImage organization complete. Total subfolders created: {subfolder_count}")

def split_main(SOURCE_FOLDER, DESTINATION_BASE_FOLDER, MAX_FOLDER_SIZE_GB):
    organize_images_by_size(SOURCE_FOLDER, DESTINATION_BASE_FOLDER, MAX_FOLDER_SIZE_GB)


# # --- Configuration ---
# # IMPORTANT: Replace 'path/to/your/20000_images_folder' with the actual path to your images.
# SOURCE_FOLDER = "/home/whitepi/MasterPics"

# # IMPORTANT: Replace 'path/to/your/output_folders' with where you want the new subfolders to be created.
# DESTINATION_BASE_FOLDER = "/home/whitepi/MasterPicsDeduped"

# # Maximum size per subfolder in Gigabytes
# MAX_FOLDER_SIZE_GB = 1.85

# --- Run the script ---
# if __name__ == "__main__":
#     # Example usage:
#     # First, create some dummy files for testing if you don't have 20,000 images
#     # This part is for demonstration and can be removed or commented out for actual use
#     # print("Creating dummy files for demonstration...")
#     # dummy_source = "dummy_images_source"
#     # os.makedirs(dummy_source, exist_ok=True)
#     # for i in range(100): # Create 100 dummy files, each ~20MB
#     #     with open(os.path.join(dummy_source, f"image_{i:04d}.jpg"), "wb") as f:
#     #         f.write(os.urandom(20 * 1024 * 1024)) # 20MB random data
#     # print("Dummy files created.")
#     #
#     # # Then run the organization
#     # organize_images_by_size(dummy_source, "organized_images_output", 0.5) # Example: 0.5 GB per folder

#     # For your actual use case, uncomment and adjust the paths below:
#     organize_images_by_size(SOURCE_FOLDER, DESTINATION_BASE_FOLDER, MAX_FOLDER_SIZE_GB)
