---
name: encode-files
description: Encode binary files (images, fonts) to base64 for Upesi upload. Text files (HTML, CSS, JS) don't need encoding – use the `content` parameter directly.
---

# Encode Files for Upesi Upload

## When to Use This Skill

- **Text files** (HTML, CSS, JS, JSON, SVG, XML, TXT, MD): **No encoding needed.** Pass content directly via the `content` parameter of `upesi_files_upload`.
- **Binary files** (images, fonts, etc.): **Must be base64-encoded.** Use the Python script below to encode them, then pass via `content_base64`.

## Quick Reference

```
Text file  → upesi_files_upload(app: "x", path: "index.html", content: "<html>...</html>")
Binary file → upesi_files_upload(app: "x", path: "logo.png", content_base64: "<base64 from script>")
```

## Encoding Binary Files

Write and run this Python script to encode binary files:

```bash
python3 -c '
import base64, json, mimetypes, os, sys

SKIP_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "venv"}
DEPLOY_EXT = {
    ".html", ".css", ".js", ".json", ".svg", ".png", ".jpg", ".jpeg",
    ".gif", ".ico", ".webp", ".woff", ".woff2", ".ttf", ".txt", ".xml",
    ".webmanifest", ".map", ".otf", ".eot", ".md",
}
MAX = 10 * 1024 * 1024

def enc(fp, base=None):
    if os.path.getsize(fp) > MAX: return None
    rel = (os.path.relpath(fp, base) if base else os.path.basename(fp)).replace(os.sep, "/")
    with open(fp, "rb") as f: data = f.read()
    mt = mimetypes.guess_type(fp)[0] or "application/octet-stream"
    return {"path": rel, "content_base64": base64.standard_b64encode(data).decode(), "content_type": mt}

def scan(d):
    r = []
    for root, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for f in sorted(files):
            if os.path.splitext(f)[1].lower() in DEPLOY_EXT:
                e = enc(os.path.join(root, f), d)
                if e: r.append(e)
    r.sort(key=lambda e: (0 if e["path"] == "index.html" else 1, e["path"]))
    return r

targets = sys.argv[1:]
if not targets: print("Usage: python3 encode.py <file-or-dir> [...]", file=sys.stderr); sys.exit(1)
if len(targets) == 1 and os.path.isdir(targets[0]):
    res = scan(targets[0])
else:
    res = [e for t in targets if os.path.isfile(t) for e in [enc(t)] if e]
if not res: print("No files found.", file=sys.stderr); sys.exit(1)
print(json.dumps(res if len(res) > 1 else res[0], indent=2))
' "$@"
```

### Usage Examples

```bash
# Encode a single image
python3 encode.py logo.png

# Encode all files in a directory
python3 encode.py .

# Encode specific binary files
python3 encode.py images/hero.jpg fonts/inter.woff2
```

### Output Format

```json
{
  "path": "images/logo.png",
  "content_base64": "iVBORw0KGgo...",
  "content_type": "image/png"
}
```

Use the `content_base64` and `path` values directly in `upesi_files_upload`.

## Recommended Workflow

1. **Text files** – upload directly with `content`:
   ```
   upesi_files_upload(app: "my-app", path: "index.html", content: "<html>...</html>")
   ```

2. **Binary files** – encode first, then upload with `content_base64`:
   ```bash
   python3 encode.py images/logo.png
   ```
   ```
   upesi_files_upload(app: "my-app", path: "images/logo.png", content_base64: "iVBORw0KGgo...")
   ```

3. **Batch deploy** – encode entire directory, upload text files with `content`, binary files with `content_base64`:
   ```bash
   python3 encode.py .
   ```

## Important

- **Never base64-encode text files manually** – use `content` instead, it's faster and less error-prone
- The script skips `node_modules/`, `.git/`, and files over 10 MB
- `index.html` is sorted first in directory scans
- Standard base64 encoding is used (not URL-safe variant)
