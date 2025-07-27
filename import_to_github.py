#!/usr/bin/env python3
"""
import_to_github.py
-------------------
Bulk‑create (or skip) GitHub repositories and push local folders.

Key behaviours
  • If the repo already exists → skip everything (no defaults, no push).
  • If the repo is created but push fails → log that distinction.
  • Clear status icons for Success / Failed / Skipped in the final summary.
  • If pause_between_repos == True → always pause after each repo, regardless of outcome.
"""

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

# ---------------------------------------------------------------------------
#  Logging
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
#  Load configuration
# ---------------------------------------------------------------------------
try:
    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)

    token     = config["github_token"]
    username  = config["username"]
    headers   = {"Authorization": f"token {token}"}

    pause_between_repos = config.get("pause_between_repos", pause_between_repos)

except Exception as e:
    logging.error(f"Failed to load configuration: {e}")
    raise SystemExit(1)

# ---------------------------------------------------------------------------
#  Status tracking helpers
# ---------------------------------------------------------------------------
repo_status          = {}   # {repo_name: "Success" | "Failed" | "Skipped"}
repo_status_details  = {}   # {repo_name: human‑readable reason}


def print_repo_summary(config_projects: list,
                       status: dict[str, str],
                       details: dict[str, str]) -> None:
    """Pretty one‑pager at the end (or after each pause if enabled)."""
    logging.info("📊 Repository status summary:")
    for project in config_projects:
        repo    = project.get("repo_name") or "Unnamed"
        state   = status.get(repo, "Not yet processed")
        reason  = details.get(repo, "")

        # pick an icon
        match state:
            case "Success" if "already exists" in reason.lower(): symbol = "⚠️"
            case "Success":   symbol = "✅"
            case "Failed":    symbol = "❌"
            case "Skipped":   symbol = "⏭️"
            case _:           symbol = "⏳"

        msg = f"   {symbol} {repo} - {state}"
        if reason:
            msg += f" (! {reason})"
        logging.info(msg)


def pause_if_requested(repo_name: str) -> None:
    """Pause between repos if flag turned on."""
    if pause_between_repos:
        logging.info(f"⏸️ Paused after processing: {repo_name}")
        print_repo_summary(config.get("projects", []), repo_status, repo_status_details)
        input("\n🔄 Press Enter to continue to the next repository...\n")


# ---------------------------------------------------------------------------
#  Main processing loop
# ---------------------------------------------------------------------------
for project in config.get("projects", []):
    name         = project.get("repo_name")
    desc         = project.get("repo_description", "")
    private      = project.get("private", True)
    input_folder = project.get("input_folder")

    logging.info(f"📁 Processing project: {name}")

    # ---------- basic validation ----------
    if not all([name, input_folder]):
        logging.warning(f"⚠️ Skipping invalid project configuration: {project}")
        repo_status[name or "Unnamed"]         = "Skipped"
        repo_status_details[name or "Unnamed"] = "⏭️ Missing repo_name or input_folder"
        pause_if_requested(name or "Unnamed")
        continue

    # ---------- does the repo already exist? ----------
    repo_api_url = f"https://api.github.com/repos/{username}/{name}"
    try:
        resp = requests.get(repo_api_url, headers=headers)
        if resp.status_code == 200:
            logging.warning(f"⚠️ Repo already exists: {name} – skipping.")
            repo_status[name]         = "Skipped"
            repo_status_details[name] = "⚠️ Repo already exists"
            pause_if_requested(name)
            continue
    except Exception as e:
        logging.error(f"❌ Error checking repo existence for {name}: {e}")
        repo_status[name]         = "Failed"
        repo_status_details[name] = "❌ Repo existence check failed"
        pause_if_requested(name)
        continue

    # ---------- create the repo ----------
    repo_created = False
    try:
        payload  = {"name": name, "description": desc, "private": private}
        c_resp   = requests.post("https://api.github.com/user/repos",
                                 headers=headers, json=payload)

        if c_resp.status_code == 201:
            logging.info(f"✅ Repo {name} created successfully.")
            repo_created = True
            repo_status[name]         = "Success"
            repo_status_details[name] = "✅ Repo created (push pending)"
        else:
            msg = c_resp.json().get("message", "unknown error")
            logging.error(f"❌ Failed to create repo '{name}': {c_resp.status_code} - {msg}")
            repo_status[name]         = "Failed"
            repo_status_details[name] = f"❌ Repo creation failed: {msg}"
            pause_if_requested(name)
            continue
    except requests.RequestException as e:
        logging.error(f"❌ Exception while creating repo '{name}': {e}")
        repo_status[name]         = "Failed"
        repo_status_details[name] = "❌ Repo creation failed"
        pause_if_requested(name)
        continue

    # ---------- copy files, write defaults, git init & push ----------
    try:
        repo_url = f"https://github.com/{username}/{name}.git"
        push_url = f"https://{username}:{token}@github.com/{username}/{name}.git"

        with tempfile.TemporaryDirectory() as tmpdir:
            dest_path = os.path.join(tmpdir, name)
            shutil.copytree(input_folder, dest_path)

            def write_if_missing(path: str, content: str, label: str) -> None:
                if not os.path.exists(path):
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)
                    logging.info(f"Created default {label} for {name}")

            write_if_missing(
                os.path.join(dest_path, ".gitignore"),
                "__pycache__/\n*.pyc\n.env\n.DS_Store\n*.log\n*.sqlite3\n*.egg-info/\n*.idea/\n.vscode/\n",
                ".gitignore",
            )
            write_if_missing(
                os.path.join(dest_path, "README.md"),
                f"# {name}\n\n{desc}\n",
                "README.md",
            )

            def git(*args: str) -> None:
                subprocess.run(
                    ["git", *args],
                    check=True,
                    cwd=dest_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

            git("init")
            git("config", "user.name", username)
            git("config", "user.email", f"{username}@users.noreply.github.com")
            git("add", ".")
            git("commit", "-m", "Initial commit")
            git("branch", "-M", "main")
            git("remote", "add", "origin", repo_url)
            git("push", "-u", push_url, "main")

            logging.info(f"🚀 Successfully pushed files from '{input_folder}' to '{repo_url}'")
            repo_status[name]         = "Success"
            repo_status_details[name] = "✅ Repo created and files pushed"

    except Exception as e:
        logging.error(f"❌ Push failed for '{name}': {e}")
        repo_status[name] = "Failed"
        if repo_created:
            repo_status_details[name] = "⚠️ Repo created but push failed"
        else:
            repo_status_details[name] = "❌ Push/setup failed"

    # ---------- always pause if requested ----------
    pause_if_requested(name)

# ---------------------------------------------------------------------------
#  Final report
# ---------------------------------------------------------------------------
logging.info("\n🏁 All projects processed. Final summary:")
print_repo_summary(config.get("projects", []), repo_status, repo_status_details)
