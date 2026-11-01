---
description: "unreal-mcp console commands (StartServer/StopServer/RefreshTools/GenerateClientConfig), bEnableToolSearch mode, proxy recovery, identifying which editor answered (instance metadata, PID), symptom→fix matrix (missing tools, port in use, missing toolset, hangs, empty docked context)"
metadata:
  order: 2
  label: "Operations, recovery, troubleshooting"
  default_enabled: false
  load_condition: "Unreal MCP tools missing, port in use, stale tool registry, proxy problems, several editors, or calls hang/fail"
---

# Operations: console commands, settings, recovery

Read when tools are missing, the port collides, the registry is stale, or you need non-default config.

## Console commands (editor console `~`)

| Command | Use |
|---|---|
| `ModelContextProtocol.StartServer [port]` | Start the server; pass a port if 8000 is taken. |
| `ModelContextProtocol.StopServer` | Stop it — clean restart when the registry is in a bad state. |
| `ModelContextProtocol.RefreshTools` | Re-register every toolset — run after enabling a new toolset plugin. |
| `ModelContextProtocol.GenerateClientConfig <client>` | Regenerate client config: `ClaudeCode`, `Cursor`, `VSCode`, `Gemini`, `Codex`, `All`. |

## Tool-search mode

`bEnableToolSearch` on `UModelContextProtocolSettings` (default `true`):

- `True`: `tools/list` returns only `list_toolsets`, `describe_toolset`, `call_tool`; toolset tools are dispatched server-side and the catalog never changes mid-session (warm prompt cache).
- `False`: every toolset tool is registered as a native MCP tool at startup (used by the hash-mapping commandlet).

```ini
[/Script/ModelContextProtocolEngine.ModelContextProtocolSettings]
bEnableToolSearch=False
```

## Proxy recovery

The client connects to `unreal-mcp-proxy`; do not add a second direct connection during recovery.

- `unreal_mcp_status` = does the proxy hold an initialized upstream session. It does not test reachability.
- Visible tools can come from a stored catalog — verify with a read-only call.
- No stored catalog and no upstream session → only `unreal_mcp_status` is exposed. After recovery the proxy sends `notifications/tools/list_changed`; clients must refetch `tools/list`. A client that ignores it keeps the status-only or older catalog → use the client's reconnect/reload action, else restart the client (a client limitation, not normal recovery).
- Killing the proxy closes the client's STDIO (`Transport closed`) → the client must reconnect; starting an unrelated proxy cannot repair it. Ask before stopping active proxies.
- Still failing: the editor's MCP startup log, the configured endpoint, proxy stderr. With several editors, find which process owns the configured port — a running editor alone does not prove the proxy targets it. Follow the recorded `.mcp.json` entry and the engine's `Extras/Proxy/README.md` for transport limits.

## Identify the editor

With several editors running, confirm which one answers before changing anything.

- Recent builds include instance metadata in the `initialize` result (and in `server/discover` on protocol `2026-07-28`) under `_meta["com.epicgames.unrealengine/instance"]`: `processId`, `engineVersion`, `engineBranch`, `engineChangelist`, `projectName`, `engineDirectory`, `projectDirectory`, `projectFile`. Compare `projectDirectory` / `engineDirectory` with the expected workspace.
- That checks the port, not your session: a client with an older config can reach a different editor. If `execute_python` exists, run `import os; print(os.getpid())` once and compare with `processId`.
- No metadata → find the process that owns the port and check its executable path.

## Troubleshooting matrix

| Symptom | Fix |
|---|---|
| Unreal tools missing / `list_toolsets` errors | Check both `unreal-mcp` and `unreal-mcp-proxy` in the client config, the editor's MCP startup log, the endpoint. Proxy → recovery above before concluding the editor is stopped. |
| Editor logs "Failed to listen on port" | Another process holds it. Change `ServerPortNumber` in `EditorPerProjectUserSettings.ini` (see `setup`) or `-ModelContextProtocolPort=<port>`; restart the editor; re-run `GenerateClientConfig ClaudeCode`. Several editors → one port each (`setup` step 5). |
| Expected toolset (e.g. `NiagaraTools`) missing | `ModelContextProtocol.RefreshTools`; still missing → its plugin is not enabled in the `.uproject`. |
| Server up but zero tools | `AllToolsets` (or the specific toolset plugins) not enabled. |
| Calls hang / error | Editor compiling, loading a level, or in PIE. Wait and retry. Long C++ compiles → `LiveCodingToolset.CompileLiveCoding` (returns when done). |
| `AIAssistantToolset.GetDockedContext` empty | The assistant tab must be docked inside an asset editor (Blueprint, Material, …). |
| Concurrent calls conflict | Serialize dependent calls and same-state mutations; parallel only for independent, overlap-safe work. |
