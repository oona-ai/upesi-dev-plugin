#!/usr/bin/env python3
"""Encode files to base64 JSON for upesi_files_upload.

Usage:
  python3 encode.py <file>              # Single file
  python3 encode.py <file1> <file2> ... # Multiple files
  python3 encode.py <directory>         # All deployable files in directory

Output (single file):
  {"path": "index.html", "content_base64": "PGh0bWw+...", "content_type": "text/html"}

Output (multiple files):
  [{"path": "index.html", ...}, {"path": "css/style.css", ...}]

The output can be used directly as arguments to upesi_files_upload.
"""

import base64
import json
import mimetypes
import os
import sys

DEPLOYABLE_EXTENSIONS = {
    ".html", ".css", ".js", ".json", ".svg", ".png", ".jpg", ".jpeg",
    ".gif", ".ico", ".webp", ".woff", ".woff2", ".ttf", ".txt", ".xml",
    ".webmanifest", ".map", ".otf", ".eot",
}

SKIP_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "venv"}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def detect_content_type(path):
    mt, _ = mimetypes.guess_type(path)
    return mt or "application/octet-stream"


def encode_file(filepath, base_dir=None):
    size = os.path.getsize(filepath)
    if size > MAX_FILE_SIZE:
        print(f"SKIP {filepath}: {size} bytes exceeds 10 MB limit", file=sys.stderr)
        return None

    if base_dir:
        rel = os.path.relpath(filepath, base_dir)
    else:
        rel = os.path.basename(filepath)

    # Normalize to forward slashes
    rel = rel.replace(os.sep, "/")

    with open(filepath, "rb") as f:
        content = f.read()

    return {
        "path": rel,
        "content_base64": base64.standard_b64encode(content).decode("ascii"),
        "content_type": detect_content_type(filepath),
    }


def scan_directory(directory):
    results = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in sorted(files):
            _, ext = os.path.splitext(name)
            if ext.lower() not in DEPLOYABLE_EXTENSIONS:
                continue
            filepath = os.path.join(root, name)
            entry = encode_file(filepath, base_dir=directory)
            if entry:
                results.append(entry)
    # index.html first
    results.sort(key=lambda e: (0 if e["path"] == "index.html" else 1, e["path"]))
    return results


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    targets = sys.argv[1:]

    # Single directory
    if len(targets) == 1 and os.path.isdir(targets[0]):
        results = scan_directory(targets[0])
        if not results:
            print("No deployable files found.", file=sys.stderr)
            sys.exit(1)
        print(json.dumps(results, indent=2))
        return

    # One or more files
    results = []
    for target in targets:
        if not os.path.isfile(target):
            print(f"SKIP {target}: not a file", file=sys.stderr)
            continue
        entry = encode_file(target)
        if entry:
            results.append(entry)

    if not results:
        print("No files encoded.", file=sys.stderr)
        sys.exit(1)

    if len(results) == 1:
        print(json.dumps(results[0], indent=2))
    else:
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
