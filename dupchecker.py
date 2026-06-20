import os
import sqlite3
import hashlib
import imagehash
from PIL import Image
from concurrent.futures import ProcessPoolExecutor

IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
VIDEO_EXTENSIONS = {'.mp4'}
DEFAULT_BATCH_SIZE = 500

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
        with Image.open(image_path) as img:
            processed = img.convert('L').resize((256, 256))
            return str(imagehash.phash(processed))
    except Exception as e:
        print(f"Error calculating pHash for {image_path}: {e}")
        return None

def process_single_image(img_path):
    phash = calculate_phash(img_path)
    if phash:
        return ("hashes", os.path.basename(img_path), img_path, phash)
    return None

def process_single_video(video_path):
    mhash = calculate_mhash(video_path)
    if mhash:
        return ("video_hashes", os.path.basename(video_path), video_path, mhash)
    return None

def process_single_file(file_path):
    extension = os.path.splitext(file_path)[1].lower()

    if extension in IMAGE_EXTENSIONS:
        try:
            return process_single_image(file_path)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None

    if extension in VIDEO_EXTENSIONS:
        try:
            return process_single_video(file_path)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None

    return None

def iter_media_files(folder):
    for root, _, files in os.walk(folder):
        for file_name in files:
            extension = os.path.splitext(file_name)[1].lower()
            if extension in IMAGE_EXTENSIONS or extension in VIDEO_EXTENSIONS:
                yield os.path.join(root, file_name)

def initialize_database(db_name):
    conn = sqlite3.connect(db_name)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    conn.execute('PRAGMA busy_timeout=5000')
    cursor = conn.cursor()

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
    return conn

def flush_batches(conn, batches):
    rows_to_write = 0
    with conn:
        for table_name, rows in batches.items():
            if not rows:
                continue
            if table_name == 'hashes':
                conn.executemany(
                    'INSERT OR IGNORE INTO hashes (filename, path, phash) VALUES (?, ?, ?)',
                    rows,
                )
            else:
                conn.executemany(
                    'INSERT OR IGNORE INTO video_hashes (filename, path, mhash) VALUES (?, ?, ?)',
                    rows,
                )
            rows_to_write += len(rows)
            rows.clear()
    return rows_to_write

def process_images_and_store_hashes(folder, db_name='imagehash.db', max_workers=2, batch_size=DEFAULT_BATCH_SIZE, chunksize=32):
    conn = None
    try:
        conn = initialize_database(db_name)
        batches = {
            'hashes': [],
            'video_hashes': [],
        }

        scanned_files = 0
        staged_rows = 0

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            for result in executor.map(process_single_file, iter_media_files(folder), chunksize=chunksize):
                scanned_files += 1
                if result is None:
                    continue

                table_name, filename, path, hash_value = result
                batches[table_name].append((filename, path, hash_value))
                staged_rows += 1

                if staged_rows >= batch_size:
                    written_rows = flush_batches(conn, batches)
                    print(f"Scanned {scanned_files} files, staged {written_rows} rows")
                    staged_rows = 0

        if any(batches.values()):
            written_rows = flush_batches(conn, batches)
            print(f"Flushed final {written_rows} rows")

        print(f"Processed {scanned_files} media files and stored hashes in {db_name}")
    except Exception as e:
        print(f"Error processing folder {folder}: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass

def dupchecker_main(IMAGE_FOLDER):
    process_images_and_store_hashes(IMAGE_FOLDER)

if __name__ == '__main__':
    image_folder = '/home/piir/Pictures/'  # Replace with the path to your image folder
    process_images_and_store_hashes(image_folder)