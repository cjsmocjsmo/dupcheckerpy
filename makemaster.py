import os
import sqlite3
import shutil

# Define the directories and database file
master_pics_dir = '/media/piir/PiTB/MASTERPICS/'
db_file = './imagehash.db'

class MakeMasterPics:
    def __init__(self, master_pics_dir, db_file):
        self.master_pics_dir = master_pics_dir
        self.db_file = db_file

    def create_master_pics_dir(self):
        """Create the MasterPics directory if it doesn't exist."""
        if not os.path.exists(self.master_pics_dir):
            try:
                os.makedirs(self.master_pics_dir)
                print(f"Directory '{self.master_pics_dir}' created successfully.")
            except OSError as e:
                print(f"Error creating directory '{self.master_pics_dir}': {e}")
                exit()
        else:
            print(f"Directory '{self.master_pics_dir}' already exists.")
        return self.master_pics_dir

    def create_piclist(self):
        """Create a list of image paths from the database."""
        piclist = []
        try:
            conn = sqlite3.connect(self.db_file)
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


    def copy_images(self, piclist):
        """Copy images from the piclist to the MasterPics directory."""
        for data in piclist:
            try:
                src_path = data["path"]  # Extract the source path from the dictionary
                if os.path.isfile(src_path):
                    dpath = os.path.join(self.master_pics_dir, f"{data['phash']}.jpg")
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

    def create_movlist(self):
        """Create a list of video paths from the database."""
        
        movlist = []

        try:
            conn = sqlite3.connect(self.db_file)
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

    def copy_movies(self, movlist):
        """Copy videos from the movlist to the MasterPics directory."""

        for data in movlist:
            try:
                src_path = data["path"]  # Extract the source path from the dictionary
                if os.path.isfile(src_path):
                    dpath = os.path.join(self.master_pics_dir, f"{data['mhash']}.mp4")
                    shutil.copy2(src_path, dpath)  # Use the extracted path
                    print(f"Copied '{os.path.basename(src_path)}' to\t\n '{dpath}'")
                else:
                    print(f"Warning: Source path '{src_path}' is not a file. Skipping.")
            except FileNotFoundError:
                print(f"Error: Source file '{src_path}' not found.")
            except OSError as e:
                print(f"Error copying '{src_path}': {e}")
        print("Video copying process completed.")
    

    def main(self):
        _ = self.create_master_pics_dir(self.master_pics_dir)
        print("MasterPics directory is ready.")
        piclist = self.create_piclist()
        if piclist:
            self.copy_images(piclist)
        else:
            print("No images found in the database to copy.")
        movlist = self.create_movlist(self.db_file)
        if movlist:
            self.copy_movies(movlist, self.master_pics_dir)
        else:
            print("No videos found in the database to copy.")

if __name__ == '__main__':
    master_pics_dir = ""
    db_file = "./imagehash.db"
    mpd = MakeMasterPics(master_pics_dir, db_file)
    mpd.main()