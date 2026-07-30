---
description: "Finding devices and actors in the level — label_filter patterns and the class_prefix trap"
metadata:
  order: 2
  label: "Discovery"
  default_enabled: false
  load_condition: "Searching the level for devices/actors, or a device seems missing"
---

## Find anything in the level

| Wrong | Right |
|-------|-------|
| `get_all_actors(class_prefix="Fort")` | Only player starts — **never** for "what's in the scene?" |
| Assume device missing | `find_devices(label_filter="wallet")` or `get_all_actors(label_filter="wallet", limit=500)` |
| Guess actor paths | Outliner **label only**, exactly as returned by `find_devices` — **never** long `UAID_...` paths |
| Full inventory | `get_all_actors(limit=500)` — no class_prefix |
