import os
import sqlite3
from PIL import Image
import imagehash
import cv2  # Import cv2 here as well, in case it's not already in the environment
from walkdir import filtered_walk
from pprint import pprint
import tempfile
from concurrent.futures import ProcessPoolExecutor
from functools import partial

# def calculate_phash(image_path):
#     try:
#         img = Image.open(image_path).convert('L')
#         hash_value = imagehash.phash(img)
#         return str(hash_value)
#     except Exception as e:
#         print(f"Error calculating pHash for {image_path}: {e}")
#         return None

# def process_images_and_store_hashes(folder, db_name='image.db'):
#     conn = sqlite3.connect(db_name)
#     cursor = conn.cursor()

#     # Create table if it doesn't exist
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS hashes (
#             image_id INTEGER PRIMARY KEY AUTOINCREMENT,
#             filename TEXT UNIQUE,
#             path TEXT UNIQUE,
#             phash TEXT UNIQUE
#         )
#     ''')
#     conn.commit()

#     image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    
#     extlist = []
#     count = 0
#     # for img_path in filtered_walk(folder, included_files=image_extensions):
#     for dir, _, files in os.walk(folder):
#         for file in files:
#             ext = os.path.splitext(file)[1].lower()
#             extlist.append(ext)
#             count += 1
#             if file.lower().endswith(tuple(image_extensions)):
#                 img_path = os.path.join(dir, file)
#                 # print(f"Processing file: {img_path}")
#                 try:
#                     img = Image.open(img_path).convert('L')
#                     img = img.resize((256, 256))
#                     with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
#                         temp_path = temp_file.name
#                         img.save(temp_path)
#                         # print(f"Temporary file saved at {temp_path}")
#                         phash = calculate_phash(temp_path)
#                     os.remove(temp_path)
#                     # print(f"Calculated pHash for {img_path}: {phash}")
#                     if phash:
#                         try:
#                             cursor.execute("INSERT INTO hashes (filename, path, phash) VALUES (?, ?, ?)", (file, img_path, phash))
#                             print(phash)
#                         except sqlite3.IntegrityError:
#                             print(f"Skipping {phash} as it's already in the database.")
#                         conn.commit()
#                     else:
#                         print(f"Hash for {file} is None, skipping database insertion.")
#                 except Exception as e:
#                     print(f"Error processing {img_path}: {e}")
#                     continue
            
#     pprint(list(set(extlist)))
#     print(f"Processed {count} images and stored hashes in {db_name}")

# if __name__ == '__main__':
#     image_folder = '/home/whitepi/Pictures'  # Replace with the path to your image folder
#     process_images_and_store_hashes(image_folder)


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
    conn.commit()
    conn.close()

    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    img_paths = []

    # Collect all image paths
    count = 0
    for dir, _, files in os.walk(folder):
        for file in files:
            count += 1
            if file.lower().endswith(tuple(image_extensions)):
                img_paths.append(os.path.join(dir, file))

    # Use ProcessPoolExecutor to process images in parallel
    with ProcessPoolExecutor() as executor:
        process_func = partial(process_single_image, db_name=db_name)
        executor.map(process_func, img_paths)

    print(f"Processed {count} images and stored hashes in {db_name}")

if __name__ == '__main__':
    image_folder = '/home/whitepi/Pictures/Pic6'  # Replace with the path to your image folder
    process_images_and_store_hashes(image_folder)