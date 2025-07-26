import os
import hashlib
import logging
from pathlib import Path
from datetime import datetime
import sys
# --- CONFIGURATION ---
dir1 = r"C:\Users\demet\OneDrive\Documents\GitHub\github_repo_importer\temp_files_from_server\3-30-23_BACKUP_WINTER 23 SEMESTER-FILES"
dir2 = r"C:\Users\demet\OneDrive\Documents\GitHub\github_repo_importer\temp_files_from_server\WINTER 2023 SEMESTER CLASS FILES"
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
script_dir = Path(__file__).parent if '__file__' in globals() else Path(sys.argv[0]).resolve().parent
log_path = script_dir / f"compare_directories_{timestamp}.log"


# --- LOGGING SETUP ---
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

# --- UTILS ---
def hash_file(path, algo="sha256"):
    logging.info(f"🔄 Hashing file: {path}")
    h = hashlib.new(algo)
    try:
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        digest = h.hexdigest()
        logging.info(f"   ✔ Hash complete: {digest}")
        return digest
    except Exception as e:
        logging.warning(f"   ❌ Failed to hash file: {path} — {e}")
        return f"ERROR: {e}"

def collect_files(base_dir):
    logging.info(f"\n📁 Scanning directory: {base_dir}")
    file_map = {}
    base_path = Path(base_dir).resolve()
    count = 0
    for root, _, files in os.walk(base_path):
        for name in files:
            full_path = Path(root) / name
            rel_path = full_path.relative_to(base_path)
            logging.info(f"→ Processing file: {rel_path}")
            file_map[str(rel_path)] = {
                "full": str(full_path),
                "hash": hash_file(full_path)
            }
            count += 1
    logging.info(f"✔️ Finished scanning {base_dir} — {count} files found.\n")
    return file_map

# --- MAIN COMPARISON LOGIC ---
def compare_directories(dir1, dir2):
    logging.info("=====================================")
    logging.info("🔍 DIRECTORY COMPARISON STARTED")
    logging.info("=====================================")
    logging.info(f"📦 BACKUP  DIRECTORY: {dir1}")
    logging.info(f"🗂️  CURRENT DIRECTORY: {dir2}\n")

    files1 = collect_files(dir1)
    files2 = collect_files(dir2)

    logging.info("📊 Analyzing file differences...\n")

    only_in_dir1 = sorted(set(files1) - set(files2))
    only_in_dir2 = sorted(set(files2) - set(files1))
    common_files = set(files1) & set(files2)

    diff_content = sorted([
        f for f in common_files
        if files1[f]['hash'] != files2[f]['hash']
    ])

    # Report differences
    logging.info(f"\n📁 FILES ONLY IN BACKUP ({len(only_in_dir1)}):")
    for f in only_in_dir1:
        logging.info(f"🔹 {f}  ←  {files1[f]['full']}")

    logging.info(f"\n📁 FILES ONLY IN CURRENT ({len(only_in_dir2)}):")
    for f in only_in_dir2:
        logging.info(f"🔸 {f}  ←  {files2[f]['full']}")

    logging.info(f"\n🧬 FILES WITH DIFFERENT CONTENT ({len(diff_content)}):")
    for f in diff_content:
        logging.info(f"⚠️  {f}")
        logging.info(f"   BACKUP :  {files1[f]['full']}")
        logging.info(f"   CURRENT:  {files2[f]['full']}\n")

    # Summary
    logging.info("\n📋 SUMMARY:")
    logging.info(f"📦 Total files in BACKUP : {len(files1)}")
    logging.info(f"🗂️  Total files in CURRENT: {len(files2)}")
    logging.info(f"🔹 Only in BACKUP        : {len(only_in_dir1)}")
    logging.info(f"🔸 Only in CURRENT       : {len(only_in_dir2)}")
    logging.info(f"⚠️  Different content     : {len(diff_content)}")

    logging.info(f"\n✅ Comparison complete. Log saved to:\n{log_path}")
    logging.info("=====================================\n")

# --- RUN ---
if __name__ == "__main__":
    compare_directories(dir1, dir2)
