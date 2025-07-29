### 🧠 FULL LLM PROMPT (Use per JSON file)

---

I am preparing the **Programming Projects** section of my résumé. The JSON content I’m providing comes from my GitHub repositories—one JSON file per university course (each GitHub repo corresponds to a course).

Here’s what I need you to do:

---

### 🔍 Input Format

You’ll receive a JSON array with this shape:

```json
[
  {
    "repo": "REPO_NAME",
    "folder": "project/subfolder/path",
    "code_files": ["path/to/file1.cpp", "path/to/file2.py"],
    "snippets": [
      {
        "file": "path/to/file1.cpp",
        "snippet": "// sample code snippet"
      }
      // …
    ]
  }
  // …
]
```

Each object represents **one project/assignment folder** that contains source code.

You will also have access to **`repo_links.json`**, which maps every repository name to its GitHub URL:

```json
[
  { "name": "CIS-150_COMPUTER_SCIENCE_I",
    "url": "https://github.com/meechtheballer99/CIS-150_COMPUTER_SCIENCE_I" },
  { "name": "CIS-200_COMPUTER_SCIENCE_II",
    "url": "https://github.com/meechtheballer99/CIS-200_COMPUTER_SCIENCE_II" }
  // …
]
```

---

### ✅ Your Tasks

For **each project object** in the list:

1. **Create a clean, résumé‑ready project title** derived from the `folder` path and snippets.
2. **Classify the domain**—e.g., `C++`, `AI`, `ML`, `Python`, `systems`, `web`, etc.
3. **Write a concise 1–2‑sentence summary** describing what the project does, using only the folder name and snippets.
4. **Generate an HTML `<li>` element** containing:

   * **A link to the project's subfolder** on GitHub (see “🔗 Building GitHub Links” below).
   * The **bolded project title**, domain tag, and summary.

---

#### 🔗 Building GitHub Links — *MUST match repo structure*

1. Find the repository’s **base URL** by matching the `repo` field to the `name` field in `repo_links.json`.
2. Append `/tree/main/` followed by the **exact `folder` path**, preserving the directory hierarchy.

   * Encode spaces and special characters as GitHub does (e.g., `" "` → `%20`).
3. Example:

```
Base URL:  https://github.com/meechtheballer99/CIS-150_COMPUTER_SCIENCE_I  
Folder:    FINAL PROJECT CIS-150 WINTER 2020/FINAL PROJECT CIS-150 WINTER 2020 - MEECH  
Full link: https://github.com/meechtheballer99/CIS-150_COMPUTER_SCIENCE_I/tree/main/FINAL%20PROJECT%20CIS-150%20WINTER%202020/FINAL%20PROJECT%20CIS-150%20WINTER%202020%20-%20MEECH
```

The link **must point to that folder** so anyone can browse the project exactly as it appears in the repo.

---

### 📤 Output Format

Output one `<li>` per project, wrapped in a single `<ul>` under a course header. Example:

```html
<h3>CS 225: Data Structures</h3>
<ul>
  <li>
    <a href="https://github.com/meechtheballer99/cs225/tree/main/mp_traversals">
      <strong>Image Traversal Visualizer</strong>
    </a> (C++): Implemented DFS and BFS to traverse and manipulate image pixels based on color thresholds, enabling interactive visual exploration.
  </li>
  <!-- more projects -->
</ul>
```

---

### ⚠️ Notes

* Skip folders that are clearly lecture notes, textbooks, web links, or boilerplate.
* Don’t summarize PDFs/DOCs—rely only on code snippets and folder names.
* Feel free to refine unclear project titles using available context.


If you could, please give the final output html as a file i can download (please name it appropriately.)