---
description: "In-editor Content Pre-Checks (v42.30) — moderation flags during cook: the notification, Show Violations → Message Log, yellow triangle in the Content Browser, what to do, never blocks publish"
metadata:
  order: 12
  label: "Content Pre-Checks (v42.30)"
  default_enabled: false
  load_condition: "Content Pre-Check, moderation warning, violation notification, yellow warning triangle on an asset, Moderation Message Log, content guidelines, or an asset flagged before publish"
---

# Content Pre-Checks (v42.30)

UEFN now checks assets against the **Epic Games Developer Rules** and the Content
Guidelines **while you build** (during cook), instead of only at upload.

## Where it shows

- A **notification** in the lower right with the number of potential violations
  (and a link to the Content Guidelines).
- **Show Violations** opens the **Message Log** (moderation messages): each flagged
  asset and the policy it may break. Click an asset link to find it in the Content Browser.
- In the **Content Browser** a flagged asset has a **yellow warning triangle**;
  hover it for the policy.

## What to do

1. Open the Message Log from the notification.
2. For each flagged asset: replace or edit it (texture, mesh, text, audio) so it
   follows the guidelines, or remove it if unused.
3. Re-cook (launch a session / push changes) and check the notification again.

These are early **informational** flags, not decisions: they **do not block**
building or publishing. Everything is still moderated at publish. If a flag looks
wrong, publish to the Creator Portal for the full review.

## For Ducky

- Read flags from the editor log: `get_editor_log` / Epic `EditorToolset.LogsToolset.GetLogEntries`
  (pattern on the asset name or "violation"). Report which assets and why; do not
  delete user assets without asking.
- Never try to hide or work around a flag (Developer Rules — includes the 1.22
  conversations rules for LLM personas).
