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
inspect_verse_device(actor_path="MyWallet")          # STOP false → continue (partial OK)
set_currency_config_entries(actor_path="MyWallet", entries=[
  {"CurrencyName": "Gold", "DisplayOrder": 0},
  {"CurrencyName": "Diamonds", "DisplayOrder": 1}
])
wire_verse_device_ref(actor_path="MyWallet", field="PlayerManager", target_path="MyPlayerManager")
patch_verse_array_entry(actor_path="MyWallet", array_field="CurrencyConfigs", index=0, properties={"CurrencyIcon": {"texture_path": "T_..."}})
save_current_level()
inspect_verse_device(actor_path="MyWallet")
```

All names from **inspect** — never from templates. **One MCP call per wire/set —
wait for each result before the next** (never same-turn multi wire/spawn/save).

## Creative golden path (granter example)

```
find_devices(label_filter="granter")
inspect_creative_device(actor_path="MyGoldGranter")
set_creative_device_fields(actor_path="MyGoldGranter", fields={...}, save_level=true)
```

Property keys from **inspect_creative_device** only.
