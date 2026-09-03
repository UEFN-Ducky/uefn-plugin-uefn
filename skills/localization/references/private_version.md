---
description: "Private Version / Publish automatic export and translate — Build Localization checkbox, Automatically Build Localization opt-out, first Native Language prompt"
metadata:
  order: 4
  label: "Private Version auto L10N"
  default_enabled: false
  load_condition: "Private Version, Upload to Private Version, Publish Project, Build Localization checkbox, or automatic localization on upload"
---

## Automatic export and translation (Private Version)

Creating a **Private Version** runs the localization pipeline by default
(export + translate), whether you use:

- UEFN: **Project → Upload to Private Version**, or
- Creator Portal: **Project → Publish Project**.

### Opt out

| Scope | How |
|-------|-----|
| **Permanent** | Project Settings → uncheck **Automatically Build Localization** |
| **One Private Version** | Uncheck **Build Localization** on the Private Version settings dialog |

### First Native Language

If Native Language has never been set, the first Private Version generation
requires choosing it (same meaning as Project Settings Native Language).
That prompt only appears when Native Language is unset.

### Agent role

- Remind the user that publish/Private Version will touch localization unless
  they opted out.
- If they have not authored gatherable copy yet, fix UI first (`ui_ready`)
  before relying on automatic build.
- Cannot toggle these checkboxes via MCP — describe where to click.
