# github_repo_importer
Use this to import (create) repos in my github - specifically uploading all my college and research projects 


That error means GitHub **rejected your token** — it's a **401 Unauthorized** response:

---

### ❌ What "Bad credentials" Means

GitHub is saying:

> "The `github_token` you're sending is either missing, invalid, expired, or doesn't have the right permissions."

---

### ✅ How to Fix It

#### 1. **Double-check your `config.json`**

Make sure this line is correct:

```json
"github_token": "ghp_XXXXXXXXXXXXXXXXXXXX"
```

* Replace `"ghp_XXXXXXXXXXXXXXXXXXXX"` with your **actual** GitHub token (starts with `ghp_`)
* No extra quotes, whitespace, or trailing commas
* Don’t include the word "Bearer" or anything else

---

#### 2. **Generate a New Token** (if needed)

Go to: [https://github.com/settings/tokens](https://github.com/settings/tokens)

1. Click **"Generate new token"**
2. Use **"Classic" token**, not fine-grained
3. **Give it permissions**:

   * `repo` ✅ (for creating and pushing to repos)
4. Copy the token (you won’t see it again)
5. Paste it into your `config.json`

---

### 🧪 Example Good `config.json` Token Section

```json
{
  "github_token": "ghp_abc123def456ghi789jkl000",
  "username": "your_github_username",
  ...
}
```

---

### ✅ After That

Save the file and rerun:

```bash
python import_to_github.py
```

Let me know if you'd like help checking the exact permissions or creating the token correctly — I can walk you through it step-by-step.
