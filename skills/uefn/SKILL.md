---
source_plugin_id: uefn
name: uefn
description: "Device wiring, Verse vs Creative tools, golden paths"
license: MIT
metadata:
  label: UEFN MCP
  version: 34
  author: UEFN-Ducky
  copyright: Copyright 2026 Mindful Path Company, LLC
  allow_redistribute: true
---

# UEFN MCP — Operator Skill

**ALWAYS prefer official UEFN MCP (`unreal__*`) when `epic_mcp_online`.**
Settings → MCPs → **UEFN MCP (Epic)** (`unreal-mcp`).
Only three bridge tools: `unreal__list_toolsets` → `unreal__describe_toolset` →
`unreal__call_tool` into Valkyrie Device / Entity / Verse / Session toolsets (and
`editor_toolset.*` for actors/assets/materials/Niagara/UMG). There are **no** flat
`unreal__create_entity` names. Listener is second — offline `workspace_*`,
VerseDevice wires, prefabs, screenshots/Meshy — never pruned Ducky
`find_devices` / `inspect_creative_device` / `play_in_editor` / `create_entity`
while Epic is up. If Epic is offline, recite `epic_mcp_setup_steps`. Full map:
`skill_read_subskill("uefn", "epic_mcp")`.

Work loop: **find → inspect → write → verify → `save_current_level`**.
Code/behavior changes live in `Verse/**/*.verse` on disk (workspace tools — works with the listener **offline**). Creative-device place/edit and PIC need Epic MCP; VerseDevice `@editable` wires still use Ducky `inspect_verse_device` / `wire_verse_device_ref`. Never poll status tools waiting for the listener.

**CRITICAL — editor mutations are SERIAL:**
Never issue multiple `unreal__*` / `spawn_actor` / `wire_verse_device_ref` / `wire_verse_device_array` /
`set_verse_editable` / `set_actor_*` / destroy/delete /
`instantiate_prefab` / `save_current_level` / `execute_python` (editor) calls in the
same assistant turn or in parallel. One heavy MCP call → wait for result → next.
Parallel or same-batch editor calls freeze/crash UEFN (Epic hitching too).
Prefer `spawn_actor(..., label=..., folder=...)` (same tick) over separate
`set_actor_label` / `set_actor_folder` for **props/meshes**. Never Grep the project root / `Saved/` /
`Intermediate/` / `*.uasset`. Details: `skill_read_subskill("uefn", "batch_commands")`.

**Gameplay SFX / horns / alarms = Fortnite Creative Audio Player only**
(`audio_player_device` in Verse). Never Speakers, prop meshes, or
`spawn_actor(actor_class="*_device")`. Search `/Game/Creative` → spawn `…_C`.
Recipe: `skill_read_subskill("uefn", "creative_devices")`.

**Project content mount (hard rule):** before creating materials/meshes/tables/folders, call `get_project_info()` and use `content_root` (e.g. `/catland/…`). **Never invent `/Game/...` for new island assets** — that breaks cook. `/Game/Creative` is OK for **search/spawn** of catalog devices only.

**Verse folders (hard rule):** never dump new `.verse` at `Verse/` root — one system per folder (`Verse/Economy/…`, `Verse/Shop/…`, …). Prefer `verse_template_apply`. Details: `skill_read_subskill("verse","modules")` and `verse_files`.

**Write boundary (hard rule):** `workspace_write_file` may only write `Content/**` and `.ducky/**`. Never touch UEFN core files, digests, `Saved/`, `Intermediate/`, or the project root. Same rule for `execute_python` / listener file I/O. Scratch → `%LOCALAPPDATA%/UEFN-Ducky/`. Verse build wait / digest deadlock: `skill_read_subskill("uefn", "verse_build_lifecycle")`.

**No extra Python in the island (HARD):** Ducky auto-manages `Content/Python/init_unreal.py` on project open — that file **starts the listener**. **Never delete it, never move it, never tell anyone to remove it.** Do not add any other `.py` / `.pyc` (project root, `.ducky/**`, extra files under `Content/Python/`). Extra `.py` can trip Epic `[ContainsPythonData]`. `execute_python` is in-memory only. Scratch → `%LOCALAPPDATA%/UEFN-Ducky/`.

**Verse errors / logic FIRST:** `workspace_list_verse_errors` (host) — never `ping`, `get_project_info`, `ducky_get_errors`, `execute_python`, or listener tools. If a listener call does not return immediately it is offline/broken; do not retry — stay on `workspace_*`.

