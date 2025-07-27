import os
import pathlib
import logging
import sys
from datetime import datetime
import math

# === OPTIONAL HARDCODED TARGET DIRECTORY === 
# (if command line argument of file path is passed in, TARGET_DIR will be overwritten to use that value)
# this gives the program max flexibility
TARGET_DIR = None  # e.g., "~/OneDrive/Documents/GitHub/github_repo_importer/projects"

# === SETUP SCRIPT DIRECTORY AND LOGGING ===
script_dir = pathlib.Path(__file__).parent.resolve()
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file = script_dir / f"directory_sizes_{timestamp}.log"

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)

def format_size(bytes_size):
    """Convert bytes into a human-readable KB, MB, or GB format."""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 ** 2:
        return f"{bytes_size / 1024:.2f} KB"
    elif bytes_size < 1024 ** 3:
        return f"{bytes_size / (1024 ** 2):.2f} MB"
    else:
        return f"{bytes_size / (1024 ** 3):.2f} GB"

def get_directory_sizes(path, allocation_unit=4096):
    """Recursively calculate total size and size-on-disk of all files in a directory."""
    total_size = 0
    size_on_disk = 0
    try:
        for root, dirs, files in os.walk(path, topdown=True, followlinks=False):
            for f in files:
                try:
                    fp = os.path.join(root, f)
                    size = os.path.getsize(fp)
                    total_size += size
                    # Round up to nearest allocation unit to estimate disk usage
                    size_on_disk += math.ceil(size / allocation_unit) * allocation_unit
                except Exception as fe:
                    logging.warning(f"⚠️ Could not read size of file {fp}: {fe}")
    except Exception as e:
        logging.error(f"❌ Error walking through {path}: {e}")
        return 0, 0
    return total_size, size_on_disk

def list_subdirectory_sizes(base_path):
    if not base_path.is_dir():
        logging.error(f"❌ Path not found or not a directory: {base_path}")
        print(f"❌ Invalid path: {base_path}")
        return

    print(f"\n📂 Scanning directory: {base_path}\n")
    logging.info(f"📂 Scanning directory: {base_path}")

    dir_sizes = []
    total_bytes = 0
    total_disk = 0

    for item in base_path.iterdir():
        if item.is_dir() and not item.is_symlink():
            size_bytes, disk_bytes = get_directory_sizes(item)
            dir_sizes.append((item.name, size_bytes, disk_bytes))
            total_bytes += size_bytes
            total_disk += disk_bytes
            logging.info(f"📁 {item.name}: actual={format_size(size_bytes)}, disk={format_size(disk_bytes)}")

    dir_sizes.sort(key=lambda x: x[1], reverse=True)

    for name, size_bytes, disk_bytes in dir_sizes:
        print(f"📦 {name:<30} — actual: {format_size(size_bytes):>10} | disk: {format_size(disk_bytes):>10}")

    print(f"\n📊 Total size of subdirectories:")
    print(f"   📄 Actual Size     : {format_size(total_bytes)}")
    print(f"   💽 Size on Disk    : {format_size(total_disk)}")

    logging.info(f"📊 Total actual size: {format_size(total_bytes)}")
    logging.info(f"💽 Total size on disk: {format_size(total_disk)}")

    print(f"\n✅ Done. Log saved to: {log_file}")

if __name__ == "__main__":
    # Priority: CLI arg > TARGET_DIR > script location
    if len(sys.argv) > 1:
        user_path = pathlib.Path(sys.argv[1]).expanduser().resolve()
    elif TARGET_DIR:
        user_path = pathlib.Path(TARGET_DIR).expanduser().resolve()
    else:
        user_path = script_dir

    list_subdirectory_sizes(user_path)
