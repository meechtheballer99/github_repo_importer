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

The below output is an example output that is a good model of how the format should be

```html
<h3>CIS 150: Computer Science I</h3>
<ul>
  <li>
    <a href="https://github.com/meechtheballer99/CIS-150_COMPUTER_SCIENCE_I/tree/main/FINAL%20PROJECT%20CIS-150%20WINTER%202020/FINAL%20PROJECT%20CIS-150%20WINTER%202020%20-%20MEECH">
      <strong>Dynamic Airline Seat Reservation System</strong>
    </a> (C++): Built a flexible airline reservation and cancellation system that handles any number of rows and seat configurations by parsing structured input files; supported mixed row formats and dynamic seating arrangements.
  </li>
  <li>
    <a href="https://github.com/meechtheballer99/CIS-150_COMPUTER_SCIENCE_I/tree/main/Lab%201">
      <strong>Introductory Console I/O Programs</strong>
    </a> (C++): Wrote basic programs including "Hello World", input/output prompts, and ASCII triangle patterns to build foundational C++ programming skills.
  </li>
  <li>
    <a href="https://github.com/meechtheballer99/CIS-150_COMPUTER_SCIENCE_I/tree/main/Lab%202">
      <strong>Coin Value Calculator and Input Summation</strong>
    </a> (C++): Computed dollar values from coin counts and summed two integers based on user input, focusing on basic arithmetic and input handling.
  </li>
  <li>
    <a href="https://github.com/meechtheballer99/CIS-150_COMPUTER_SCIENCE_I/tree/main/Lab%203">
      <strong>Conditional Logic and Equation Solver</strong>
    </a> (C++): Implemented voter eligibility checks, overtime pay calculation, and quadratic equation root evaluation using control structures and mathematical formulas.
  </li>
  <li>
    <a href="https://github.com/meechtheballer99/CIS-150_COMPUTER_SCIENCE_I/tree/main/Lab%204">
      <strong>Control Flow and Loop Constructs</strong>
    </a> (C++): Developed programs using `if/else`, `switch`, and loops to handle temperature advice, triangle printing, and grade interpretation based on user inputs.
  </li>
  <li>
    <a href="https://github.com/meechtheballer99/CIS-150_COMPUTER_SCIENCE_I/tree/main/Lab%205">
      <strong>Classroom and Game Data Evaluators</strong>
    </a> (C++): Built applications to compute average grades, determine basketball winners, and find max/min values from sets of integers using functions and menus.
  </li>
  <li>
    <a href="https://github.com/meechtheballer99/CIS-150_COMPUTER_SCIENCE_I/tree/main/Lab%206">
      <strong>Function Design with Pass-by-Reference</strong>
    </a> (C++): Created reusable functions to compute sums, averages, and reference-modifying operations while emphasizing return types and parameter passing.
  </li>
  <li>
    <a href="https://github.com/meechtheballer99/CIS-150_COMPUTER_SCIENCE_I/tree/main/Lab%207">
      <strong>File-Based Payroll and Grade Analyzer</strong>
    </a> (C++): Parsed structured employee and student data files to calculate weekly salaries and grade statistics using file I/O and array operations.
  </li>
  <li>
    <a href="https://github.com/meechtheballer99/CIS-150_COMPUTER_SCIENCE_I/tree/main/Lab%208">
      <strong>Array Statistics and Search Tool</strong>
    </a> (C++): Implemented functions to compute array metrics (sum, avg, min, max) and search values by position using linear search techniques.
  </li>
  <li>
    <a href="https://github.com/meechtheballer99/CIS-150_COMPUTER_SCIENCE_I/tree/main/Lab%209/Lab%2009%20-%20Meech">
      <strong>2D Array and Struct-Based Grade Processing</strong>
    </a> (C++): Wrote functions to analyze 2D arrays for averages and searches; also used structs to read student grade files and compute statistical summaries.
  </li>
  <li>
    <a href="https://github.com/meechtheballer99/CIS-150_COMPUTER_SCIENCE_I/tree/main/Lab%2010/Lab%2010%20-%20Meech">
      <strong>Temperature Analyzer with Vectors</strong>
    </a> (C++): Designed functions using STL vectors to filter and count freezing temperatures from a dataset, emphasizing vector manipulation and file input.
  </li>
  <li>
    <a href="https://github.com/meechtheballer99/CIS-150_COMPUTER_SCIENCE_I/tree/main/Lab%2011/Lab%2011%20-%20Meech">
      <strong>US State Database System</strong>
    </a> (C++): Created a `State` class and supporting functions to manage a US state database with search by year of statehood and abbreviation; processed from structured file input.
  </li>
  <li>
    <a href="https://github.com/meechtheballer99/CIS-150_COMPUTER_SCIENCE_I/tree/main/WORKOUT%20PACE%20CALCULATOR%20--BY%20DEMETRIUS%20JOHNSON">
      <strong>Workout Pace Calculator</strong>
    </a> (C++): Developed a console app to compute average workout pace from repeated user-entered time inputs, supporting interactive session restarts and menu selection.
  </li>
</ul>
```

REMEMBER TO USE THE repo_links_json to map a project to the git repo link.

note file name format should be as for example like this

CIS-150_Resume_Projects.html