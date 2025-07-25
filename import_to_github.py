import json
import os
import shutil
import subprocess
import tempfile
import requests

# Load config
with open("config.json") as f:
    config = json.load(f)

token = config["github_token"]
username = config["username"]
headers = {"Authorization": f"token {token}"}

for project in config["projects"]:
    name = project["repo_name"]
    desc = project["repo_description"]
    private = project["private"]
    input_folder = project["input_folder"]

    print(f"\n📁 Processing: {name}")

    # Create repo on GitHub
    payload = {
        "name": name,
        "description": desc,
        "private": private
    }
    response = requests.post("https://api.github.com/user/repos", headers=headers, json=payload)

    if response.status_code == 201:
        print(f"✅ Created repo: {name}")
    elif response.status_code == 422 and "already exists" in response.text:
        print(f"⚠️ Repo already exists: {name}")
    else:
        print(f"❌ Failed to create repo: {response.text}")
        continue

    repo_url = f"https://github.com/{username}/{name}.git"
    push_url = f"https://{username}:{token}@github.com/{username}/{name}.git"

    # Setup temp Git repo
    with tempfile.TemporaryDirectory() as tmpdir:
        dest_path = os.path.join(tmpdir, name)
        shutil.copytree(input_folder, dest_path)

        # ✅ Auto-create .gitignore if not present
        gitignore_path = os.path.join(dest_path, ".gitignore")
        if not os.path.exists(gitignore_path):
            with open(gitignore_path, "w") as f:
                f.write("__pycache__/\n*.pyc\n.env\n.DS_Store\n*.log\n*.sqlite3\n*.egg-info/\n*.idea/\n.vscode/\n")

        # ✅ Auto-create README.md if not present
        readme_path = os.path.join(dest_path, "README.md")
        if not os.path.exists(readme_path):
            with open(readme_path, "w") as f:
                f.write(f"# {name}\n\n{desc}\n")

        def git(*args):
            subprocess.run(["git", *args], check=True, cwd=dest_path)

        git("init")
        git("config", "user.name", username)
        git("config", "user.email", f"{username}@users.noreply.github.com")
        git("add", ".")
        git("commit", "-m", "Initial commit")
        git("branch", "-M", "main")
        git("remote", "add", "origin", repo_url)
        git("push", "-u", push_url, "main")
        
        print(f"🚀 Pushed to: {repo_url}")
