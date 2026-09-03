---
description: "Auto Localization (machine translate) and manual PO editing — Translation Mode, import results, Poedit / Crowdin"
metadata:
  order: 3
  label: "Translation (auto + manual)"
  default_enabled: false
  load_condition: "Auto Localization, machine translation, editing PO files, Poedit, Crowdin, or importing translation results"
---

## Translation

After export, fill per-language replacements in the PO files. Two paths:
**Auto Localization** (machine) and **manual** PO edit. Use either or both.

### Localization vs literal translation

- **Localization** — adapt copy so it feels natural (idioms, puns, jokes,
  local references → suitable equivalents).
- **Translation** — more literal word-for-word. Prefer localization when
  hand-editing player-facing copy.

### Auto Localization

1. Configure Auto Localization settings if prompted (`project_settings`).
2. User: **Build → Build Auto Localization**.
3. Runs **asynchronously** via an online service — project / UEFN need not
   stay open.
4. When finished, UEFN prompts to **import** the result → updates PO files
   on disk.

| Setting | Notes |
|---------|--------|
| Languages to Translate | May be a subset of Languages to Generate |
| Translation Mode | Default: only fill **untranslated** text; do not overwrite existing translations unless the mode allows it |

Agent cannot start Auto Localization via MCP — guide the menu + import step.

### Manual localization

Edit the exported PO files:

- On disk (workspace tools / external editor), or
- Through the Content Browser in UEFN.

PO is a common format:

- Local tools: **Poedit**
- Collaborative: **Smartling**, **Crowdin** — if using Crowdin, match the
  project’s **PO Format** export setting.

After manual edits, keep PO under source control with the rest of content.

### Agent role on PO files

- Only edit PO that already exists from a real export.
- Preserve msgid / structure; change msgstr (and comments only when needed).
- Do not fabricate a full Localization tree from scratch — user must Export
  first if files are missing.
