---
description: "End-to-end worked wiring examples — a Verse device config flow and a Creative device config flow"
metadata:
  order: 5
  label: "Golden paths"
  default_enabled: false
  load_condition: "Wanting a full worked example of configuring/wiring a device end to end"
---

## Verse golden path (wallet / currency example)

Labels below are placeholders — always use the real Outliner labels from `find_devices`.

```
find_devices(label_filter="wallet")
inspect_verse_device("MyWallet")          # STOP false → continue (partial OK)
set_currency_config_entries("MyWallet", entries=[
  {"CurrencyName": "Gold", "DisplayOrder": 0},
  {"CurrencyName": "Diamonds", "DisplayOrder": 1}
])
wire_verse_device_ref("MyWallet", "PlayerManager", "MyPlayerManager")
patch_verse_array_entry("MyWallet", "CurrencyConfigs", 0, {"CurrencyIcon": {"texture_path": "T_..."}})
save_current_level()
inspect_verse_device("MyWallet")
```

All names from **inspect** — never from templates. **One MCP call per wire/set —
wait for each result before the next** (never same-turn multi wire/spawn/save).

## Creative golden path (granter example)

```
find_devices(label_filter="granter")
inspect_creative_device("MyGoldGranter")
set_creative_device_fields("MyGoldGranter", fields={...}, save_level=true)
```

Property keys from **inspect_creative_device** only.
