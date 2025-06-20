import os
import sqlite3
import hashlib
import imagehash
import tempfile
from PIL import Image
from functools import partial
from concurrent.futures import ProcessPoolExecutor

def calculate_mhash(file_path, buffer_size=65536):
    """Generates an MD5 hash of the file content."""
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as file:
            while True:
                chunk = file.read(buffer_size)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except FileNotFoundError:
        return None

def calculate_phash(image_path):
    try:
        img = Image.open(image_path).convert('L')
        hash_value = imagehash.phash(img)
        return str(hash_value)
    except Exception as e:
        print(f"Error calculating pHash for {image_path}: {e}")
        return None

def process_single_image(img_path, db_name):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        img = Image.open(img_path).convert('L')
        img = img.resize((256, 256))
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_path = temp_file.name
            img.save(temp_path)
            phash = calculate_phash(temp_path)
        os.remove(temp_path)

        if phash:
            try:
                cursor.execute("INSERT INTO hashes (filename, path, phash) VALUES (?, ?, ?)", 
                               (os.path.basename(img_path), img_path, phash))
                conn.commit()
                print(f"Inserted {img_path} with pHash {phash}")
            except sqlite3.IntegrityError:
                print(f"Skipping {img_path} as it's already in the database.")
        else:
            print(f"Hash for {img_path} is None, skipping database insertion.")
    except Exception as e:
        print(f"Error processing {img_path}: {e}")
    finally:
        conn.close()

def process_single_video(video_path, db_name):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        mhash = calculate_mhash(video_path)
        
        if mhash:
            try:
                cursor.execute("INSERT INTO video_hashes (filename, path, mhash) VALUES (?, ?, ?)", 
                               (os.path.basename(video_path), video_path, mhash))
                conn.commit()
                print(f"Inserted {video_path} with pHash {mhash}")
            except sqlite3.IntegrityError:
                print(f"Skipping {video_path} as it's already in the database.")
        else:
            print(f"Hash for {video_path} is None, skipping database insertion.")
    except Exception as e:
        print(f"Error processing {video_path}: {e}")
    finally:
        conn.close()

