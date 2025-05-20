import os
import sqlite3
import shutil

# Define the directories and database file
master_pics_dir = '/home/whitepi/MasterPics'
db_file = '/home/whitepi/dupcheckerpy/dupcheckerpi/image.db'

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
    cursor.execute("SELECT path FROM hashes")
    rows = cursor.fetchall()
    for row in rows:
        piclist.append(row[0])
    conn.close()
    print(f"Successfully retrieved {len(piclist)} image paths from the database.")
except sqlite3.Error as e:
    print(f"Error connecting to or querying the database: {e}")
    exit()

# Loop through the piclist and copy the images
print("Copying images to MasterPics...")
for source_path in piclist:
    try:
        if os.path.isfile(source_path):
            destination_path = os.path.join(master_pics_dir, os.path.basename(source_path))
            shutil.copy2(source_path, destination_path)  # copy2 preserves metadata
            print(f"Copied '{os.path.basename(source_path)}'")
        else:
            print(f"Warning: Source path '{source_path}' is not a file. Skipping.")
    except FileNotFoundError:
        print(f"Error: Source file '{source_path}' not found.")
    except OSError as e:
        print(f"Error copying '{source_path}': {e}")

print("Image copying process completed.")