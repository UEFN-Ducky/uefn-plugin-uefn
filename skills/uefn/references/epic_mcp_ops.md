---
description: "Epic's official unreal-mcp rules applied to UEFN: check every unreal__* result (silent failures), save before/after bulk edits, wait for Verse builds, mind sessions, concurrency, AgentSkillToolset if present, which editor owns :8000, MCP console commands, symptom→fix table"
metadata:
  order: 1
  label: "Epic MCP safety & recovery"
  default_enabled: false
  load_condition: "An unreal__* call fails, hangs, returns OK but nothing changed, toolsets are missing, Epic calls hit the wrong island, or before a bulk (5+) Epic edit"
---

# Epic MCP — safety & recovery (Epic's official rules, UEFN edition)

Complements `epic_mcp` (flow + toolsets) and `epic_toolsets` (catalog). Adapted from
EpicGames/unreal-engine-skills-for-claude-code-plugin (MIT, Epic Games). Full Unreal Engine 5
version: `skill_read_subskill("unreal-engine", "core")`.

## Safety rules (HARD)

- **Check every result.** Epic tools (widget creation, material edits, compile, `BuildAll`, `PlaceDevice`) can return a status that flips success/failure with **no exception on the wire**. Read the response; anything not an explicit success is a stop — never report done on a silent fail.
- **Save before and after bulk changes.** MCP edits are not always undoable, especially across a Verse build boundary. 5+ assets/actors = destructive: `AssetTools.save_assets` with explicit paths first (an empty list saves every unsaved asset), then the batch, then save again. Never save the level while Verse has errors (`uefn_popups`, `verse_build_lifecycle`).
- **Wait for builds.** Calls during a Verse build, shader compile or level load hang or fail oddly. Let `BuildAll` / `workspace_compile_verse` finish first.
- **Mind the session.** Editor-only tools (asset creation especially) behave differently while a session is running. Result looks wrong → `ValkyrieToolset.SessionToolset.GetSessionStatus`; stop it if needed.
- **Concurrency.** The server accepts concurrent requests, but async tools overlap and request order is not completion order. Ducky stays stricter: one mutating `unreal__call_tool` per turn; batch inside `execute_tool_script`. Read-only `describe_toolset` calls may run in parallel.
- **Privileged script.** `ProgrammaticToolset.execute_tool_script` runs Python in the editor with full project access; keep scripts narrow. Localhost is not a trust boundary — never expose port 8000 beyond loopback.

## Project Agent Skills

Projects and plugins can register Agent Skills through `AgentSkillToolset` (`ListSkills`, `GetSkills`). It is not in the 42.40 UEFN catalog. If `unreal__list_toolsets` ever lists it, call `ListSkills` when starting unfamiliar work; a relevant project skill overrides generic defaults. Authoring: `skill_read_subskill("unreal-engine", "agent_skills")`.

## Which editor answered

Several UEFN / UE editors fight over `127.0.0.1:8000`: the second cannot bind, and the client reaches the first. Recent builds return `_meta["com.epicgames.unrealengine/instance"]` in `initialize` (`processId`, `projectName`, `projectDirectory`, `engineVersion`, …). If Epic calls hit the wrong island (unknown actors/devices), compare `projectName` with `get_project_info` and close the other editor. The port is per user in `EditorPerProjectUserSettings.ini` → `[/Script/ModelContextProtocolEngine.ModelContextProtocolSettings] ServerPortNumber=`; Ducky's nested server URL must match.

## Console commands (editor console)

| Command | Use |
|---|---|
| `ModelContextProtocol.StartServer [port]` | Start the server (pass a port if 8000 is taken). |
| `ModelContextProtocol.StopServer` | Clean restart when the registry is in a bad state. |
| `ModelContextProtocol.RefreshTools` | Re-register every toolset — a toolset is missing or a toolset plugin was just enabled. |
| `ModelContextProtocol.GenerateClientConfig <client>` | `ClaudeCode`, `Cursor`, `VSCode`, `Gemini`, `Codex`, `All`. |

Run them with `exec_console_command`.

## Symptom → fix

| Symptom | Fix |
|---|---|
| `unreal__*` missing / `list_toolsets` errors | `epic_mcp_online` is only a TCP probe. `uefn_popups`, retry once, then the closest Ducky tool and finish. Missing tools do not prove the editor is stopped. |
| Core Python toolsets (Actor / Scene / Asset) missing | `ValkyriePythonToolset.IsPythonEnabledInUEFN` → `EnablePythonInUEFN` (async), then re-list or `RefreshTools`. |
| An expected toolset missing | `ModelContextProtocol.RefreshTools`, re-list. |
| "Failed to listen on port" in the log | Another editor owns 8000 — close it, or change `ServerPortNumber` and the Ducky MCP URL. |
| Calls hang | Popup (`uefn_popups` first), Verse build, level load, or a running session. |
| Tool returns OK but nothing changed | Silent failure — read the payload; verify with `diff` / `get_properties` / `GetDeviceProperties`. |
