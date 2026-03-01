# Deploy to Upesi

Deploy local files to an Upesi app. Reads files from the current directory, base64-encodes them, and uploads via MCP.

Every Upesi MCP tool operates on an app identified by its subdomain (e.g. `my-site`). The user must either already have an app or create one first.

## Instructions

1. **Check authentication**: Call `upesi_whoami` to verify you're logged in.

2. **Ensure an app exists**: Ask the user for the target subdomain.
   - If they don't have one yet, ask for a subdomain and call `upesi_app_create`.
   - If unsure, call `upesi_apps_list` to show their existing apps.

3. **Encode files**: Use the helper script to scan and base64-encode all deployable files:
   ```bash
   python3 scripts/encode.py .
   ```
   This outputs JSON with `path`, `content_base64`, and `content_type` for each file. It automatically skips `node_modules/`, `.git/`, non-deployable extensions, and files over 10 MB. `index.html` is sorted first.

   For individual files: `python3 scripts/encode.py index.html css/style.css`

4. **Show deployment plan**: List all files from the encode output with their sizes. Ask user to confirm before uploading.

5. **Upload files**: For each entry from the encode output, call:
   ```
   upesi_files_upload(app: "<subdomain>", path: "<path>", content_base64: "<content_base64>")
   ```
   Upload `index.html` first (the script already sorts it first).

6. **Verify deployment**: Call `upesi_app_info(app: "<subdomain>")` to confirm file count and total size. Display the live URL (`<subdomain>.upesi.dev`).

## Important

- The `app` parameter (subdomain or UUID) is required for all file operations
- Maximum 100 files per app, 10 MB per file, 50 MB total
- Paths must be relative with max 5 directory levels
- Binary files (images, fonts) must also be base64-encoded
- Use standard base64 encoding, not URL-safe variant