## STOP ladder

- `inspect_verse_device` / `get_verse_editables` `STOP: true` or `mangled_name: null` is **advisory**. Resolve, then wire — do not ask the user to Build Verse, paste T3D, or drag Details. Ladder: `list_verse_property_hashes(refresh=true)` → re-inspect that one device → `wire_verse_*` once → still empty: `reload_listener` → retry once. Internals: `skill_read_subskill("uefn", "verse_editable_internals")`.
- `STOP: false` (even with `wiring.status: partial`) → wire with labels now.
- Digest deadlock / `WinError 10054`: `skill_read_subskill("uefn", "verse_build_lifecycle")`.

## Do not / do instead

| Do not | Do instead |
|--------|------------|
| `class_prefix="Fort"` to inventory the scene | `find_devices` / `get_all_actors(label_filter=…)` |
| Loop `inspect_verse_device` / `inspect_creative_device` over every device | `find_devices` once (`kind` + `script_class`); inspect only the device you will write |
| Verse tools on a native device, or Creative tools on a Verse device | Check `kind` from `find_devices` first |
| Check Verse errors via the game / listener / `ping` / `get_project_info` / `execute_python` / `ducky_get_errors` | `workspace_list_verse_errors` FIRST (offline OK); never probe the listener for compile errors |
| >3 discovery calls before a write | find → inspect → write → verify |
| `batch_commands`, `bulk_*`, `setup_verse_device`, `spawn_actor_batch` | **One thin MCP tool per editor op per turn** — never same-turn multi spawn/wire/save |
| Multiple `wire_*` / `spawn_actor` in one assistant message | One call → wait → next; after all placements, one `save_current_level` |
| Prop mesh / Speakers as a “horn” or wave SFX | Creative **Audio Player** only — see `creative_devices` |
| Scan `.uasset` / binaries / `os.walk` for `__verse_0x` hashes | Direct read/write of one object's mangled `__verse_0x<HASH>_<Field>` is fine; prefer `list_verse_property_hashes` / `get_verse_editables` / `wire_verse_*` |
| `wire_verse_device_ref` when target is another Verse device | Same tool works now (auto-routes), or `set_verse_editable` for `?player_manager`-style refs |
| `wire_verse_device_array` for scalar spawner fields (`NPCSpawner1`, …) | `wire_verse_device_ref` once per scalar field — read names from `get_verse_editables` |
| Loop a failing call more than twice | One alternative, then `ducky_ask_user` — do not invent Details-panel homework |
| Ask the user to create NPCDefs / AnimPresets / hook anims / drag wires | You program it: `ducky_get_tools` + `skill_read_subskill("animation", "npc_characters")` + the `create_*` NPC tools. Write original Verse for *this* island. |

## Project memory (index + pull, like skills)

Each project has ONE memory shared by its duckies: named entries stored in app data per project (`memory/projects/<project-slug>/<entry>.md`, same separation as chats — survives project-folder deletion). Only the INDEX (name — description) is in your prompt — pull one entry with `project_memory_get(name)` when its description matches the task, never bulk-read. Save stable facts (the user's name for a thing → its Outliner label, verse vs creative devices, field names that worked, coding standards, decisions) with `project_memory_save(name, content, description, author=<your ducky name>)` — one topic per entry, description says when to pull it; extend with `project_memory_append(name, text)`. Memory entries grow like skills: when a topic gets big, split it into sub-entries — `project_memory_save("coding-standards/error-handling", …)` (one nesting level; the parent becomes that topic's index). Document hard-won solutions as you solve them, like building a project-specific skill. You WRITE only to YOUR project's memory; you can READ any project's with `project_memory_list(project=...)` / `project_memory_get(name, project=...)`. To check what duckies elsewhere know: `ducky_memory_overview` surveys every project's memory index + chats, then `ducky_read_chat(conv_id, project=...)` / `ducky_get_chat_context(conv_id, project=...)` read a specific ducky's context (its chat history) cross-project.

**Island languages / PO / Export Localization / L10N assets:** load
`skill_read_subskill("localization")` (UI-ready checklist:
`skill_read_subskill("localization", "ui_ready")`). Not Ducky app UI translation.

This guide is already in your context — do **not** call `uefn_skill` to re-fetch it. Load the reference files listed below with `skill_read_subskill` only when their condition applies.
