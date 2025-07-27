import json
import os
import shutil
import subprocess
import tempfile
import requests
import logging
from datetime import datetime

# === Default setting (can be overridden by config.json) ===
pause_between_repos = False

# Setup logging
log_filename = f"upload_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

# Load config
try:
    with open("config.json") as f:
        config = json.load(f)
    token = config["github_token"]
    username = config["username"]
    headers = {"Authorization": f"token {token}"}

    # Override default pause flag if specified in config
    if "pause_between_repos" in config:
        pause_between_repos = config["pause_between_repos"]

except Exception as e:
    logging.error(f"Failed to load configuration: {e}")
    raise SystemExit(1)

# Process each project
for project in config.get("projects", []):
    name = project.get("repo_name")
    desc = project.get("repo_description", "")
    private = project.get("private", True)
    input_folder = project.get("input_folder")

    logging.info(f"📁 Processing project: {name}")

    if not all([name, input_folder]):
        logging.warning(f"Skipping invalid project configuration: {project}")
        continue

    # Create GitHub repo
    payload = {"name": name, "description": desc, "private": private}
    try:
        response = requests.post("https://api.github.com/user/repos", headers=headers, json=payload)
        if response.status_code == 201:
            logging.info(f"✅ Created repo: {name}")
        elif response.status_code == 422 and "already exists" in response.text:
            logging.warning(f"⚠️ Repo already exists: {name}")
        else:
            logging.error(f"❌ Failed to create repo '{name}': {response.status_code} - {response.text}")
            continue
    except requests.RequestException as e:
        logging.error(f"❌ Exception while creating repo '{name}': {e}")
        continue

    repo_url = f"https://github.com/{username}/{name}.git"
    push_url = f"https://{username}:{token}@github.com/{username}/{name}.git"

    # Setup temp Git repo
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            dest_path = os.path.join(tmpdir, name)
            shutil.copytree(input_folder, dest_path)

            # Create .gitignore if needed
            gitignore_path = os.path.join(dest_path, ".gitignore")
            if not os.path.exists(gitignore_path):
                with open(gitignore_path, "w") as f:
                    f.write("__pycache__/\n*.pyc\n.env\n.DS_Store\n*.log\n*.sqlite3\n*.egg-info/\n*.idea/\n.vscode/\n")
                    logging.info(f"Created default .gitignore for {name}")

            # Create README.md if needed
            readme_path = os.path.join(dest_path, "README.md")
            if not os.path.exists(readme_path):
                with open(readme_path, "w") as f:
                    f.write(f"# {name}\n\n{desc}\n")
                    logging.info(f"Created default README.md for {name}")

            def git(*args):
                subprocess.run(["git", *args], check=True, cwd=dest_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            git("init")
            git("config", "user.name", username)
            git("config", "user.email", f"{username}@users.noreply.github.com")
            git("add", ".")
            git("commit", "-m", "Initial commit")
            git("branch", "-M", "main")
            git("remote", "add", "origin", repo_url)
            git("push", "-u", push_url, "main")

            logging.info(f"🚀 Successfully pushed to: {repo_url}")

    except (subprocess.CalledProcessError, OSError, Exception) as e:
        logging.error(f"❌ Failed to process repo '{name}': {e}")
        continue

    # Optional pause
    if pause_between_repos:
        input("⏸️ Press Enter to continue to the next repository...")
