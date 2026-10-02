---
description: "UEFN popups — why tools hang behind them, uefn_popups (numbered capture) + uefn_popup_press, the Verse-error popups Ducky answers on project open, and why the level is not saved until Verse builds clean"
metadata:
  order: 6
  label: "UEFN popups"
  default_enabled: false
  load_condition: "A tool hangs or times out, UEFN shows a dialog/popup, a project opened with Verse errors, or Save is refused after a skip"
---

## UEFN popups

A modal UEFN popup blocks the editor's thread: listener calls, Epic `unreal__*` tools and
`execute_python` all wait behind it. Never wait one out and never restart UEFN for it.

UEFN draws its dialogs itself (Slate): no button can be found by name. Ducky finds them
in a capture instead.

1. `uefn_popups` — every UEFN window besides the main editor, each captured into the chat
   with its buttons boxed and numbered 1, 2, 3… left to right. `blocking: true` means a
   modal is up (the main editor is disabled); a floating Message Log is not a blocker.
2. Look at the capture, pick the button, `uefn_popup_press(hwnd, n)`. The result says
   whether it closed and which popups are open now (one press can open the next).
3. A button outside the numbered row (e.g. "Open in VS Code" in an error list): use the
   capture's fractions with `uefn_window_click`.

Save prompts ("Save Content") are still pressed for you around builds; `dismiss_uefn_modal`
does it by hand.

### Project opened with Verse errors (answered for you)

| Popup | Ducky presses |
|---|---|
| Verse Build Errors | **Skip Rebuild** (button 3) |
| Data Loss Warning | **Skip Rebuild & Continue** (button 1) |
| Verse Validation Errors | **Continue** (button 4) |

Ducky only presses when the popup looks as expected (button count and where the blue
default button is); otherwise it leaves it for you and `uefn_popups`.

After that the level's Verse devices are broken in memory ("Failed to load verse class"
in the Message Log). Saving the level now would break them for good, so until Verse
builds clean Ducky refuses `save_*` tools, skips the pre-build save and does not press
Save prompts. Fix the Verse, then `workspace_compile_verse`: on a clean build Ducky
reloads the level from disk without saving (`level_reloaded` in the result) and the
devices find their classes again. Then launch the session.
