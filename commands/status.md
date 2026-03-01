# Upesi App Status

Show comprehensive status information for an Upesi app.

Every Upesi MCP tool operates on an app identified by its subdomain (e.g. `my-site`). Ask the user which app they want to inspect.

## Instructions

1. **Determine app**: Ask the user for the subdomain. If unsure, call `upesi_apps_list` to show their existing apps.

2. **Gather information** by calling these tools with the subdomain as `app` parameter:
   - `upesi_app_info(app: "<subdomain>")` – App details (subdomain, UUID, file count, total size, URL)
   - `upesi_files_list(app: "<subdomain>")` – All deployed files with sizes
   - `upesi_custom_domains_list(app: "<subdomain>")` – Custom domains configured
   - `upesi_db_status(app: "<subdomain>")` – Database collections and document counts

3. **Display a summary**:

```
App: {subdomain}
URL: https://{subdomain}.upesi.dev
UUID: {uuid}

Files: {count} ({total_size} bytes)
  - index.html (1.2 KB)
  - css/style.css (3.4 KB)
  - ...

Custom Domains: {count}
  - mysite.com
  - ...

Database:
  Collections: {count}
  - todos: 42 documents
  - users: 5 documents
  API Key: {exists? "active" : "not created"}
```

## Important

- The `app` parameter (subdomain or UUID) is required for all tools
- All tools used here are read-only and safe to call at any time
- If any tool returns an error, display what information was gathered and note what failed
