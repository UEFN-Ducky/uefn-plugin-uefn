---
description: "UEFN Project Settings for Text Localization — Native Language, Languages to Generate, PO Format, Automatically Build Localization"
metadata:
  order: 1
  label: "Project Settings (L10N)"
  default_enabled: false
  load_condition: "Configuring Native Language, languages to generate, PO Format, or Automatically Build Localization in Project Settings"
---

## Project Settings — Text Localization

Open **Project → Project Settings** in UEFN. If localization has never been
configured, Export Localization / Auto Localization / first Private Version
will prompt for the needed fields.

### Settings that matter for export

| Setting | Meaning |
|---------|---------|
| **Native Language** | Language in which you author all localizable text. One language for the whole project. |
| **Languages to Generate** | Locales that get localization data. Limited to languages Fortnite supports. |
| **PO Format** | Format of exported PO files. May be changed later if a translation tool needs a different format. |

### Settings that matter for Auto Localization

Configured under Auto Localization in Project Settings (prompted on first
`Build > Build Auto Localization`):

| Setting | Meaning |
|---------|---------|
| **Languages to Translate** | Subset of generated languages that machine translation will fill. Change anytime. |
| **Translation Mode** | Whether machine translation may replace existing translations. Default: only untranslated text. |

### Automatically Build Localization

When checked (default), creating a Private Version / publishing runs the
automatic export + translate pipeline. Uncheck to **permanently** opt out
for the island. One-shot opt-out lives on the Private Version dialog — see
`private_version`.

### Hard rules

1. **Set Native Language once** and keep it. Changing it after translations
   exist loses existing translation data.
2. Author every localizable string in that Native Language — do not mix
   source languages in gathered text.
3. Languages to Generate ⊆ Fortnite-supported set — do not invent locale codes.
4. Agent cannot flip these via MCP — tell the user which settings to open and
   what to set.
