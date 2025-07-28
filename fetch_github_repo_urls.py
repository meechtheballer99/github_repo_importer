import requests
import json

# Replace with your GitHub username
username = "meechtheballer99"
url = f"https://api.github.com/users/{username}/repos"

# Send GET request to GitHub API
response = requests.get(url)

# Raise error if request failed
response.raise_for_status()

# Parse JSON response
repos = response.json()

# Write to repos.json
with open("repos.json", "w") as f:
    json.dump(repos, f, indent=4)

print(f"✅ Successfully saved {len(repos)} repos to repos.json")
