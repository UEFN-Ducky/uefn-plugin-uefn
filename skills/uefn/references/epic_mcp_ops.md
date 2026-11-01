---
description: "Epic's official unreal-mcp rules applied to UEFN: check every unreal__* result (silent failures), save before/after bulk edits, wait for Verse builds, mind sessions, concurrency, Exec Python vs programmatic toolset (43.00), classic device options, AgentSkillToolset, which editor owns :8000, MCP console commands, symptom→fix table"
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
- **Save before and after bulk changes.** MCP edits are not always undoable, especially across a Verse build boundary. 5+ assets/actors = destructive: `EditorToolset.AssetToolset.SaveAsset(assetPath)` for each touched asset first (actors: `LevelToolset.SaveActor`), then the batch, then save again. Never save the level while Verse has errors (`uefn_popups`, `verse_build_lifecycle`).
- **Wait for builds.** Calls during a Verse build, shader compile or level load hang or fail oddly. Let `BuildAll` / `workspace_compile_verse` finish first.
- **Mind the session.** Editor-only tools (asset creation especially) behave differently while a session is running. Result looks wrong → `ValkyrieFortniteToolset.SessionToolset.GetSessionStatus`; stop it if needed.
- **Concurrency.** The server accepts concurrent requests, but async tools overlap and request order is not completion order. Ducky stays stricter: one mutating `unreal__call_tool` per turn; batch inside `execute_tool_script`. Read-only `describe_toolset` calls may run in parallel.
- **Privileged script.** `ProgrammaticToolset.execute_tool_script` runs Python in the editor with full project access; keep scripts narrow. Localhost is not a trust boundary — never expose port 8000 beyond loopback.

## Exec Python vs programmatic toolset (43.00)

| | `ProgrammaticToolset.execute_tool_script` | `PythonScriptingTools.execute_python` |
|---|---|---|
| Runs | a sandboxed script whose `run() -> dict` calls registered toolsets via `execute_tool(...)` | arbitrary `unreal` Python in the editor |
| Imports | only `get_execution_environment().supported_modules` | anything the editor has |
| Use for | 5+ placements / property sets / entity edits in one call (faster in 43.00) | a gap no toolset covers, after `read_me` / `search_symbols` / `get_symbol` / `grep_stubs` |
| Ducky rule | default batch path | **last resort**, never for placement, layout, spawning or material assignment |

Order: a toolset tool → `execute_tool_script` for batches → `execute_python` only when neither covers it. Some tools (e.g. `PCGSpatialToolset.RunPCGInstantGraph`) refuse to run inside a script; call them directly. Neither is Ducky's listener `execute_python` (also last resort). Python-backed toolsets need `ValkyriePythonToolset.IsPythonReadyForMainProject` true (`EnablePythonForMainProject`, async).

43.00 Python fixes that change script results: in-place `unreal.Array` / `unreal.Set` ops (`a += b`) used to return `None`; `>=` behaved like `>` for some types; `unreal.Text.is_culture_invariant()` was bound to the wrong function; multicast delegates now tell same-type callables apart. Drop any workaround for these.

## Classic devices (43.00)

`ValkyrieFortniteToolset.DeviceToolset` now edits classic (Blueprint) Creative devices the way the Details panel does: `ListClassicDeviceOptions(devicePath)` returns each option's `currentValue`, `allowedValues` (or `numAllowedValues` → `GetClassicDeviceOptionValues`), min/max and `bIsActive`; `SetClassicDeviceOption(devicePath, optionName, value)` rejects inactive options and values the option does not accept. A rejected set is the validator talking — enable the gating option first, don't retry the same value. `GetDeviceProperties` / `SetDeviceProperty` stay for Verse `creative_device` settings. Event options are not listed: use `ListEventBindings` / `AddEventBinding`.

## Project Agent Skills

Projects and plugins can register Agent Skills through `ToolsetRegistry.AgentSkillToolset` (`ListSkills`, `GetSkills`, `CreateSkill`, `UpdateSkill`) — listed in UEFN 43.00. Call `ListSkills` when starting unfamiliar work; a relevant project skill overrides generic defaults. Authoring: `skill_read_subskill("unreal-engine", "agent_skills")`.

## Which editor answered

Several UEFN / UE editors fight over `127.0.0.1:8000`: the second cannot bind, and the client reaches the first. Recent builds return `_meta["com.epicgames.unrealengine/instance"]` in `initialize` (`processId`, `projectName`, `projectDirectory`, `engineVersion`, …). If Epic calls hit the wrong island (unknown actors/devices), compare `projectName` with `get_project_info` and close the other editor. The port is per user in `EditorPerProjectUserSettings.ini` → `[/Script/ModelContextProtocolEngine.ModelContextProtocolSettings] ServerPortNumber=`; Ducky's nested server URL must match. In 43.00 the MCP settings (port, Start/Stop, config setup) live in **Editor Settings**, not Project Settings.

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
| `unreal__*` missing / `list_toolsets` errors | `epic_mcp_online` is only a TCP probe. `uefn_popups`, retry once, then the closest Ducky tool and finish. Missing tools do not prove the editor is stopped. 43.00: Editor Settings → MCP → Start if the server is stopped. |
| Python-backed toolsets (Sequencer, Geometry, PythonScripting, Programmatic) missing | `ValkyriePythonToolset.IsPythonReadyForMainProject` → `EnablePythonForMainProject` (async), then re-list or `RefreshTools`. |
| "Unknown toolset" for `editor_toolset.toolsets.scene.SceneTools` / `ActorTools` / `AssetTools` | Renamed in 43.00: `EditorToolset.LevelToolset` / `ActorToolset` / `AssetToolset`, PascalCase tools (`epic_toolsets`). |
| An expected toolset missing | `ModelContextProtocol.RefreshTools`, re-list. |
| "Failed to listen on port" in the log | Another editor owns 8000 — close it, or change `ServerPortNumber` and the Ducky MCP URL. |
| Calls hang | Popup (`uefn_popups` first), Verse build, level load, or a running session. |
| Tool returns OK but nothing changed | Silent failure — read the payload; verify with `diff` / `get_properties` / `GetDeviceProperties`. |