def process_images_and_store_hashes(folder, db_name='image.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hashes (
            image_id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE,
            path TEXT UNIQUE,
            phash TEXT UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS video_hashes (
            video_id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE,
            path TEXT UNIQUE,
            mhash TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    img_paths = []
    mov_paths = []

    # Collect all image paths
    count = 0
    for dir, _, files in os.walk(folder):
        for file in files:
            count += 1
            if file.lower().endswith(tuple(image_extensions)):
                img_paths.append(os.path.join(dir, file))
            elif file.lower().endswith('.mp4'):
                mov_paths.append(os.path.join(dir, file))

    # Use ProcessPoolExecutor to process images in parallel
    with ProcessPoolExecutor() as executor:
        process_func = partial(process_single_image, db_name=db_name)
        executor.map(process_func, img_paths)

    with ProcessPoolExecutor() as executor:
        process_func = partial(process_single_video, db_name=db_name)
        executor.map(process_func, mov_paths)

    print(f"Processed {count} images and stored hashes in {db_name}")

def dupchecker_main(IMAGE_FOLDER):
    process_images_and_store_hashes(IMAGE_FOLDER)

import os
import sqlite3
import shutil

# Define the directories and database file
# master_pics_dir = '/home/whitepi/MasterPics'
# db_file = '/home/whitepi/dupcheckerpy/dupcheckerpy/image.db'

def create_master_pics_dir(master_pics_dir):
    """Create the MasterPics directory if it doesn't exist."""
    if not os.path.exists(master_pics_dir):
        try:
            os.makedirs(master_pics_dir)
            print(f"Directory '{master_pics_dir}' created successfully.")
        except OSError as e:
            print(f"Error creating directory '{master_pics_dir}': {e}")
            exit()
    else:
        print(f"Directory '{master_pics_dir}' already exists.")

def create_piclist(db_file):
    """Create a list of image paths from the database."""
    piclist = []
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT path, phash FROM hashes")
        rows = cursor.fetchall()
        for row in rows:
            data = {
                "path": row[0],
                "phash": row[1]
            }
            piclist.append(data)
        conn.close()
        print(f"Successfully retrieved {len(piclist)} image paths from the database.")
    except sqlite3.Error as e:
        print(f"Error connecting to or querying the database: {e}")
        exit(1)
    return piclist


def copy_images(piclist, master_pics_dir):
    """Copy images from the piclist to the MasterPics directory."""
    for data in piclist:
        try:
            src_path = data["path"]  # Extract the source path from the dictionary
            if os.path.isfile(src_path):
                dpath = os.path.join(master_pics_dir, f"{data['phash']}.jpg")
                shutil.copy2(src_path, dpath)  # Use the extracted path
                print(f"Copied '{os.path.basename(src_path)}' to\n\t '{dpath}'")
            else:
                print(f"Warning: Source path '{src_path}' is not a file. Skipping.")
        except FileNotFoundError:
            print(f"Error: Source file '{src_path}' not found.")
        except OSError as e:
            print(f"Error copying '{src_path}': {e}")
# Loop through the piclist and copy the images
    print("Image copying process completed.")

def create_movlist(db_file):
    """Create a list of video paths from the database."""
    
    movlist = []

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT path, mhash FROM video_hashes")
        rows = cursor.fetchall()
        for row in rows:
            data = {
                "path": row[0],
                "mhash": row[1]
            }
            movlist.append(data)
        conn.close()
        print(f"Successfully retrieved {len(movlist)} video paths from the database.")
    except sqlite3.Error as e:
        print(f"Error connecting to or querying the database: {e}")
        exit(1)
    try:
        conn.close()
        print("Database connection closed.")
    except sqlite3.Error as e:
        print(f"Error closing the database connection: {e}")
        exit(1)
    return movlist

def copy_movies(movlist, master_pics_dir):
    """Copy videos from the movlist to the MasterPics directory."""

    for data in movlist:
        try:
            src_path = data["path"]  # Extract the source path from the dictionary
            if os.path.isfile(src_path):
                dpath = os.path.join(master_pics_dir, f"{data['mhash']}.mp4")
                shutil.copy2(src_path, dpath)  # Use the extracted path
                print(f"Copied '{os.path.basename(src_path)}' to\t\n '{dpath}'")
            else:
                print(f"Warning: Source path '{src_path}' is not a file. Skipping.")
        except FileNotFoundError:
            print(f"Error: Source file '{src_path}' not found.")
        except OSError as e:
            print(f"Error copying '{src_path}': {e}")
    print("Video copying process completed.")
    

def main(pics_dir):
    master_pics_dir = create_master_pics_dir(pics_dir)
    print("MasterPics directory is ready.")
    piclist = create_piclist()
    if piclist:
        copy_images(piclist, master_pics_dir)
    else:
        print("No images found in the database to copy.")
    movlist = create_movlist()
    if movlist:
        copy_movies(movlist, master_pics_dir)
    else:
        print("No videos found in the database to copy.")

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

if __name__ == '__main__':

    SOURCE_FOLDER = "/home/whitepi/MasterPics"
    DESTINATION_BASE_FOLDER = "/home/whitepi/MasterPicsDeduped"
    DB_FILE = '/home/whitepi/dupcheckerpy/dupcheckerpy/image.db'
    MAX_FOLDER_SIZE_GB = 1.0

    dupchecker_main(SOURCE_FOLDER)
    create_master_pics_dir(SOURCE_FOLDER)
    piclist = create_piclist(DB_FILE)
    copy_images(piclist, SOURCE_FOLDER)
    movlist = create_movlist(DB_FILE)
    copy_movies(movlist, SOURCE_FOLDER)
    split_main(SOURCE_FOLDER, DESTINATION_BASE_FOLDER, MAX_FOLDER_SIZE_GB)
    print("All operations completed successfully.")