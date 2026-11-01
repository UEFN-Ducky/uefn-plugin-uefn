---
source_plugin_id: uefn
name: unreal-engine
description: "Full Unreal Engine 5 editor through Epic's official unreal-mcp server (ModelContextProtocol + AllToolsets): discover → describe → call_tool, safety rules, project Agent Skills, setup, recovery, authoring toolsets and Agent Skills. Trigger on UE work: BP_/WBP_/M_/MI_/NS_/CR_/SK_/SM_/ABP_ assets, Sequencer, Control Rig, GAS, Behavior/State Trees, Live Coding, .uproject. UEFN islands: uefn epic_mcp / epic_mcp_ops"
license: MIT
metadata:
  label: Unreal Engine (Epic MCP)
  version: 1
  author: UEFN-Ducky (adapted from Epic Games)
  copyright: Copyright 2026 Epic Games, Inc.; adaptation Copyright 2026 Mindful Path Company, LLC
  allow_redistribute: true
---

# Unreal MCP — live Unreal Engine editor

Adapted from EpicGames/unreal-engine-skills-for-claude-code-plugin (`skills/unreal-mcp`, MIT).
UEFN islands use the same server family with a different toolset set → `uefn` `epic_mcp`,
`epic_toolsets`, `epic_mcp_ops`.

The `unreal-mcp` server exposes hundreds of tools across 30+ toolsets (actors, Blueprints, materials, Niagara, Sequencer, Control Rigs, GAS, automation tests, Live Coding, State/Behavior Trees, widgets, Dataflow, Game Feature Plugins, physics assets, …) registered through Unreal's `ToolsetRegistry`. Inspect and mutate live editor state yourself; never tell the user to do it by hand.

The connection may appear as `unreal-mcp-proxy` when the engine's optional proxy is installed — use that one. In Ducky the tools show as `unreal__list_toolsets`, `unreal__describe_toolset`, `unreal__call_tool`.

Treat as Unreal context even without the word "Unreal": asset prefixes `BP_`, `WBP_`, `M_`, `MI_`, `NS_`, `CR_`, `SK_`, `SM_`, `ABP_`; UE C++ types/macros (`AActor`, `UPROPERTY`, `UMyComponent::Method`); `.uproject`; Content Browser; Outliner; PlayerStart. Skip for Unity, Godot, or unrelated uses of "blueprint" / "sequencer" / "widget".

## First step every time: discover, then dispatch via `call_tool`

Tool search is on by default (`bEnableToolSearch=true`): the server advertises only `list_toolsets`, `describe_toolset`, `call_tool`. Names like `BlueprintTools.create` or `SequencerTools.create_level_sequence` are **not** in `tools/list` — they are dispatched server-side through `call_tool`. This keeps context small and the prompt cache warm.

1. `list_toolsets` to see what is registered, then `describe_toolset` on the candidate(s) for schemas. If you already know the toolset ("make a Blueprint" → Blueprint toolset), skip listing and go straight to `describe_toolset`.
2. `call_tool` with `toolset_name`, `tool_name`, and an `arguments` object matching the schema. The result comes back the same turn.
3. Top-level dispatch (omitting `toolset_name`) is reserved for tools registered directly on the server and is rejected for `call_tool` itself.

Missing tools do not prove the editor is stopped. Check the `unreal-mcp` / `unreal-mcp-proxy` connection and follow `operations`. A proxy can stay connected while Unreal is down, and a client can keep a stale catalog after recovery. `unreal_mcp_status` reports the proxy's session state, not reachability — verify with a read-only Unreal tool call. First-time config: `setup`.

## Safety rules

- **Save first, then save again.** Save (`EditorToolset.AssetToolset.SaveAsset`; actors `LevelToolset.SaveActor`) before any bulk change and after. MCP edits are not always undoable, especially across compilation boundaries. Anything touching multiple assets is destructive and needs a recovery point.
- **Wait for compilation.** With C++ or shader compilation in flight, calls hang or fail confusingly. To rebuild C++ from the running editor, call `LiveCodingToolset.CompileLiveCoding` and wait on its result — it blocks until the compile finishes and returns MSVC diagnostics. Never send the user to the IDE.
- **Control concurrent calls.** MCP accepts concurrent requests and synchronizes dispatch, but async tools can overlap and request order is not completion order. Serialize dependent calls and mutations of the same asset/editor state; parallelize only independent work on tools that tolerate overlap. Multiple agents can share one editor; their conflicting changes collide. Ducky default: one mutating editor call per turn.
- **Always check the result.** Blueprint compile, widget creation, material edits often return a status that flips success/failure with no exception on the wire. Read the response; anything not an explicit success is a stop.
- **Mind PIE.** Editor-only tools (asset creation especially) behave differently during Play-in-Editor. If a result looks wrong, check for PIE and stop it.
- **Source control.** Save and commit/shelve before a long MCP session; review the diff before submitting.
- **Security.** `ProgrammaticToolset.execute_tool_script` runs arbitrary Python in the editor with full project access — treat every call as privileged. Localhost is not a trust boundary: any same-user process can reach the port. Never expose it beyond loopback.

## Project skills (Agent Skills)

Projects and plugins can register **Agent Skills** — named instruction bundles (naming conventions, folder layout, required setup, canonical multi-step sequences). They are reached through `AgentSkillToolset`, not `list_toolsets`. Check whenever you start unfamiliar work in a project:

1. `call_tool` → `AgentSkillToolset.ListSkills` — each entry has a short description.
2. Relevant one → `AgentSkillToolset.GetSkills` on it, then follow it.
3. Nothing matches → normal tool discovery.

A relevant project skill **overrides** generic defaults. Authoring them: `agent_skills`.

## Batching

5+ editor ops → `ProgrammaticToolset`: `get_execution_environment` once (read `instructions`, `supported_modules`), `describe_toolset` for every toolset the script calls, then `execute_tool_script(script)` defining `run() -> dict`.

## Reference files

- `setup` — enable plugins, auto-start, `.mcp.json`, proxy, several editors.
- `operations` — console commands, tool-search mode, proxy recovery, identify the editor, troubleshooting matrix.
- `create_toolset` — author or extend a toolset (C++ or Python): principles, docs, errors, tests, review.
- `agent_skills` — author or review Agent Skills (Python class or UAsset).
- `project_context` — telling a folder is a UE project or engine tree, and which conventions to default to.
