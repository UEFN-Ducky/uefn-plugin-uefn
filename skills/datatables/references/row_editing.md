---
description: "The JSON round-trip recipe for row edits, CSV variant, struct discovery, and fill-rejection troubleshooting"
metadata:
  order: 1
  label: "Row editing (round-trip)"
  default_enabled: false
  load_condition: "Editing/adding/deleting data table rows, a fill call was rejected, or column discovery came back unavailable"
---

## Row editing — the JSON round-trip

There is no add_row/update_row/delete_row in editor Python. Every write is a
full-table replace, so every edit follows the same shape:

1. **Read everything.** `get_data_table_info` for `row_struct` + `row_names`,
   then `get_data_table_rows` (page with `offset`/`limit` until you have all
   rows — `total` tells you when you're done).
2. **Rebuild the full JSON array** — one object per row. The row's NAME goes in
   a `"Name"` key alongside the struct fields (that is the engine's JSON table
   format):

```json
[
  {"Name": "Sword",  "DisplayName": "Iron Sword", "Cost": 150},
  {"Name": "Shield", "DisplayName": "Oak Shield", "Cost": 90}
]
```

3. **Apply the change in the JSON** — edit a value, append an object (add row),
   drop an object (delete row), rename via the `Name` key.
4. `fill_data_table_from_json` with the complete array.
5. Re-read one changed row to verify — never assume the fill landed.

### CSV variant

Header row = `---` then the field names; first column is the row name:

```
Name,DisplayName,Cost
Sword,Iron Sword,150
```

Use CSV when the user hands you spreadsheet data; JSON otherwise (types are
less ambiguous).

### When column discovery is unavailable

`get_data_table_info` returns `columns: null` + a note on some builds. Get the
field names from the row struct instead:

- `row_struct` in the info result names the struct asset/class.
- Engine structs: `describe_class` on the struct name shows its attributes.
- User structs (a `/Game/...` path): open in the editor or read one row via
  `get_data_table_rows` with your best-guess `columns` — wrong names come back
  in `column_errors` without failing the whole read.

### Fill rejected? (the engine returned false)

- A field name in the JSON doesn't match the struct — case matters.
- A value can't parse into the field type (e.g. text into an int field).
- Struct fields with exported names differ from display names — the editor
  Output Log names the exact offending row/field; ask for it or check via
  `get_editor_log`.
- Enums/asset refs are strings in table JSON — use the exact enumerator or
  object path text you saw in the read.

### Creating a table

```
# folder = get_project_info().content_root + "Data" (e.g. /catland/Data) — never invent /Game/Data
create_data_table({"asset_name": "DT_Items", "folder": "/catland/Data",
                   "row_struct": "<StructName or <content_root>/.../S_ItemRow>"})
```

Then fill it — a fresh table has zero rows. If the struct doesn't exist yet,
that's editor work (or an engine struct found via `search_unreal_api`); the
tool errors clearly when it can't resolve the struct.
