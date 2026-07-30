---
description: "Symptom→fix table for listener/wiring failures — STOP stays true, hash-not-in-cache, hung tools, wrong tool family"
metadata:
  order: 7
  label: "Troubleshooting"
  default_enabled: false
  load_condition: "A listener/wiring call failed, STOP stays true, or tools hang"
---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Device "not found" after a Fort class filter | `find_devices(label_filter="<part of its label>")` |
| Some fields show "Hash not in cache" but STOP is false | **Do not** ask user to compile — `set_currency_config_entries` / `wire_verse_device_ref` |
| Empty Verse editables / STOP true | `workspace_compile_verse` → still STOP: `reload_listener` (wait 3s) → still STOP: user restarts UEFN |
| Tools hang after `reload_listener` | **Restart UEFN** — old reload could deadlock the tick |
| UEFN freezes / listener wedged / `ping` 504 | **Cause:** parallel wire/spawn/save. **Fixed in listener:** atomic accept lock + no clear-on-504; **bridge:** serial lock + 503 retry. **Recover:** restart UEFN. Cursor MCP should use repo `launcher.py` bridge (not stale EXE) so AppData listener stays race-safe. |
| ToyOptions error on Verse device | Wrong path — use Verse tools |
| @editable ref won't set on granter | Wrong path — use Creative tools |

Never loop retries more than twice — report the symptom and the fix you need
from the user (open UEFN, Build Verse Code, restart) instead.
