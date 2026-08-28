---
source_plugin_id: uefn
name: datatables
description: "DataTable assets in UEFN — inspect row structs, read rows, create tables, and rewrite contents via JSON/CSV; capability-guarded editor tools"
license: MIT
metadata:
  label: UEFN Data Tables
  version: 4
  author: UEFN-Ducky
  copyright: Copyright 2026 Mindful Path Company, LLC
  allow_redistribute: true
---

# UEFN Data Tables — read and rewrite

**SERIAL:** never parallel `save_current_level` with other heavy editor calls
in the same turn (`skill_read_subskill("uefn", "batch_commands")`).

DataTables are editor assets holding rows of one struct type. Editing is
**editor-only** Python and has ONE write model: **replace all rows** from
JSON/CSV — there is no per-row write API in Python. The safe loop is always
read → modify → fill.

New island tables live under the **project content mount** from
`get_project_info().content_root` (e.g. `/catland/Data`) — **never** invent
`/Game/...` for create paths (Creative catalog `/Game/Creative` is read-only OK).

## The tools (flat MCP tools)

| Kind | Tools |
|------|-------|
| **PROBE** | `data_table_capabilities` |
| **READ** | `list_data_tables`, `get_data_table_info`, `get_data_table_rows` |
| **CREATE** | `create_data_table` |
| **REPLACE** | `fill_data_table_from_json`, `fill_data_table_from_csv` |

Always `data_table_capabilities({})` first — UEFN builds vary in what
DataTable API Python sees; tools self-describe what IS present on a miss.

## Golden path (edit one row safely)

```
# FIRST: get_project_info() → content_root (e.g. /catland/) — use THAT for new assets
data_table_capabilities({})                                        # PROBE
get_data_table_info({"data_table_path": "/catland/Data/DT_Items"}) # READ -> row_struct, row names, columns
get_data_table_rows({"data_table_path": "/catland/Data/DT_Items",
                     "columns": ["Name", "Cost"]})                 # READ -> current values (paged)
# build the FULL row set as JSON with your one change applied, then:
fill_data_table_from_json({"data_table_path": "/catland/Data/DT_Items",
                           "json_string": "[ ...ALL rows... ]"})   # REPLACE (destructive)
save_current_level()
```

## Hard rules

- **`fill_data_table_from_*` REPLACES EVERY ROW.** Never call it with a partial
  set — read all rows first and write back the complete data. Rows you omit
  are deleted.
- **Field names must match the row struct exactly** (case included) or the
  engine rejects the fill; the error says to check `get_data_table_info` and
  the editor Output Log.
- If `columns` discovery is unavailable in this build, pass `columns=[...]`
  yourself — the row struct's field names (see reference **Row editing**).
- `create_data_table` needs a `row_struct`: an `unreal` struct name
  (`search_unreal_api` to find one) or a full asset path to a user struct.
- Create under `<content_root>/Data/...` — never invent `/Game/Data` for new tables.
- Reads are paged and capped — use `offset`/`limit` and `row_names` filters,
  don't dump giant tables.

## After ANY table change

The fill tools save the asset themselves; still `save_current_level()` if
anything in the level references the table.
