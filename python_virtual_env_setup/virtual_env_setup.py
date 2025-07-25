import os
import subprocess
import sys
import venv
from pathlib import Path
import logging
import re

# Required packages
REQUIRED_PACKAGES = ["requests"]

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
VENV_DIR = SCRIPT_DIR / "github_import_python_venv"
ACTIVATE_PATH = VENV_DIR / "Scripts" / "activate.bat"
LOG_FILE = SCRIPT_DIR / "setup_github_import_python_venv.log"
PYTHON_EXE = VENV_DIR / "Scripts" / "python.exe"

# ---------- Safe Logging Setup ----------
class SafeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            self.stream.write(msg + self.terminator)
            self.flush()
        except UnicodeEncodeError:
            msg = self.format(record).encode(self.stream.encoding, errors='replace').decode(self.stream.encoding)
            self.stream.write(msg + self.terminator)
            self.flush()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
        SafeStreamHandler(sys.stdout)
    ]
)

# ---------- Core Functions ----------
def create_virtual_env():
    if not VENV_DIR.exists():
        logging.info("Creating virtual environment...")
        venv.create(VENV_DIR, with_pip=True)
        logging.info("Virtual environment created.")
    else:
        logging.info("Virtual environment already exists.")

def run_in_venv(command):
    full_cmd = [str(PYTHON_EXE), "-m"] + command
    logging.info(f"Running command in venv: {' '.join(full_cmd)}")
    result = subprocess.run(
        full_cmd,
        capture_output=True,
        text=True
    )
    if result.stdout:
        logging.info(result.stdout.strip())
    if result.stderr:
        logging.error(result.stderr.strip())
    return result

def check_installed(package):
    result = run_in_venv(["pip", "show", package])
    return result.returncode == 0

def install_packages():
    missing = [pkg for pkg in REQUIRED_PACKAGES if not check_installed(pkg)]
    if missing:
        logging.info(f"Installing missing packages: {', '.join(missing)}")
        result = run_in_venv(["pip", "install"] + missing)
        if result.returncode != 0:
            logging.error(f"Failed to install packages: {', '.join(missing)}")
            sys.exit(1)
    else:
        logging.info("All required packages are already installed.")

def check_for_pip_upgrade():
    result = run_in_venv(["pip", "list", "--outdated"])
    if result.returncode != 0:
        logging.warning("Unable to check for outdated packages.")
        return

    for line in result.stdout.splitlines():
        if line.lower().startswith("pip"):
            parts = re.split(r"\s+", line)
            if len(parts) >= 3:
                current, latest = parts[1], parts[2]
                logging.warning(f"Pip upgrade available: {current} → {latest}")
                response = input("Upgrade pip now? (y/n): ").strip().lower()
                if response == 'y':
                    upgrade_result = run_in_venv(["pip", "install", "--upgrade", "pip"])
                    if upgrade_result.returncode == 0:
                        logging.info("pip successfully upgraded.")
                    else:
                        logging.error("pip upgrade failed.")
                else:
                    logging.info("Skipped pip upgrade.")
            break

# ---------- Main ----------
def main():
    logging.info("Starting environment setup...")
    create_virtual_env()
    install_packages()
    check_for_pip_upgrade()

    logging.info("Environment setup complete.")
    logging.info(f"To activate the environment, run:\n{ACTIVATE_PATH}")
    logging.info("Then you can run your script with:\npython your_script.py")

if __name__ == "__main__":
    main()
