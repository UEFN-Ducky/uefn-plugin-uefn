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
| UEFN freezes / listener wedged / `ping` 504 | **Cause:** parallel wire/spawn/save in one turn. **Recover:** restart UEFN; resume **one** editor op per turn (`batch_commands`). |
| Partial wires after a crash | `inspect_verse_device` → list empty vs set → wire remaining fields **one at a time** |
| Horn / SFX is Speakers or a prop mesh | Delete wrong actor; place Creative **Audio Player** (`creative_devices`); wire `audio_player_device` fields |
| New `@editable` missing on device Script | Build Verse → may need **re-place** the Verse device so Script picks up fields; then wire serially |
| MCP bridge dies: `Request already responded to` | Cancel race — restart Ducky/MCP bridge (launcher patches idempotent respond); do not parallel long tools |
| ToyOptions error on Verse device | Wrong path — use Verse tools |
| @editable ref won't set on granter | Wrong path — use Creative tools |

Never loop retries more than twice — report the symptom and the fix you need
from the user (open UEFN, Build Verse Code, restart) instead.
