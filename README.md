# ⚡ PySentinel — System Health Snapshot

> A Python-powered desktop application for monitoring your computer's storage health.
> Built as the **Week 1 assignment** for the **SkillMe Python Technical Internship**.

**Current version: 2.0.0** — Premium UI/UX upgrade applied. All backend functionality preserved.

---

## 📋 What It Does

PySentinel gives you a clear, real-time picture of your computer's storage:

- 📊 **Disk usage** — total, used, and free space in GB
- 📁 **Folder scanner** — calculates the total size of any folder you choose
- 🏆 **Top 5 largest files** — finds the biggest files with name, size, type, and location
- 📋 **System health report** — timestamped, human-readable report
- 🕒 **Scan history** — every scan is logged permanently to `health_log.txt`
- 🛡️ **Error handling** — handles permission errors and missing paths gracefully
- 🎨 **Modern GUI** — clean white and orange interface built with `tkinter`

---

## 🖥️ Screenshots

> Run the application and take screenshots. Place them in the `screenshots/` folder.

---

## 🚀 Getting Started

### Requirements

- Python **3.10 or newer**
- No additional packages needed — everything uses Python's standard library

### Check your Python version

```powershell
python --version
```

You should see something like `Python 3.12.x`. If not, download Python from [python.org](https://www.python.org).

### Run the application

**Option A — Graphical interface (recommended):**

```powershell
cd PySentinel
python app.py
```

**Option B — Terminal only (no GUI):**

```powershell
cd PySentinel
python monitor.py
```

The terminal version will ask you which folder to scan and print a report directly.

---

## 📂 Project Structure

```
PySentinel/
│
├── monitor.py          ← Core monitoring logic (runs independently)
├── app.py              ← Graphical User Interface (imports monitor.py)
├── health_log.txt      ← Auto-created on first scan; never erased
├── requirements.txt    ← Lists the standard-library modules used
├── README.md           ← This file
│
├── assets/             ← Application assets (icons, etc.)
└── screenshots/        ← Add screenshots here for your submission
```

### Key Design Principle

`monitor.py` and `app.py` are intentionally **separate files**.

- `monitor.py` does all the real work (disk stats, folder scanning, logging).
- `app.py` only displays those results in the graphical interface.
- You can run `monitor.py` entirely on its own — the GUI is optional.

---

## 🧰 Core Functions (monitor.py)

| Function | Purpose | Returns |
|---|---|---|
| `disk_usage(path)` | Reads total, used, and free disk space | `(total_gb, used_gb, free_gb)` |
| `folder_size(path)` | Calculates the combined size of all files in a folder | Size in bytes |
| `largest_files(path, n)` | Finds the N largest files, sorted by size | List of `(size, filepath)` tuples |
| `human_size(num_bytes)` | Converts bytes to KB, MB, or GB | Readable string like `"5.00 MB"` |
| `generate_report(disk, folder)` | Builds a timestamped text report | Formatted string |
| `log_scan(disk, folder, log_file)` | Appends one summary line to `health_log.txt` | Nothing (writes to file) |
| `get_folder_from_user()` | Asks for a folder path, validates it | Valid folder path string |
| `get_file_type(filepath)` | Identifies file type from extension | Label like `"Video"`, `"Image"` |

---

## 🎨 Interface Overview

### Sidebar Navigation
| Section | What You See |
|---|---|
| Dashboard | 4 metric cards + disk progress bar + folder analysis |
| Storage Analysis | Detailed drive statistics + visual storage bar + health tips |
| Largest Files | Table of the 5 largest files with size, type, and location |
| Scan History | Full log of every previous scan |
| About | Project information and SkillMe details |

### How to Use
1. Launch `app.py`
2. Click **🔍 Scan Folder** in the top-right
3. Choose any folder from the dialog
4. All pages update automatically with real data
5. Navigate using the left sidebar

---

## 🧪 Test Results

All 31 automated tests pass:

| Test Scenario | Result |
|---|---|
| Normal folder scanning | ✅ PASS |
| Empty folder | ✅ PASS |
| Non-existent folder path | ✅ PASS |
| Permission-restricted files (System32) | ✅ PASS |
| `human_size()` with 7 edge cases | ✅ PASS (7/7) |
| Log file preservation (3 consecutive runs) | ✅ PASS |
| File type detection (9 types including uppercase) | ✅ PASS (9/9) |
| `disk_usage()` accuracy (used + free ≈ total) | ✅ PASS |

---

## 📚 Python Concepts Used

This project demonstrates the following Python fundamentals:

| Concept | Where Used |
|---|---|
| `import` | Importing `os`, `shutil`, `datetime`, `tkinter` |
| `def` / functions | All 8 functions in `monitor.py` |
| Return values & tuples | `disk_usage()` returns `(total, used, free)` |
| `for` loops | File walking in `folder_size()` and `largest_files()` |
| `try` / `except` | Handling `PermissionError` and `OSError` |
| `os.walk()` | Recursively exploring folder trees |
| `sorted()` / `lambda` | Ranking files by size |
| `datetime` | Timestamps in reports and log entries |
| File I/O (`open`, `"a"`) | Appending to `health_log.txt` |
| f-strings | Formatting readable output |
| Dictionaries | File type mapping in `get_file_type()` |
| Classes | `PySentinelApp` and `ScrollableFrame` in `app.py` |
| `threading` | Background scanning to keep the GUI responsive |
| `tkinter` | Entire graphical interface |

---

## 📝 health_log.txt Format

Each line looks like this:

```
[2026-11-21 21:57:15] Disk: 475.83GB total | Free: 390.55GB (82.1%) | Scanned: C:\Users\HP\Documents | Folder Size: 1.24 GB
```

- Lines are **always appended** — never deleted or overwritten
- One line per scan execution
- The file is created automatically on the first scan

---

## ⚠️ Important Notes

- PySentinel **never deletes, moves or modifies** any of your files
- It **only reads** file sizes and paths — your data is completely safe
- It does **not** scan your entire computer automatically
- You choose exactly which folder to scan each time

---

## 👨‍💻 About the Project

| Detail | Value |
|---|---|
| **Program** | SkillMe Python Technical Internship |
| **Week** | 1 |
| **Assignment** | System Health Snapshot |
| **Language** | Python 3.10+ |
| **Dependencies** | None (standard library only) |
| **Version** | 2.0.0 (Premium UI/UX) |

---

*Built with Python's standard library. No external packages required.*
