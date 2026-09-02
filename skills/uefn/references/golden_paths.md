---
description: "End-to-end worked wiring examples — a Verse device config flow and a Creative device config flow"
metadata:
  order: 5
  label: "Golden paths"
  default_enabled: false
  load_condition: "Wanting a full worked example of configuring/wiring a device end to end"
---

## Verse golden path (wallet / currency example)

Labels below are placeholders — always use the real Outliner labels from `list_verse_devices`.

```
workspace_list_verse_errors()                        # Problems clean first
workspace_compile_verse()                            # real build — fields need a compiled hash (else STALE REFLECTION)
list_verse_devices()                                 # label + script_class; pick "MyWallet"
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
unreal__describe_toolset(toolset_name="ValkyrieToolset.DeviceToolset")   # read exact argument names — never invent them
unreal__call_tool(toolset_name="ValkyrieToolset.DeviceToolset", tool_name="GetDeviceProperties", arguments={…})  # device ref for "MyGoldGranter"
unreal__call_tool(toolset_name="ValkyrieToolset.DeviceToolset", tool_name="SetDeviceProperty",  arguments={…})  # one property per call, wait
save_current_level()                                                     # once at the end — never save_level=true inside other calls
```

Property keys from Epic **GetDeviceProperties** only. If `ducky_get_status.epic_mcp_online` is
false or the Epic call errors twice, degrade: placement falls back to `spawn_actor(asset_path=…)`
(props and Verse devices only) and finish the task — never stop mid-task.
