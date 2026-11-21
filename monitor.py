"""
PySentinel — System Health Snapshot
monitor.py — Core Monitoring Logic

This file is the heart of PySentinel.
It can be run directly in the terminal:
    python monitor.py

It is also imported by app.py (the GUI),
but it works completely on its own.

Author : You (SkillMe Python Internship — Week 1)
Version: 1.0
"""

# ─────────────────────────────────────────────────────────────
# IMPORTS
# We borrow three toolboxes from Python's standard library.
# No installation needed — they come with Python.
# ─────────────────────────────────────────────────────────────

import os           # Lets us walk folders and inspect file paths
import shutil       # Lets us read disk usage statistics
import datetime     # Lets us read the current date and time


# ─────────────────────────────────────────────────────────────
# FUNCTION 1 — disk_usage(path)
#
# PURPOSE  : Find out how much space is on the whole disk.
# PARAMETER: path — any valid folder path (e.g. "C:\\" on Windows)
# RETURNS  : A tuple of three numbers: (total_gb, used_gb, free_gb)
#
# A TUPLE is a group of values bundled together in parentheses.
# Example:  (500.0, 320.5, 179.5)
#           That means: 500 GB total, 320.5 GB used, 179.5 GB free.
# ─────────────────────────────────────────────────────────────

def disk_usage(path):
    """Return (total_gb, used_gb, free_gb) for the disk at the given path."""

    # shutil.disk_usage() is a built-in Python function.
    # It returns an object with three attributes: total, used, free — all in BYTES.
    usage = shutil.disk_usage(path)

    # Bytes are tiny units. We convert to Gigabytes by dividing by 1024 three times.
    # 1 KB = 1024 bytes
    # 1 MB = 1024 KB  = 1024 × 1024 bytes
    # 1 GB = 1024 MB  = 1024 × 1024 × 1024 bytes  = 1,073,741,824 bytes
    GB = 1024 ** 3   # 1024 to the power of 3

    # Round to 2 decimal places so the output looks clean (e.g. 476.84 GB).
    total_gb = round(usage.total / GB, 2)
    used_gb  = round(usage.used  / GB, 2)
    free_gb  = round(usage.free  / GB, 2)

    # Return all three values as a tuple.
    # The caller can unpack them like:  total, used, free = disk_usage("C:\\")
    return total_gb, used_gb, free_gb


# ─────────────────────────────────────────────────────────────
# FUNCTION 2 — folder_size(path)
#
# PURPOSE  : Calculate the total size of every file inside a folder
#            (including files inside sub-folders, and sub-sub-folders, etc.)
# PARAMETER: path — the folder path to scan
# RETURNS  : Total size in BYTES (an integer)
#
# KEY CONCEPT — os.walk()
# os.walk() travels through a folder tree.
# For each folder it visits, it gives you:
#   root   — the current folder path
#   dirs   — list of sub-folder names inside root
#   files  — list of file names inside root
# It repeats this for every sub-folder automatically.
# ─────────────────────────────────────────────────────────────

def folder_size(path):
    """Return the total size in bytes of all files inside a folder."""

    total_bytes = 0   # We start counting from zero

    # os.walk() explores the folder and every folder inside it, level by level.
    for root, dirs, files in os.walk(path):

        # For each file found in the current folder (root):
        for filename in files:

            # Build the full file path by joining the folder path + file name.
            # os.path.join() handles the slashes correctly on any OS.
            filepath = os.path.join(root, filename)

            # TRY to get the file's size.
            # Some system files are protected — accessing them causes a PermissionError.
            # We use try/except so the program does not crash on those files.
            try:
                # os.path.getsize() returns the file size in bytes.
                total_bytes += os.path.getsize(filepath)

            except (PermissionError, OSError):
                # PermissionError : we don't have access to this file — skip it.
                # OSError         : the file may have been deleted mid-scan — skip it.
                pass   # "pass" means: do nothing and continue the loop

    return total_bytes


# ─────────────────────────────────────────────────────────────
# FUNCTION 3 — largest_files(path, n)
#
# PURPOSE  : Find the N largest files inside a folder.
# PARAMETERS:
#   path — the folder to scan
#   n    — how many large files to find (we'll use 5)
# RETURNS  : A list of tuples, sorted from largest to smallest.
#            Each tuple looks like:  (size_in_bytes, full_file_path)
#            Example: [(52428800, "C:\\Videos\\movie.mp4"), ...]
#
# KEY CONCEPT — sorted() with reverse=True
# sorted() arranges items in order.
# reverse=True means largest first (descending order).
# ─────────────────────────────────────────────────────────────

