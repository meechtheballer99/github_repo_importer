import requests
import json

# --- Configuration ---
username = "meechtheballer99"
api_url = f"https://api.github.com/users/{username}/repos"
full_output = "repos.json"
links_output = "repo_links.json"

# --- Fetch Repositories ---
print(f"🔍 Fetching repos for user '{username}'...")
response = requests.get(api_url)
response.raise_for_status()
repos = response.json()

# --- Save Full Response ---
with open(full_output, "w") as f:
    json.dump(repos, f, indent=4)
print(f"📦 Saved full repo data to '{full_output}'")

# --- Extract name and html_url ---
repo_links = [
    {"name": repo["name"], "url": repo["html_url"]}
    for repo in repos
]

# --- Save Extracted Repo Links ---
with open(links_output, "w") as f:
    json.dump(repo_links, f, indent=4)
print(f"✅ Saved simplified repo links to '{links_output}'")
