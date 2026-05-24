---
name: upesi-workflow
description: Upesi deployment workflow guidance. Use when deploying web apps, managing files, databases, or custom domains on Upesi.
---

# Upesi Deployment Workflow

You are connected to an Upesi hosting server via MCP. Use these instructions to effectively deploy and manage static web apps with optional database functionality.

## Tool Reference

All tools that operate on an app use `app` (subdomain or UUID) as parameter.

| Tool | Parameters | Notes |
|------|-----------|-------|
| `upesi_whoami` | *(none)* | Verify authentication. Call first. |
| `upesi_apps_list` | `app`? | List all apps. Optional `app` to filter by subdomain. |
| `upesi_app_create` | **`app`** | Create app. `app` = desired subdomain (permanent). |
| `upesi_app_info` | **`app`** | App details: file count, total size, URL. |
| `upesi_app_destroy` | **`app`**, **`confirm`** | Delete app + all data. `confirm` = subdomain. |
| `upesi_app_spa_enable` | **`app`** | Enable SPA fallback to `index.html` for extensionless browser routes. |
| `upesi_app_spa_disable` | **`app`** | Disable SPA fallback. |
| `upesi_files_list` | **`app`** | List files with path, size, content_type. |
| `upesi_files_upload` | **`app`**, **`path`**, `content`?, `content_base64`?, `content_type`? | Upsert file. Use `content` for text, `content_base64` for binary. |
| `upesi_files_download` | **`app`**, **`path`** | Download file content (returned as text). |
| `upesi_files_delete` | **`app`**, **`path`** | Delete file. Cannot be undone. |
| `upesi_custom_domains_list` | **`app`** | List custom domains (max 5 per app), including DNS target and status URL. |
| `upesi_custom_domains_add` | **`app`**, **`domain_name`** | Add domain. User must configure DNS CNAME to `ingress.upesi.dev`. |
| `upesi_custom_domains_remove` | **`app`**, **`domain_name`** | Remove domain. Cannot be undone. |
| `upesi_variables_list` | **`app`** | List app environment variable metadata. Secret values are never returned. |
| `upesi_variable_set` | **`app`**, **`name`**, **`value`** | Set/update an app variable. Optional `allowed_upstreams` restricts proxy use by host. |
| `upesi_variable_remove` | **`app`**, **`name`** | Remove an app variable. |
| `upesi_proxy_routes_list` | **`app`** | List app-specific proxy routes. |
| `upesi_proxy_route_set` | **`app`**, **`path`**, **`upstream`** | Set/update a same-origin proxy route. Optional `method` and `headers`. |
| `upesi_proxy_route_remove` | **`app`**, **`path`** | Remove an app-specific proxy route. |
| `upesi_db_status` | **`app`** | Collections, document counts, API key status. |
| `upesi_db_key` | **`app`** | Show/create browser API key (auto-embedded in `/_db/db.js`). Agents should prefer MCP CRUD tools for direct data work. |
| `upesi_db_key_rotate` | **`app`** | Rotate browser key. Old browser clients stop working immediately until reload. |
| `upesi_db_reset` | **`app`**, **`confirm`** | Delete ALL DB data. `confirm` must be `"yes"`. |
| `upesi_db_find` | **`app`**, **`collection`**, `filter`?, `sort`?, `limit`?, `offset`? | Query documents. Returns `{ data, total, limit, offset }`. |
| `upesi_db_get` | **`app`**, **`collection`**, **`id`** | Read one document by id. |
| `upesi_db_insert` | **`app`**, **`collection`**, **`data`** | Create one document. Pass document fields directly as `data`. |
| `upesi_db_update` | **`app`**, **`collection`**, **`id`**, **`data`** | Merge fields, preserving omitted fields. |
| `upesi_db_replace` | **`app`**, **`collection`**, **`id`**, **`data`** | Replace all user fields; omitted fields are removed. |
| `upesi_db_delete` | **`app`**, **`collection`**, **`id`** | Permanently delete one document. |
| `upesi_db_count` | **`app`**, **`collection`**, `filter`? | Count matching documents without returning them. |
| `upesi_skill` | *(none)* | These instructions. |

**Bold** = required, `?` = optional.

## Recommended Tool Order

1. `upesi_whoami` – Verify authentication
2. `upesi_apps_list` – See existing apps
3. `upesi_app_create` – Create new app (if needed)
4. `upesi_files_upload` – Deploy files (always start with `index.html`)
5. `upesi_app_info` – Verify deployment succeeded

## Best Practices

### Creating Apps
- Choose short, descriptive subdomains: `snake-game`, `my-portfolio`, `todo-app`
- Subdomains are permanent and cannot be changed after creation
- Valid format: lowercase letters, numbers, hyphens; 2-32 chars; must start/end with alphanumeric

