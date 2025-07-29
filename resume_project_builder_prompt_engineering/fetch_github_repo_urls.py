#!/usr/bin/env python3
"""
Fetch *all* public repositories for a GitHub user, no matter how many pages.

Usage:
    python fetch_github_repo_urls.py [github_username]

If you omit the command‑line argument the script falls back to the USERNAME
constant below.  It writes two files:
  • repos.json      – the full GitHub API response (every repo field)
  • repo_links.json – just "name" and "html_url" for each repo
"""

import json
import sys
import time
from pathlib import Path

import requests

# ---------------------------- Configuration ---------------------------- #

USERNAME       = "meechtheballer99"         # default; can be overridden by argv
API_ROOT       = "https://api.github.com"
HEADERS        = {"Accept": "application/vnd.github+json"}  # good practice
PARAMS         = {"per_page": 100, "type": "public"}        # 100 = API max
FULL_OUTPUT    = Path("repos.json")
LINKS_OUTPUT   = Path("repo_links.json")
BACKOFF_SECS   = 1.0    # naive back‑off if we ever hit secondary rate limits

# If you have a Personal Access Token, uncomment the next line and replace
# 'YOUR_TOKEN' – this lifts you to higher rate‑limit ceilings.
# HEADERS["Authorization"] = "Bearer YOUR_TOKEN"

# --------------------------- Helper Functions -------------------------- #

def fetch_all_repos(username: str) -> list[dict]:
    """Walk through every paginated result and return a list of repos."""
    repos: list[dict] = []
    url, params = f"{API_ROOT}/users/{username}/repos", PARAMS

    while url:
        resp = requests.get(url, headers=HEADERS, params=params)
        # Handle the odd 403 from secondary rate limits with a tiny nap + retry
        if resp.status_code == 403 and "secondary rate limit" in resp.text.lower():
            time.sleep(BACKOFF_SECS)
            continue

        resp.raise_for_status()
        repos.extend(resp.json())

        # GitHub encodes pagination URLs in the Link header
        url = resp.links.get("next", {}).get("url")  # None when we're done
        params = None  # subsequent URLs already contain ?per_page=… etc.

    return repos

def save_json(data: object, path: Path) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True))
    print(f"💾  Wrote {path}")

# ------------------------------ Main ----------------------------------- #

def main() -> None:
    user = sys.argv[1] if len(sys.argv) > 1 else USERNAME
    print(f"🔍 Fetching public repos for '{user}' …")

    repos = fetch_all_repos(user)
    print(f"✅ Retrieved {len(repos)} repositories")

    # Full JSON payload
    save_json(repos, FULL_OUTPUT)

    # Slimmed‑down list for quick use (name + HTML URL)
    repo_links = [{"name": r["name"], "url": r["html_url"]} for r in repos]
    save_json(repo_links, LINKS_OUTPUT)

if __name__ == "__main__":
    main()
