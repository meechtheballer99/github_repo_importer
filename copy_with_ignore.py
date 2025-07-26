import os
import shutil
import logging
from datetime import datetime
import fnmatch
import csv
import time

# ==== CONFIGURATION ====
SOURCE_DIR = r"Z:\Meech's stuff\UM-Dearborn-All Projects and Class Files"
DEST_DIR = r"C:\Users\demet\OneDrive\Documents\GitHub\github_repo_importer\temp_files_from_server"

IGNORE_FOLDER_PATTERNS = [".vs", "__pycache__", ".git", "Debug", "bin"]
IGNORE_FILE_PATTERNS = ["*.log", "Thumbs.db", ".DS_Store", "~$*", "*.vcxproj*", "*.ova", "*.iso", "*.ovf"]

# ==== MATCHING HELPERS ====
def matches_any_glob(name, pattern_list):
    return any(fnmatch.fnmatch(name, pattern) for pattern in pattern_list)

# ==== SETUP LOGGING ====
script_dir = os.path.dirname(os.path.abspath(__file__))
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file = os.path.join(script_dir, f"copy_log_{timestamp}.log")
skipped_files = []  # List of (path, reason)

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
        for d in list(dirs):
            if matches_any_glob(d, IGNORE_FOLDER_PATTERNS):
                full_path = os.path.join(root, d)
                skipped_files.append((full_path, "Ignored folder pattern"))
                logging.info(f"IGNORED FOLDER: {full_path}")
                dirs.remove(d)

        for file in files:
            if matches_any_glob(file, IGNORE_FILE_PATTERNS):
                full_path = os.path.join(root, file)
                skipped_files.append((full_path, "Ignored file pattern"))
                logging.info(f"IGNORED FILE: {full_path}")
                continue

            raw_path = os.path.join(root, file)
            src_path = os.path.normpath(raw_path)
            win_path = f"\\\\?\\{src_path}"

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    if not os.path.exists(win_path):
                        logging.warning(f"File does not exist: {win_path}")
                        skipped_files.append((win_path, "File does not exist"))
                        break

                    size = os.path.getsize(win_path)
                    plan.append((win_path, size))
                    total_files += 1
                    total_size += size
                    break
                except FileNotFoundError as e:
                    if attempt < max_retries - 1:
                        time.sleep(0.2)
                        continue
                    logging.warning(f"File not found during scan after retries: {win_path} | {e}")
                    skipped_files.append((win_path, f"FileNotFoundError: {e}"))
                except Exception as e:
                    logging.error(f"Unexpected error accessing file: {win_path} | {e}")
                    skipped_files.append((win_path, f"Access error: {e}"))
                    break

    return plan, total_files, total_size

# ==== COPY LOGIC ====
def copy_files_with_progress(plan, src_dir, dest_dir):
    copied_files = 0
    copied_bytes = 0

    for src_file, size in plan:
        src_file_clean = src_file[4:] if src_file.startswith('\\\\?\\') else src_file
        rel_path = os.path.relpath(src_file_clean, src_dir)
        dest_file = os.path.join(dest_dir, rel_path)

        long_dest_file = f"\\\\?\\{os.path.normpath(dest_file)}"
        long_dest_folder = os.path.dirname(long_dest_file)

        try:
            os.makedirs(long_dest_folder, exist_ok=True)
            shutil.copy2(src_file, long_dest_file)
            copied_files += 1
            copied_bytes += size
            logging.info(f"COPIED: {rel_path} ({size / 1024:.1f} KB)")
        except Exception as e:
            logging.error(f"ERROR copying {src_file} -> {long_dest_file}: {e}")
            skipped_files.append((src_file, f"Copy error: {e}"))

    return copied_files, copied_bytes

# ==== WRITE SKIPPED CSV ====
def write_skipped_csv(skipped_entries, csv_path):
    with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["File Path", "Reason"])
        for entry in skipped_entries:
            writer.writerow(entry)

# ==== MAIN ====
if __name__ == "__main__":
    logging.info("Scanning source directory...")
    copy_plan, total_files, total_size = get_copy_plan(SOURCE_DIR, IGNORE_FOLDER_PATTERNS, IGNORE_FILE_PATTERNS)

    logging.info("\nSUMMARY:")
    logging.info(f"  Files to copy: {total_files}")
    logging.info(f"  Total size: {total_size / (1024*1024):.2f} MB\n")

    logging.info("Starting copy...\n")
    copied_files, copied_bytes = copy_files_with_progress(copy_plan, SOURCE_DIR, DEST_DIR)

    logging.info("\nDONE:")
    logging.info(f"  Files copied: {copied_files}/{total_files}")
    logging.info(f"  Size copied: {copied_bytes / (1024*1024):.2f} MB / {total_size / (1024*1024):.2f} MB")
    logging.info(f"  Log saved to: {log_file}")

    skipped_csv_file = os.path.join(script_dir, f"skipped_files_{timestamp}.csv")
    write_skipped_csv(skipped_files, skipped_csv_file)
    logging.info(f"  Skipped files CSV saved to: {skipped_csv_file}")
