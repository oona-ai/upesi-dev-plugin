# Upesi Plugin for Claude Code

Deploy and manage static web apps on [Upesi](https://www.upesi.dev) directly from Claude Code.

## Install

### Via Marketplace (Claude Code CLI)
```bash
/plugin marketplace add oona-ai/upesi-dev-plugin
/plugin install upesi@upesi-marketplace
```

### Via Connector (Claude Desktop)
Settings > Connectors > `https://api.upesi.dev/mcp`

### Direct Plugin (Claude Code CLI)
```bash
claude --plugin-dir /path/to/upesi-dev-plugin
```

## What's Included

- **MCP Server** (17 tools) — app management, file operations, databases, custom domains
- **Skill** — deployment workflow guide with all tool parameters
- **Commands** — `/upesi:deploy`, `/upesi:status`
- **Agent** — `web-deployer` for automated deployments
- **Script** — `scripts/encode.py` for batch base64 file encoding

## MCP Tools

| Tool | Description |
|------|-------------|
| `upesi_whoami` | Show current user info |
| `upesi_apps_list` | List all apps |
| `upesi_app_create` | Create a new app |
| `upesi_app_info` | Get app details |
| `upesi_app_destroy` | Delete an app |
| `upesi_files_list` | List files in an app |
| `upesi_files_upload` | Upload files (base64) |
| `upesi_files_download` | Download a file |
| `upesi_files_delete` | Delete a file |
| `upesi_custom_domains_list` | List custom domains |
| `upesi_custom_domains_add` | Add a custom domain |
| `upesi_custom_domains_remove` | Remove a custom domain |
| `upesi_db_status` | Show database status |
| `upesi_db_reset` | Reset database |
| `upesi_db_key` | Show API key |
| `upesi_db_key_rotate` | Rotate API key |
| `upesi_skill` | Get the complete deployment guide |

## Authentication

OAuth 2.0 with PKCE. When connecting via Claude Desktop or Claude Code, authentication is handled automatically.
