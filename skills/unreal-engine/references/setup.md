---
description: "Unreal Engine unreal-mcp first-time setup: enable ModelContextProtocol + AllToolsets in .uproject, bAutoStartServer ini, port/url overrides, generate .mcp.json (source vs launcher build), install unreal_mcp_proxy, one port per editor, verify"
metadata:
  order: 1
  label: "First-time MCP server setup"
  default_enabled: false
  load_condition: "Setting up Epic's unreal-mcp server for a UE5 project the first time, .mcp.json, the proxy, or several editors on one PC"
---

# First-time MCP server setup (Unreal Engine)

Steps 1–3 = direct HTTP access. Step 4 adds a proxy that keeps the client session open while Unreal is down. Walk them in order; never edit the user's `.uproject` silently — confirm the path first.

## 1. Enable the plugins in the `.uproject`

Both are required: `ModelContextProtocol` (server + transport) and `AllToolsets` (the tools). With only `ModelContextProtocol` the server starts but exposes **no tools**.

```json
{ "Name": "ModelContextProtocol", "Enabled": true },
{ "Name": "AllToolsets", "Enabled": true }
```

Create the `Plugins` array if missing; flip `"Enabled": false` to `true`. `AllToolsets` is an editor-only aggregator with `EnabledByDefault` off, so enable it explicitly. For a subset, enable specific toolset plugins instead of `AllToolsets`.

## 2. Auto-start

Default: the server is stopped. Manual per session: console `ModelContextProtocol.StartServer`.
Persistent: add to `<Project>/Saved/Config/<Platform>Editor/EditorPerProjectUserSettings.ini` (per-user, not source-controlled — the file Editor Preferences writes):

```ini
[/Script/ModelContextProtocolEngine.ModelContextProtocolSettings]
bAutoStartServer=True
; optional overrides
ServerPortNumber=8000
ServerUrlPath=/mcp
```

Command-line alternative: `-ModelContextProtocolStartServer` (+ `-ModelContextProtocolPort=<port>`). Prefer the ini; it persists.

## 3. Generate `.mcp.json`

The editor never writes it on its own.

- **From a running editor (preferred):** `ModelContextProtocol.GenerateClientConfig ClaudeCode` (or `All` → `ClaudeCode`, `Cursor`, `VSCode`, `Gemini`, `Codex`). Re-running merges, so it is safe after port/URL changes. Codex uses TOML and the writer refuses to overwrite an existing `.codex/config.toml` — edit that one by hand.
- Destination: **source build** (repo contains `Engine/`) → workspace root next to `Engine/`, not next to the `.uproject`. **Installed/launcher build** → next to the `.uproject`.
- **Hand-written** (fresh bootstrap without the editor), at the location above:

```json
{ "mcpServers": { "unreal-mcp": { "type": "http", "url": "http://127.0.0.1:8000/mcp" } } }
```

Adjust the URL if step 2 overrode port or path. In Ducky: Settings → MCPs → the nested server, same URL.

## 4. Optional: the proxy

Keeps the client session alive across editor restarts (the editor must still run for live calls). Present only if `Engine/Plugins/Experimental/ModelContextProtocol/Extras/Proxy` exists; otherwise stay on HTTP.

| Platform | Binary under `Extras/Proxy` |
|---|---|
| Windows x64 | `Bin/Win64/unreal_mcp_proxy.exe` |
| macOS arm64 | `Bin/Mac/unreal_mcp_proxy` |
| Linux x64 | `Bin/Linux/unreal_mcp_proxy` |
| Linux arm64 | `Bin/LinuxArm64/unreal_mcp_proxy` |

Generate `.mcp.json` first (step 3), then from `Extras/Proxy`:

```powershell
.\Bin\Win64\unreal_mcp_proxy.exe --mcp-json "C:\path\to\.mcp.json" install
```

```bash
./Bin/Mac/unreal_mcp_proxy --mcp-json "/path/to/.mcp.json" install   # Linux: Bin/Linux or Bin/LinuxArm64
```

An explicit `--mcp-json` also supports projects outside the engine tree. `uninstall` restores the HTTP entry (reload the client after). The installer replaces the HTTP entry with a STDIO `unreal-mcp-proxy` entry and keeps the original under `_upstreamEntry`. Configure ONE Unreal connection — never proxy + a duplicate HTTP entry. Restart the client once after install; later editor shutdowns need no proxy restart. If an editor integration rewrites `.mcp.json` automatically, disable its client-config writes. The catalog cache lives in the OS user cache dir, scoped by config path, proxy path, engine build identity and client protocol version; it is not a fixed catalog. Details: the engine's `Extras/Proxy/README.md`.

## 5. Several editors at once

Each editor serves on `ServerPortNumber` (8000). A second editor cannot bind it, and a client pointed there reaches the first editor.

1. Pick a fixed port per workspace (8100, 8101, …) and keep it — never rely on "next free port".
2. Set `ServerPortNumber` in that project's ini, or `-ModelContextProtocolPort=<port>` at launch.
3. Point that workspace's `.mcp.json` at the same port and install the proxy into it.
4. Start each client session from its own workspace.

Which editor answered: `operations` → Identify the editor.

## Verify

- The Output Log shows MCP server startup.
- `list_toolsets` succeeds.
- The client lists `unreal-mcp` (or `unreal-mcp-proxy`) as connected.

A connected proxy or visible cached tools do not prove reachability — confirm with a read-only tool call. Failures → `operations`.
