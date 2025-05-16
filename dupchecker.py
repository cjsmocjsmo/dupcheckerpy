import os
import sqlite3
from PIL import Image
import imagehash
import cv2  # Import cv2 here as well, in case it's not already in the environment
from walkdir import filtered_walk

def calculate_phash(image_path):
    try:
        img = Image.open(image_path).convert('L')
        hash_value = imagehash.phash(img)
        return str(hash_value)
    except Exception as e:
        print(f"Error calculating pHash for {image_path}: {e}")
        return None

def process_images_and_store_hashes(folder, db_name='image_hashes.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS image_hashes (
            image_id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE,
            path TEXT UNIQUE,
            phash TEXT
        )
    ''')
    conn.commit()

    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp']
    for img_path in filtered_walk(folder, included_files=image_extensions):
        print(img_path)
        filename = os.path.basename(img_path)
        
    #     try:
    #         phash = calculate_phash(img_path)
    #         if phash:
    #             try:
    #                 cursor.execute("INSERT OR IGNORE INTO image_hashes (filename, path, phash) VALUES (?, ?, ?)", (filename, img_path, phash))
    #             except sqlite3.IntegrityError:
    #                 print(f"Skipping {filename} as it's already in the database.")
    #     except Exception as e:
    #         print(f"Error processing {filename}: {e}")

    # conn.commit()
    # conn.close()
    print(f"Processed images and stored hashes in {db_name}")

if __name__ == '__main__':
    image_folder = '/home/whitepi/Pictures/Pic1'  # Replace with the path to your image folder
    process_images_and_store_hashes(image_folder)