### File Structure
Every app needs at least an `index.html` as entry point. Recommended structure:
```
index.html              # Entry point (served at root URL)
css/style.css           # Stylesheets
js/app.js               # Application logic
images/logo.png         # Static assets
404.html                # Custom error page (optional)
```

### Uploading Files
- Always upload `index.html` first – it's the entry point at the root URL
- **Text files** (HTML, CSS, JS, JSON, SVG, etc.): use `content` – pass the file content as plain string
- **Binary files** (images, fonts, etc.): use `content_base64` – pass base64-encoded content
- If both `content` and `content_base64` are provided, `content_base64` takes precedence
- Upload files one at a time for reliability and clear error handling
- After uploading, call `upesi_app_info` to verify file count and total size
- `upesi_files_upload` is an upsert: creates new files or updates existing ones
- Optional `content_type` is auto-detected from file extension; set it explicitly for ambiguous types

### File Content Encoding
- **Text files**: Pass directly via `content` – no encoding needed. **Never base64-encode text files manually.**
  - Example: `content: "<h1>Hello</h1>"`
- **Binary files**: Use the encode-files skill to generate base64, then pass via `content_base64`
  - Run: `python3 encode.py images/logo.png` → outputs JSON with `content_base64`
  - Example: `content_base64: "iVBORw0KGgo..."`
- **Batch encode**: `python3 encode.py <directory>` scans all deployable files, skips `node_modules/` and `.git/`, outputs JSON array sorted with `index.html` first

### Working with Existing Apps
- Call `upesi_files_list` to see what files are currently deployed
- Call `upesi_files_download` to read a file's content before modifying it
- Never blindly overwrite – always check the current state first

### SPA Mode
Enable SPA mode for React Router, Vue Router, Svelte, Vite, or other static apps with client-side routing:

1. `upesi_app_spa_enable(app: "my-app")`
2. Upload `index.html` and assets normally
3. Missing routes like `/dashboard/settings` fall back to `index.html`
4. Missing asset paths like `/assets/app.js` still return 404

### Custom Domains
Add up to 5 custom domains per app:
1. `upesi_custom_domains_add(app: "my-app", domain_name: "mysite.com")`
2. User configures DNS: `CNAME mysite.com -> ingress.upesi.dev`
3. Check the returned `status_url` or ask the user to run `upesi domains status mysite.com`
4. SSL is handled automatically

### Environment Variables & Proxy Routes
Use app-scoped variables for API keys that must not be exposed in browser code:

1. `upesi_variable_set(app: "my-app", name: "OPENROUTER_API_KEY", value: "sk-...", allowed_upstreams: ["openrouter.ai"])`
2. `upesi_proxy_route_set(app: "my-app", path: "/api/chat", upstream: "https://openrouter.ai/api/v1/chat/completions", method: "POST", headers: { "Authorization": "Bearer ${OPENROUTER_API_KEY}" })`
3. Frontend code calls the same-origin path, e.g. `fetch("/api/chat")`
4. Upesi injects the variable server-side and forwards the request to the upstream

For CLI-driven projects, keep declarative proxy config in the app project directory at `.upesi/proxy.json` and run `upesi proxy routes apply`. `upesi sync` also applies that local config and ignores `.upesi/` during file upload.

Values are encrypted and never returned by `upesi_variables_list`.

### Destructive Operations
- `upesi_app_destroy`: `confirm` must exactly match the app's subdomain
- `upesi_db_reset`: `confirm` must be the string `"yes"`
- `upesi_db_delete`, `upesi_db_replace`, `upesi_files_delete`, `upesi_custom_domains_remove`, `upesi_variable_remove`, and `upesi_proxy_route_remove`: no confirmation, but cannot be undone or can remove data

## UpesiDB – Built-in Document Database

Every Upesi app includes a schemaless document database. Use it to store user data, form submissions, game scores, or any structured data – directly from the browser, no backend needed.

### Setup
1. `upesi_db_key(app: "my-app")` – get or create the API key
2. Include in HTML: `<script src="/_db/db.js"></script>`
3. The JS client auto-configures with the correct API key

### JavaScript API (in-browser)

Collections are accessed as properties on `db` (not methods). All operations are async.

```javascript
const post = await db.posts.insert({ title: 'Hello', body: 'World' });   // Create
const { data, total } = await db.posts.find({ status: 'published' });     // List/Filter
const post = await db.posts.findOne(42);                                   // Get by ID
await db.posts.update(42, { title: 'New' });                              // Merge fields
await db.posts.replace(42, { title: 'New' });                             // Replace all fields
await db.posts.delete(42);                                                 // Delete
const { count } = await db.posts.count({ status: 'draft' });              // Count
```

**Full API reference:** Use the `upesidb-js-api` skill for complete documentation with all method signatures, filter operators, sorting, pagination, and error handling.

### MCP API (agent-side)