def largest_files(path, n=5):
    """Return a list of the N largest (size, filepath) tuples, largest first."""

    file_list = []   # This list will collect every (size, path) pair

    for root, dirs, files in os.walk(path):
        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                size = os.path.getsize(filepath)
                # Append a tuple (size, filepath) to our list.
                file_list.append((size, filepath))

            except (PermissionError, OSError):
                pass   # Skip files we cannot access

    # Sort the list by size (the first item in each tuple) from largest to smallest.
    # key=lambda x: x[0]  means "sort by the first element of each tuple" (the size).
    # reverse=True         means largest first.
    file_list.sort(key=lambda x: x[0], reverse=True)

    # Return only the first N items (the N largest).
    # list[:n] is called "slicing" — it takes items from index 0 up to (not including) n.
    return file_list[:n]


# ─────────────────────────────────────────────────────────────
# FUNCTION 4 — human_size(num_bytes)
#
# PURPOSE  : Convert a raw byte count into a readable string.
# PARAMETER: num_bytes — an integer (e.g. 5242880)
# RETURNS  : A readable string  (e.g. "5.0 MB")
#
# KEY CONCEPT — if / elif / else
# We check which unit is appropriate and pick the right one.
# ─────────────────────────────────────────────────────────────

def human_size(num_bytes):
    """Convert bytes to a human-readable string like '5.0 MB' or '1.2 GB'."""

    # Define unit thresholds
    KB = 1024
    MB = 1024 ** 2    # 1,048,576 bytes
    GB = 1024 ** 3    # 1,073,741,824 bytes

    if num_bytes >= GB:
        # Large enough to express in GB
        return f"{num_bytes / GB:.2f} GB"

    elif num_bytes >= MB:
        # Large enough to express in MB
        return f"{num_bytes / MB:.2f} MB"

    elif num_bytes >= KB:
        # Large enough to express in KB
        return f"{num_bytes / KB:.2f} KB"

    else:
        # Tiny — just show raw bytes
        return f"{num_bytes} bytes"

    # f"{value:.2f}" means: format the value as a decimal with exactly 2 decimal places.
    # Example: f"{5.0:.2f}" → "5.00"


# ─────────────────────────────────────────────────────────────
# FUNCTION 5 — get_file_type(filepath)
#
# PURPOSE  : Identify the type of a file from its extension.
# PARAMETER: filepath — full path to the file
# RETURNS  : A readable label like "Video", "Image", "Document"
# ─────────────────────────────────────────────────────────────

def get_file_type(filepath):
    """Return a human-readable file type label based on the file extension."""

    # os.path.splitext() splits a filename into (name, extension).
    # Example: "photo.jpg"  →  ("photo", ".jpg")
    _, ext = os.path.splitext(filepath)

    # Convert to lowercase so ".JPG" and ".jpg" are treated the same.
    ext = ext.lower()

    # Map extensions to categories using a dictionary.
    # A dictionary stores key → value pairs.
    type_map = {
        # Video files
        ".mp4": "Video", ".mkv": "Video", ".avi": "Video",
        ".mov": "Video", ".wmv": "Video",
        # Image files
        ".jpg": "Image", ".jpeg": "Image", ".png": "Image",
        ".gif": "Image", ".bmp": "Image", ".svg": "Image",
        # Audio files
        ".mp3": "Audio", ".wav": "Audio", ".flac": "Audio",
        ".aac": "Audio",
        # Document files
        ".pdf": "Document", ".doc": "Document", ".docx": "Document",
        ".txt": "Document", ".xlsx": "Document", ".pptx": "Document",
        # Archive files
        ".zip": "Archive", ".rar": "Archive", ".7z": "Archive",
        ".tar": "Archive", ".gz": "Archive",
        # Code files
        ".py": "Code", ".js": "Code", ".html": "Code",
        ".css": "Code", ".json": "Code",
        # Executable files
        ".exe": "Executable", ".msi": "Executable",
    }

    # dict.get(key, default) looks up the key; if not found, returns the default.
    return type_map.get(ext, "Other")


# ─────────────────────────────────────────────────────────────
# FUNCTION 6 — generate_report(disk_path, folder_path)
#
# PURPOSE  : Build a full text report combining disk and folder info.
# PARAMETERS:
#   disk_path   — the drive to check (e.g. "C:\\")
#   folder_path — the user-selected folder to scan
# RETURNS  : A formatted multi-line string (the report text)
# ─────────────────────────────────────────────────────────────

