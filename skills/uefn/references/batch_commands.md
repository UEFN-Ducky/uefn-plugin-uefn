---
description: "Serial MCP tools — one editor operation per call (batch/bulk removed)"
metadata:
  order: 8
  label: "Serial tools"
  default_enabled: false
  load_condition: "Placing or wiring multiple devices in the level"
---

## One operation per MCP call

`batch_commands`, `bulk_*`, and `setup_verse_device` were **removed** — they froze UEFN.

| Task | Pattern |
|------|---------|
| Place N devices | `spawn_actor` → `set_actor_label` **once per device**, then `save_current_level` |
| Wire N scalar refs | `inspect_verse_device` → `wire_verse_device_ref` **once per field** |
| Wire N array entries | `resize_verse_array` if needed → `wire_verse_device_array` **once per target** (single `target_path`) or `patch_verse_array_entry` per row |
| Spawn + wire Verse device | `spawn_actor` → `set_actor_label` → `wire_verse_device_ref` per field → `save_current_level` |

**Never** pass multiple fields, multiple spawn items, or combined verify+save mega-calls.
**Never** fire multiple wire/spawn/save tools in the same assistant turn (parallel or batched) — that freezes UEFN and wedges the listener.
The listener drains **max 1 heavy command per tick**.
