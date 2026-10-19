---
description: "UMG composition of User Widgets — kit widgets and composites inside your screen, named slots for styling, screen fields bound to children (no hidden values), repeated row widgets with paging"
metadata:
  order: 72
  label: "UMG compose"
  default_enabled: false
  load_condition: "Embedding a User Widget in a parent, filling a Named Slot, or building repeated rows"
---

## Compose User Widgets

A screen embeds kit widgets, kit composites and your own small widgets (header, offer row, details pane). Place a child by its class path from `list_widget_classes` (the kit's or the project's `UW_*_C`) with `build_widget_tree`.

**No hidden values.** Never set Verse fields or properties directly on a nested instance — UEFN doesn't show them in the Details panel, so nobody can see or change them. Give the screen a Verse field and bind it to the child (`IsToggleButton1Active` → `ToggleButton1.IsActive`), fill a named slot, or set it from Verse code.

**Style through named slots.** `list_named_slots` on the child, then put an `Image` with your material instance in each slot (`verse_ui_kit` — Style recipe). Renaming a named slot drops what every parent put in it — ask first, note each parent's content, and put it back.

**Clicks from children.** A parent can't listen to a child's Verse event. Bind each child's inner button (`Row1.Root_Button.OnButtonClicked`) to one shared int event on the screen, each child sending its own number from 1 (`verse_ui_kit` — Clicks).

Repeated rows:

- One small row widget built on a kit button (`UW_Shop_OfferRow`), placed a fixed number of times (`Row1` … `Row6`).
- The screen owns one field set per row (`Row1TitleText`, `IsRow1Visible`) bound to that row.
- More data than rows: page with `OnNavigatePage(int)`, refill the fields from Verse, collapse empty rows, refocus.
- Kit list and grid composites already work this way — start from them.

The details pane is one `UW_Shop_OfferDetails`. The parent does not contain a copy of every offer.
