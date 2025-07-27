#!/usr/bin/env python3
"""
import_to_github.py
-------------------
Bulk‑create (or skip) GitHub repositories and push local folders.

Key behaviours
  • If the repo already exists → skip everything (no defaults, no push).
  • If the repo is created but push fails → log that distinction.
  • Clear status icons for Success / Failed / Skipped in the final summary.
  • If pause_between_repos == True → always pause after each repo, regardless of outcome,
    showing which repo is next with a ➡️ marker.
  • NEW: one commit per top‑level directory (plus a root‑files commit) so you can see
    exactly which directory was last pushed if the run fails mid‑way.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import requests
import logging
from datetime import datetime
from typing import List                      # NEW

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
repo_status: dict[str, str]         = {}   # {repo_name: "Success" | "Failed" | "Skipped"}
repo_status_details: dict[str, str] = {}   # {repo_name: human-readable reason}


def get_next_repo(current_repo: str | None) -> str | None:
    """Return the next repo (by order in config.json) that hasn't been processed yet."""
    found_current = current_repo is None
    for project in config.get("projects", []):
        name = project.get("repo_name")
        if not found_current:
            found_current = (name == current_repo)
            continue
        if found_current and name not in repo_status:
            return name
    return None


def print_repo_summary(
    config_projects: list,
    status: dict[str, str],
    details: dict[str, str],
    next_repo: str | None = None,
) -> None:
    """Pretty one‑pager at the end (or after each pause if enabled)."""
    logging.info("📊 Repository status summary:")
    for project in config_projects:
        repo    = project.get("repo_name") or "Unnamed"
        state   = status.get(repo, "Not yet processed")
        reason  = details.get(repo, "")

        # icon per state
        match state:
            case "Success" if "already exists" in reason.lower(): symbol = "⚠️"
            case "Success":   symbol = "✅"
            case "Failed":    symbol = "❌"
            case "Skipped":   symbol = "⏭️"
            case _:           symbol = "⏳"

        # arrow for next repo
        if repo == next_repo:
            symbol = "➡️"

        msg = f"   {symbol} {repo} - {state}"
        if reason:
            msg += f" (! {reason})"
        logging.info(msg)


def pause_if_requested(current_repo: str) -> None:
    """
    Pause between repos if the config flag is True.
    Shows summary and the ➡️ pointer for what's next.
    """
    if not pause_between_repos:
        return

    next_repo = get_next_repo(current_repo)
    logging.info(f"⏸️ Paused after processing: {current_repo}")
    print_repo_summary(
        config.get("projects", []),
        repo_status,
        repo_status_details,
        next_repo=next_repo,
    )
    prompt = "\n🔄 Press Enter to continue"
    if next_repo:
        prompt += f" to the next repository ({next_repo})"
    prompt += "...\n"
    input(prompt)

# ---------------------------------------------------------------------------
#  Helper: enable paths longer than 260 chars on Windows
# ---------------------------------------------------------------------------
def win_long(path: str) -> str:
    """
    Prefix the absolute path with  \\?\\  on Windows so the OS uses the
    extended‑length file‑system APIs (32 767‑char limit).
    On non‑Windows systems the path is returned unchanged.
    """
    if os.name == "nt":
        abs_path = os.path.abspath(path)
        if not abs_path.startswith(r"\\?\\"):
            abs_path = r"\\?\\" + abs_path
        return abs_path
    return path


# ---------------------------------------------------------------------------
#  Optional initial pause before the first repo
# ---------------------------------------------------------------------------
if pause_between_repos:
    next_repo = get_next_repo(None)          # first repo that will be processed
    logging.info("⏸️ Initial pause before processing any repositories.")
    print_repo_summary(
        config.get("projects", []),
        repo_status,
        repo_status_details,
        next_repo=next_repo,
    )
    input(f"\n🔄 Press Enter to start with the first repository ({next_repo})...\n")


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
        resp = requests.get(repo_api_url, headers=headers, timeout=15)
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
        payload = {"name": name, "description": desc, "private": private}
        c_resp  = requests.post(
            "https://api.github.com/user/repos",
            headers=headers,
            json=payload,
            timeout=30,
        )

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
            shutil.copytree(win_long(input_folder), win_long(dest_path))

            def write_if_missing(path: str, content: str, label: str) -> None:
                path = win_long(path)            # long‑path safe
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

            # ------------------------------------------------------------------
            #  NEW incremental git workflow with verbose logging
            # ------------------------------------------------------------------
            git("init")
            git("config", "user.name", username)
            git("config", "user.email", f"{username}@users.noreply.github.com")
            git("branch", "-M", "main")
            git("remote", "add", "origin", repo_url)
            logging.info("🔧 Git repo initialised and remote set to %s", repo_url)

            def commit_and_push(paths: List[str], message: str, first: bool = False) -> None:
                """Add paths, commit, push, and log each step."""
                rel = ", ".join(paths)
                logging.info("➕  Adding paths: %s", rel)
                git("add", *paths)

                logging.info("💾  Committing: %s", message)
                git("commit", "-m", message)

                logging.info("🚀  Pushing commit (%s)…", "first push" if first else "subsequent push")
                if first:
                    git("push", "-u", push_url, "main")   # set upstream
                else:
                    git("push", push_url, "main")
                logging.info("✅  Push complete for: %s", message)

            # --- classify items at repo root ----------------------------------
            items      = sorted(os.listdir(dest_path))
            root_files = [p for p in items if os.path.isfile(os.path.join(dest_path, p))]
            root_dirs  = [p for p in items if os.path.isdir(os.path.join(dest_path, p))]

            first_push = True

            # --- commit + push root‑level files -------------------------------
            if root_files:
                logging.info("📂 Root‑level files detected: %s", ", ".join(root_files))
                commit_and_push(root_files, "Add root‑level files", first=True)
                first_push = False                      # upstream now set
            else:
                logging.info("📂 No root‑level files to commit")

            # --- commit + push each top‑level directory -----------------------
            for d in root_dirs:
                logging.info("📁 Processing directory: %s", d)
                commit_and_push([d], f"Add {d} directory", first=first_push)
                first_push = False

            logging.info(f"🚀 Successfully pushed files from '{input_folder}' to '{repo_url}'")
            repo_status[name]         = "Success"
            repo_status_details[name] = "✅ Repo created and files pushed"

    # ---------- enhanced failure diagnostics ----------
    except subprocess.CalledProcessError as e:
        # Capture stdout & stderr for the git command that failed
        out = (e.stdout or b"").decode(errors="ignore").strip()
        err = (e.stderr or b"").decode(errors="ignore").strip()
        masked_cmd = " ".join(e.cmd).replace(token, "****")
        logging.error(
            f"❌ Push failed for '{name}':\n"
            f"    return code: {e.returncode}\n"
            f"    command: {masked_cmd}\n"
            f"    stdout: {out!r}\n"
            f"    stderr: {err!r}"
        )
        repo_status[name]         = "Failed"
        repo_status_details[name] = "⚠️ Repo created but push failed"

    except Exception:
        # Any other unexpected error: full traceback for easier debugging
        logging.exception(f"❌ Unexpected error processing '{name}'")
        repo_status[name]         = "Failed"
        repo_status_details[name] = "❌ Push/setup failed (see traceback)"

    # ---------- always pause if requested ----------
    pause_if_requested(name)

# ---------------------------------------------------------------------------
#  Final report
# ---------------------------------------------------------------------------
logging.info("\n🏁 All projects processed. Final summary:")
print_repo_summary(
    config.get("projects", []),
    repo_status,
    repo_status_details,
)
