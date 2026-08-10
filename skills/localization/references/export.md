---
description: "Build > Export Localization — gather assets + Verse into per-language PO files under the project Localization content folder"
metadata:
  order: 2
  label: "Export Localization (PO)"
  default_enabled: false
  load_condition: "Exporting localization, PO files, Localization folder, or gathering localizable text from the project"
---

## Export Localization

**Export** collects localizable text from project content (assets and Verse)
and writes per-language **Portable Object (PO)** files ready to translate.

### How to run (user in UEFN)

1. Configure Project Settings if prompted (`project_settings`).
2. **Build → Export Localization**.
3. Wait for the synchronous progress notification — keep the editor open;
   export runs locally in the editor.

### Where files land

Per-language PO files appear under the **Localization** folder in the
project’s content. Treat them like any other project content:

- Submit to source control, or
- Use Lore Version Control in the project.

They are included when uploading the project and are converted to their
runtime format during cooking.

### Agent role

- Ensure copy is gatherable first → `ui_ready`.
- After export, PO may be readable/editable on disk with workspace tools
  (paths under the project Localization content). Prefer surgical edits;
  do not invent PO structure.
- **Cannot** trigger Export via MCP — instruct the user to run
  **Build → Export Localization**.

### Iterate

Re-run export as localizable text changes over the life of the island. New
strings appear as untranslated entries; existing translations are preserved
when Native Language and keys stay stable.
