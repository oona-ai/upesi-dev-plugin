# Deploy to Upesi

Deploy local files to an Upesi app. Reads files from the current directory and uploads via MCP.

Every Upesi MCP tool operates on an app identified by its subdomain (e.g. `my-site`). The user must either already have an app or create one first.

## Instructions

1. **Check authentication**: Call `upesi_whoami` to verify you're logged in.

2. **Ensure an app exists**: Ask the user for the target subdomain.
   - If they don't have one yet, ask for a subdomain and call `upesi_app_create`.
   - If unsure, call `upesi_apps_list` to show their existing apps.

3. **Scan files**: List all deployable files in the current directory. Separate them into text files (HTML, CSS, JS, JSON, SVG, XML, TXT) and binary files (images, fonts).

4. **Show deployment plan**: List all files with their sizes. Ask user to confirm before uploading.

5. **Upload text files** directly with `content`:
   ```
   upesi_files_upload(app: "<subdomain>", path: "index.html", content: "<file content>")
   ```
   Upload `index.html` first.

6. **Upload binary files** using the encode-files skill:
   - Use the Python encode script from the encode-files skill to generate base64
   - Then upload with `content_base64`:
   ```
   upesi_files_upload(app: "<subdomain>", path: "images/logo.png", content_base64: "<base64>")
   ```

7. **Verify deployment**: Call `upesi_app_info(app: "<subdomain>")` to confirm file count and total size. Display the live URL (`<subdomain>.upesi.dev`).

## Important

- The `app` parameter (subdomain or UUID) is required for all file operations
- Maximum 100 files per app, 10 MB per file, 50 MB total
- Paths must be relative with max 5 directory levels
- **Never base64-encode text files manually** – use `content` instead
- For binary files, use the encode-files skill to generate base64
