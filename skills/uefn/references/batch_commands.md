---
description: "Serial MCP tools — one editor operation per call (batch/bulk removed)"
metadata:
  order: 8
  label: "Serial tools"
  default_enabled: true
  load_condition: "Any spawn_actor, wire_verse_*, set_creative_device_fields, set_actor_*, destroy/delete, instantiate_prefab, save_current_level, or multi-device level mutation"
---

## One operation per MCP call

`batch_commands`, `bulk_*`, `setup_verse_device`, and `spawn_actor_batch` were
**removed** — they froze UEFN.

| Task | Pattern |
|------|---------|
| Place N devices | `spawn_actor` → wait → `set_actor_label` → wait → `set_actor_folder` **once per device**, then **one** `save_current_level` |
| Wire N scalar refs | `inspect_verse_device` → `wire_verse_device_ref` **once per field** (wait between each) |
| Wire N array entries | `resize_verse_array` if needed → `wire_verse_device_array` **once per target** or `patch_verse_array_entry` per row |
| Spawn + wire Verse device | `spawn_actor` → label → `wire_verse_device_ref` per field (serial) → `save_current_level` |
| Package one mesh prefab | `create_entity` (root) → `create_entity` (child) → `add_entity_component` → `create_prefab_from_entities` → `destroy_entity` the temp — **one call per assistant message**. `save_directory` every 5–10 prefabs. Never an `execute_python` loop over many prefabs. |

**Never** pass multiple fields, multiple spawn items, or combined verify+save mega-calls.
**Never** fire multiple wire/spawn/save tools in the same assistant turn (parallel or batched) — that freezes UEFN and wedges the listener.
The listener drains **max 1 heavy command per tick**.

### Crash postmortem (do not repeat)

Parallel wiring left some `@editable` refs connected and others empty, used a
wrong “horn” actor instead of Creative Audio Player, and crashed UEFN / killed
the MCP bridge on cancel. Recover: restart UEFN → `inspect_verse_device` →
resume **one wire/spawn at a time**. SFX fields → Fortnite Audio Player only
(`skill_read_subskill("uefn", "creative_devices")`).

### Crash postmortem — bulk Python + digest deadlock (do not repeat)

One `execute_python` script that packaged many prefabs froze UEFN. After
restart, Verse linking cascaded `Script error 9002: Unable to import resolve`
into `9000: previous link task did not complete successfully` for unrelated
assets. Recover: comment out the unresolvable `using` / class refs → rebuild
and wait (`WinError 10054` = started) → confirm digest with `list_verse_types`
→ uncomment → rebuild. Check `class_path` for `VERSE_DEAD_*`. Details:
`skill_read_subskill("uefn", "verse_build_lifecycle")`.