Use MCP CRUD tools when the agent needs to inspect or modify data directly. These tools use owner auth and do not require handling the browser API key.

```javascript
upesi_db_insert(app: "my-app", collection: "posts", data: { title: "Hello", status: "draft" });
upesi_db_find(app: "my-app", collection: "posts", filter: { status: "draft" }, sort: { created_at: -1 }, limit: 10);
upesi_db_get(app: "my-app", collection: "posts", id: "42");
upesi_db_update(app: "my-app", collection: "posts", id: "42", data: { status: "published" });
upesi_db_replace(app: "my-app", collection: "posts", id: "42", data: { title: "Only this remains" });
upesi_db_delete(app: "my-app", collection: "posts", id: "42");
upesi_db_count(app: "my-app", collection: "posts", filter: { status: "published" });
```

Collection names must match `^[a-z][a-z0-9_]{0,62}$`. `upesi_db_update` merges and preserves omitted fields; `upesi_db_replace` removes omitted user fields.

### Filter Operators

`$gt`, `$gte`, `$lt`, `$lte`, `$ne`, `$in`, `$or` — used in `find()` and `count()`:

```javascript
await db.scores.find({ score: { $gt: 100 } });
await db.items.find({ status: { $in: ['active', 'pending'] } });
await db.posts.find({ status: 'published' }, { sort: { created_at: -1 }, limit: 10 });
```

## Error Handling

- **"App not found"**: Call `upesi_apps_list` to verify the app exists and check for typos
- **"unauthorized"**: The OAuth session may have expired – the user needs to re-authenticate
- **"Confirmation mismatch"**: For `app_destroy`, `confirm` must match the exact subdomain
- **Validation errors**: The error message describes what's wrong – follow its guidance

## Common Workflows

### Deploy a New Static Site
```
1. upesi_app_create(app: "my-site")
2. upesi_files_upload(app: "my-site", path: "index.html", content: "<html>...</html>")
3. upesi_files_upload(app: "my-site", path: "css/style.css", content: "body { ... }")
4. upesi_files_upload(app: "my-site", path: "js/app.js", content: "console.log('hi')")
5. upesi_app_info(app: "my-site")  # verify: check file_count and total_bytes
```

### Deploy a Client-Routed SPA
```
1. upesi_app_create(app: "my-spa")
2. upesi_app_spa_enable(app: "my-spa")
3. upesi_files_upload(app: "my-spa", path: "index.html", content: "<html>...</html>")
4. upesi_files_upload(app: "my-spa", path: "assets/app.js", content: "...")
5. upesi_app_info(app: "my-spa")  # verify: spa_mode should be true
```

### Update an Existing Site
```
1. upesi_files_list(app: "my-site")           # see current files
2. upesi_files_download(app: "my-site", path: "index.html")  # read current content
3. # modify content locally
4. upesi_files_upload(app: "my-site", path: "index.html", content: "<html>...</html>")
```

### Deploy a Site with Database
```
1. upesi_app_create(app: "my-app")
2. upesi_db_key(app: "my-app")               # creates API key on first call
3. upesi_files_upload(app: "my-app", path: "index.html", content: "<html>...<script src='/_db/db.js'></script>...</html>")
4. upesi_app_info(app: "my-app")
5. upesi_db_status(app: "my-app")             # verify DB is active
```

### Inspect or Seed Database Data
```
1. upesi_db_status(app: "my-app")             # see collections and counts
2. upesi_db_insert(app: "my-app", collection: "posts", data: { title: "Hello", status: "draft" })
3. upesi_db_find(app: "my-app", collection: "posts", filter: { status: "draft" })
4. upesi_db_update(app: "my-app", collection: "posts", id: "<id>", data: { status: "published" })
5. upesi_db_count(app: "my-app", collection: "posts", filter: { status: "published" })
```

### Add Custom Domain
```
1. upesi_custom_domains_add(app: "my-site", domain_name: "mysite.com")
2. Inform user: set DNS CNAME record mysite.com -> ingress.upesi.dev
3. upesi_custom_domains_list(app: "my-site")  # verify domain was added
```

### Clean Up / Delete
```
1. upesi_files_delete(app: "my-site", path: "old-page.html")  # remove single file
2. upesi_custom_domains_remove(app: "my-site", domain_name: "mysite.com")  # remove domain
3. upesi_db_reset(app: "my-site", confirm: "yes")           # delete all DB data
4. upesi_app_destroy(app: "my-site", confirm: "my-site")    # delete entire app
```

## Limits

| Resource | Limit |
|----------|-------|
| File size | 10 MB |
| Files per app | 100 |
| Total storage per app | 50 MB |
| Path depth | 5 directory levels |
| Custom domains per app | 5 |
| DB collections per app | 100 |
| DB documents per collection | 100,000 |
| DB document size | 1 MB |
