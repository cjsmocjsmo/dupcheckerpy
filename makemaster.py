import os
import sqlite3
import shutil

# Define the directories and database file
master_pics_dir = '/home/whitepi/MasterPics'
db_file = '/home/whitepi/dupcheckerpy/dupcheckerpy/image.db'

# Create the MasterPics directory if it doesn't exist
if not os.path.exists(master_pics_dir):
    try:
        os.makedirs(master_pics_dir)
        print(f"Directory '{master_pics_dir}' created successfully.")
    except OSError as e:
        print(f"Error creating directory '{master_pics_dir}': {e}")
        exit()
else:
    print(f"Directory '{master_pics_dir}' already exists.")

# Connect to the SQLite database and fetch the paths
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

# Loop through the piclist and copy the images
print("Copying images to MasterPics...")
for data in piclist:
    try:
        src_path = data["path"]  # Extract the source path from the dictionary
        if os.path.isfile(src_path):
            dpath = os.path.join(master_pics_dir, f"{data['phash']}.jpg")
            shutil.copy2(src_path, dpath)  # Use the extracted path
            print(f"Copied '{os.path.basename(src_path)}' to '{dpath}'")
        else:
            print(f"Warning: Source path '{src_path}' is not a file. Skipping.")
    except FileNotFoundError:
        print(f"Error: Source file '{src_path}' not found.")
    except OSError as e:
        print(f"Error copying '{src_path}': {e}")

print("Image copying process completed.")