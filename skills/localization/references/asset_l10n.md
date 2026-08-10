---
description: "Asset localization — per-language asset replacements under Content L10N/<lang>/ mirroring the source path; Show Localized Content"
metadata:
  order: 5
  label: "Asset L10N (L10N folders)"
  default_enabled: false
  load_condition: "Localizing textures, materials, or whole assets per language, L10N folders, or Asset Localization Content Browser menu"
---

## Asset localization

Replace an entire asset per language when PO strings are not enough — e.g.
a texture that **contains** painted text, or culture-specific art/refs that
should not appear in another region.

### Path pattern

Localized assets live under an **L10N** folder inside the project content,
then the language code, then the same relative path as the source:

| Source | French (`fr`) localized |
|--------|-------------------------|
| `/MyProject/MyFolder/MyAsset` | `/MyProject/L10N/fr/MyFolder/MyAsset` |

Use the real project mount from `get_project_info().content_root` — never invent
`/Game/...` for new island assets.

### Content Browser

- **Asset Localization** sub-menu — manage localized variants.
- Localized assets are **hidden by default** — enable
  **Settings → Show Localized Content** to see them.

### When to use vs text PO

| Situation | Path |
|-----------|------|
| HUD / UMG / Verse string copy | `ui_ready` → export → PO (`export` / `translation`) |
| Words baked into a texture or culture-specific mesh/material | This subskill — per-lang asset under `L10N/<lang>/` |

### Agent role

- Prefer real `text_block` / UMG Text + messages over baking labels into
  textures when possible (cheaper to translate).
- When asset L10N is required: create the mirrored path under `L10N/<lang>/`,
  keep Show Localized Content in mind when searching assets.
- Create under the project content mount only.
