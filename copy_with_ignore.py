import os
import shutil
import logging
from datetime import datetime

# ==== CONFIGURATION ====
SOURCE_DIR = r"Z:\Meech's stuff\UM-Dearborn-All Projects and Class Files\WINTER 2021 SEMESTER CLASS FILES\CIS 200 - RETAKE - WINTER 2021 -JIE SHEN"
DEST_DIR = r"C:\Users\demet\OneDrive\Documents\GitHub\github_repo_importer\projects\test"

IGNORE_FOLDERS = [".vs", ".git", "__pycache__"]
IGNORE_FILES = ["Thumbs.db", ".DS_Store"]

# ==== SETUP LOGGING ====
script_dir = os.path.dirname(os.path.abspath(__file__))
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file = os.path.join(script_dir, f"copy_log_{timestamp}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# ==== PRE-SCAN TO COUNT FILES & SIZE ====
def get_copy_plan(src_dir, ignore_folders, ignore_files):
    total_files = 0
    total_size = 0
    plan = []

    for root, dirs, files in os.walk(src_dir):
        # Remove ignored folders
        for d in list(dirs):
            if d in ignore_folders:
                logging.info(f"IGNORED FOLDER: {os.path.join(root, d)}")
                dirs.remove(d)

        for file in files:
            if file in ignore_files:
                logging.info(f"IGNORED FILE: {os.path.join(root, file)}")
                continue

            src_path = os.path.join(root, file)
            try:
                size = os.path.getsize(src_path)
                plan.append((src_path, size))
                total_files += 1
                total_size += size
            except FileNotFoundError:
                logging.warning(f"File not found during scan: {src_path}")

    return plan, total_files, total_size

# ==== COPY LOGIC ====
def copy_files_with_progress(plan, src_dir, dest_dir):
    copied_files = 0
    copied_bytes = 0

    for src_file, size in plan:
        rel_path = os.path.relpath(src_file, src_dir)
        dest_file = os.path.join(dest_dir, rel_path)
        dest_folder = os.path.dirname(dest_file)

        os.makedirs(dest_folder, exist_ok=True)

        try:
            shutil.copy2(src_file, dest_file)
            copied_files += 1
            copied_bytes += size
            logging.info(f"COPIED: {rel_path} ({size / 1024:.1f} KB)")
        except Exception as e:
            logging.error(f"ERROR copying {src_file}: {e}")

    return copied_files, copied_bytes

# ==== MAIN ====
if __name__ == "__main__":
    logging.info("Scanning source directory...")
    copy_plan, total_files, total_size = get_copy_plan(SOURCE_DIR, IGNORE_FOLDERS, IGNORE_FILES)

    logging.info("\nSUMMARY:")
    logging.info(f"  Files to copy: {total_files}")
    logging.info(f"  Total size: {total_size / (1024*1024):.2f} MB\n")

    logging.info("Starting copy...\n")
    copied_files, copied_bytes = copy_files_with_progress(copy_plan, SOURCE_DIR, DEST_DIR)

    logging.info("\nDONE:")
    logging.info(f"  Files copied: {copied_files}/{total_files}")
    logging.info(f"  Size copied: {copied_bytes / (1024*1024):.2f} MB / {total_size / (1024*1024):.2f} MB")
    logging.info(f"  Log saved to: {log_file}")
