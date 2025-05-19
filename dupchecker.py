import os
import sqlite3
from PIL import Image
import imagehash
import cv2  # Import cv2 here as well, in case it's not already in the environment
from walkdir import filtered_walk
from pprint import pprint

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
            phash TEXT UNIQUE
        )
    ''')
    conn.commit()

    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    filelist = []
    extlist = []
    # for img_path in filtered_walk(folder, included_files=image_extensions):
    for dir, _, files in os.walk(folder):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            extlist.append(ext)
            if file.lower().endswith(tuple(image_extensions)):
                img_path = os.path.join(dir, file)
                filelist.append(img_path)

                # Check if the image is valid
                try:
                    img = Image.open(img_path)
                    img.verify()  # Verify that it is an image
                except Exception as e:
                    print(f"Invalid image {img_path}: {e}")
                    continue
                print(img_path)
    
    

                # Process the image
                # print(f"Processing {img_path}...")
                # Uncomment the following lines to calculate and store the hash
                phash = calculate_phash(img_path)
                if phash:
                    try:
                        cursor.execute("INSERT OR IGNORE INTO image_hashes (filename, path, phash) VALUES (?, ?, ?)", (file, img_path, phash))
                    except sqlite3.IntegrityError:
                        print(f"Skipping {file} as it's already in the database.")
            # filename = os.path.join(dir, file)
            
    pprint(list(set(extlist)))
    print(f"Processed images and stored hashes in {db_name}")

if __name__ == '__main__':
    image_folder = '/home/whitepi/Pictures'  # Replace with the path to your image folder
    process_images_and_store_hashes(image_folder)