def generate_report(disk_path, folder_path):
    """Generate and return a formatted system health report as a string."""

    # Get the current date and time.
    # datetime.datetime.now() returns a datetime object.
    # .strftime() formats it into a readable string using format codes:
    #   %Y = 4-digit year    %m = month    %d = day
    #   %H = hour (24h)      %M = minutes  %S = seconds
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    # Collect disk data
    total_gb, used_gb, free_gb = disk_usage(disk_path)
    free_pct = round((free_gb / total_gb) * 100, 1)   # Percentage free

    # Collect folder data
    f_size_bytes = folder_size(folder_path)
    f_size_human = human_size(f_size_bytes)

    # Collect largest files
    top_files = largest_files(folder_path, n=5)

    # Build the report string using a triple-quoted f-string.
    # Triple quotes (""") allow a string to span multiple lines.
    report = f"""
╔══════════════════════════════════════════════════╗
║          PYSENTINEL — SYSTEM HEALTH REPORT       ║
╚══════════════════════════════════════════════════╝

  Generated : {timestamp}

─── DISK USAGE ─────────────────────────────────────
  Drive       : {disk_path}
  Total Space : {total_gb} GB
  Used Space  : {used_gb} GB
  Free Space  : {free_gb} GB  ({free_pct}% free)

─── FOLDER ANALYSIS ────────────────────────────────
  Folder      : {folder_path}
  Total Size  : {f_size_human}

─── TOP {len(top_files)} LARGEST FILES ──────────────────────────
"""

    # Add each large file to the report
    if top_files:
        for i, (size, filepath) in enumerate(top_files, start=1):
            # enumerate(list, start=1) gives us both the index and the value.
            # i        = the rank (1, 2, 3 ...)
            # size     = file size in bytes
            # filepath = full path to the file
            fname     = os.path.basename(filepath)   # Just the filename, not the full path
            ftype     = get_file_type(filepath)
            fsize_str = human_size(size)
            report += f"  {i}. [{ftype:>10}]  {fsize_str:>10}  {fname}\n"
            report += f"     Location: {filepath}\n\n"
    else:
        report += "  No files found in this folder.\n"

    report += "════════════════════════════════════════════════════\n"
    return report


# ─────────────────────────────────────────────────────────────
# FUNCTION 7 — log_scan(disk_path, folder_path)
#
# PURPOSE  : Append a one-line summary to health_log.txt.
#            The file is created automatically if it doesn't exist.
#            Existing log entries are NEVER deleted.
# ─────────────────────────────────────────────────────────────

def log_scan(disk_path, folder_path, log_file="health_log.txt"):
    """Append one summary line to health_log.txt."""

    now       = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_gb, used_gb, free_gb = disk_usage(disk_path)
    free_pct  = round((free_gb / total_gb) * 100, 1)
    f_size    = human_size(folder_size(folder_path))

    # Build the log line
    log_line = (
        f"[{now}] "
        f"Disk: {total_gb}GB total | "
        f"Free: {free_gb}GB ({free_pct}%) | "
        f"Scanned: {folder_path} | "
        f"Folder Size: {f_size}\n"
    )

    # Open the log file in APPEND mode ("a").
    # "a" means: if the file exists, add to the end. If it doesn't exist, create it.
    # NEVER use "w" mode here — "w" would erase everything first!
    # The "encoding='utf-8'" ensures special characters are saved correctly.
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_line)


# ─────────────────────────────────────────────────────────────
# FUNCTION 8 — get_folder_from_user()
#
# PURPOSE  : Ask the user to type a folder path.
#            Validate the input. Handle errors gracefully.
# RETURNS  : A valid folder path string
# ─────────────────────────────────────────────────────────────

def get_folder_from_user():
    """Prompt the user for a folder path and validate it."""

    print("\n" + "─" * 52)
    print("  PySentinel — Folder Scanner")
    print("─" * 52)
    print("  Enter the folder path you want to scan.")
    print("  Press Enter without typing to scan the current folder.")
    print("─" * 52)

    while True:   # Keep asking until we get a valid answer
        # input() shows a prompt and waits for the user to type.
        # .strip() removes any accidental spaces at the start or end.
        user_input = input("\n  Folder path: ").strip()

        # If the user pressed Enter without typing anything:
        if user_input == "":
            # os.getcwd() returns the current working directory
            folder = os.getcwd()
            print(f"  → Using current directory: {folder}")
            return folder

        # Check whether the path actually exists on disk.
        if os.path.isdir(user_input):
            return user_input   # Valid! Return it.
        else:
            # Friendly error — no crash.
            print(f"\n  ⚠  '{user_input}' was not found or is not a folder.")
            print("     Please try again.")


# ─────────────────────────────────────────────────────────────
# MAIN BLOCK
#
# Everything inside  if __name__ == "__main__":
# only runs when you execute THIS file directly.
# It does NOT run when app.py imports monitor.py.
#
# This is a Python convention that keeps modules clean.
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":

    # ── Determine disk root automatically ──────────────────
    # On Windows: "C:\\"   On macOS/Linux: "/"
    disk_root = os.path.splitdrive(os.getcwd())[0] + "\\" or "/"

    # ── Ask user which folder to scan ──────────────────────
    folder = get_folder_from_user()

    # ── Run the scan and show the report ───────────────────
    print("\n  Scanning... please wait.")
    report = generate_report(disk_root, folder)
    print(report)

    # ── Log this scan to health_log.txt ────────────────────
    # Build the log file path next to monitor.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_path   = os.path.join(script_dir, "health_log.txt")

    log_scan(disk_root, folder, log_file=log_path)
    print(f"  ✓  Scan logged to: {log_path}\n")
