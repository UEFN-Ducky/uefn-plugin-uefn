---
source_plugin_id: uefn
name: localization
description: "UEFN Text Localization — project settings, Export Localization PO files, Auto/manual translation, Private Version auto-build, asset L10N folders, and Verse/UMG localization-ready UI. Use when translating island text, PO files, L10N, Export Localization, Auto Localization, or making HUD/UMG/canvas copy localizable."
license: Ducky Source-Available License v1.0
metadata:
  label: UEFN Text Localization
  version: 1
  author: UEFN-Ducky
  copyright: Copyright 2026 UEFN-Ducky
  allow_redistribute: false
---

# UEFN Text Localization

Widen the island audience: gather localizable text from assets + Verse into
per-language **PO** files, translate them, and (optionally) swap whole assets
per language under **L10N**.

**Not this pack:** Ducky desktop UI language (`translate_ui_*` / Settings →
language). That is app chrome. This pack is **Fortnite player-facing island**
text and localized content.

## MCP hard rule

There are **no** MCP tools for `Build > Export Localization` or
`Build > Build Auto Localization`. The agent:

1. Makes Verse / UMG / HUD **localization-ready** (workspace + digests + umg_*).
2. Edits on-disk PO files when they already exist (`workspace_*` under the
   project Localization content).
3. **Guides the user** through UEFN menus / Project Settings for export, auto
   translate, and Private Version Build Localization.

Never claim you ran Export Localization yourself.

## Two phases

| Phase | Job | Agent role |
|-------|-----|------------|
| **1. Ready** | Player-facing copy is gatherable | Author `message` + `<localizes>`; avoid baked English textures for labels → `ui_ready` |
| **2. Pipeline** | Export → translate → cook/publish | Guide menus; edit PO if present → `project_settings`, `export`, `translation`, `private_version`, `asset_l10n` |

Localization adapts copy for the target culture (idioms, jokes, references).
Literal word-for-word translation is only one approach — prefer natural
equivalents when hand-editing PO.

## Native Language (critical)

Author **all** localizable text in one Native Language (Project Settings).
Do **not** change Native Language after translations exist — you lose existing
translation data. Languages to Generate must be Fortnite-supported locales.

## Golden path (island text)

```
1. skill_read_subskill("localization", "ui_ready")
   → fix Verse/UMG/HUD to named <localizes> / message bindings
2. skill_read_subskill("localization", "project_settings")
   → user: Native Language + Languages to Generate (+ PO Format)
3. User: Build > Export Localization
   → PO under project Localization content (see export)
4. User: Build > Build Auto Localization  and/or  manual PO edit
   → import when prompted (see translation)
5. Private Version / publish cooks PO → runtime format (see private_version)
6. Texture/material text that cannot be strings → asset_l10n (L10N/<lang>/…)
```

## Verse / UI code patterns (load verse pack)

This pack owns the Epic pipeline + readiness checklist. Code recipes live in
`verse`:

| Need | Load |
|------|------|
| `<localizes>` effect | `skill_read_subskill("verse", "effects")` |
| HUD message devices | `skill_read_subskill("verse", "devices")` |
| Canvas `text_block` | `skill_read_subskill("verse", "ui")` |
| Canvas visibility + Message rule | `skill_read_subskill("verse", "sys_canvas_cookbook")` |
| ShowHUD template | `skill_read_subskill("verse", "sys_hud_template")` |
| UMG `message` fields | `skill_read_subskill("verse", "umg_verse_fields")` |
| View Bindings / ToText | `skill_read_subskill("verse", "umg_view_bindings")` |

## Load when needed

- Make UI/copy localization-ready → `skill_read_subskill("localization", "ui_ready")`
- Project Settings (Native Language, languages, auto-build) → `project_settings`
- Export Localization / PO on disk → `export`
- Auto Localization or manual PO → `translation`
- Private Version / Publish Build Localization → `private_version`
- Per-language asset swaps (`L10N/`) → `asset_l10n`
