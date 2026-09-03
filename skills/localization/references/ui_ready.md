---
description: "Verse/UMG/HUD localization-ready checklist — named <localizes> messages, no raw strings, no baked English UI textures; what to do before Export Localization"
metadata:
  order: 0
  label: "UI localization-ready"
  default_enabled: true
  load_condition: "Making island UI, HUD, canvas, UMG, or device text localization-ready / localizable for Export Localization or PO gather"
---

## UI and localizations READY

Goal: every player-facing string is a gatherable `message` so
`Build > Export Localization` can emit PO entries. Type-correct UI that still
builds English at runtime (`Message(BuiltString)`) is **not** fully L10N-ready.

### Checklist

1. **On-screen text = `message` + `<localizes>`** — never pass a raw `string`
   into `SetText`, HUD message devices, or UMG text bindings that expect
   `message`.
2. **Prefer named literals** (stable gather keys), not only a catch-all helper:

```verse
ShopTitle<localizes> : message = "Shop"
BuyButton<localizes> : message = "Buy"
NotEnoughFunds<localizes> : message = "Not enough funds"
```

3. **Format args with typed `<localizes>` helpers** when values are not plain
   strings (agents, counts):

```verse
MessageCount<localizes>(Count : int) : message = "x{Count}"
MessageAgent<localizes>(Agent : agent) : message = "{Agent}"
```

4. **Avoid concat-then-wrap as the only source of copy** —
   `Message(BuiltEnglish)` / string concat into `{String}` compiles and
   displays, but yields weak or non-existent PO keys. Keep English literals in
   `<localizes>` definitions; pass dynamic values as parameters.
5. **Verse canvas:** `text_block` + `SetText(NamedMessage)` (or a
   parameterized `<localizes>`). Do not put English labels into
   `texture_block` images when a text widget will do.
6. **HUD devices:** `SetText` returns `void`, so it **cannot be chained** —
   two calls, or the one-shot `Show` overload that takes the message:

```verse
HudMessage.SetText(NamedMessage)
HudMessage.Show(Agent)
# digest also has Show(Agent:agent, Message:message, ?DisplayTime:float)
HudMessage.Show(Agent, NamedMessage, ?DisplayTime := 3.0)
```

   Same `message` rules. Details: `skill_read_subskill("verse", "devices")`.
7. **UMG:** Verse field type `message` → View Bindings → Text. Drive with
   named `<localizes>` fields (see Style1/Style2 in
   `skill_read_subskill("verse", "umg_verse_fields")`). Numbers: ToText
   conversion or a `<localizes>` helper — `umg_view_bindings`.
8. **Static designer Text** on a UMG widget with no Verse `message` field /
   binding is not driven by your Verse gather path — bind it or accept that
   Export may not pick it up the way you expect.
9. **Baked text in textures / materials** (logos with words, poster art) cannot
   be fixed by PO strings — use **asset localization**
   (`skill_read_subskill("localization", "asset_l10n")`).
10. **`Print(...)` is not player UI** — do not treat debug prints as localized
    copy.

### Catch-all helper (OK for dynamics, not for all copy)

```verse
Message<localizes>(String : string) : message = "{String}"
```

Use for parameterized formatting when needed. Do **not** make every shop
title `Message("Shop")` with no named constant if you care about clean PO
entries — declare `ShopTitle<localizes> : message = "Shop"` instead.

### Surfaces → verse refs

| Surface | Load |
|---------|------|
| Effect table | `verse` / `effects` |
| Canvas + visibility | `verse` / `ui`, `sys_canvas_cookbook` |
| ShowHUD | `verse` / `sys_hud_template` |
| UMG fields | `verse` / `umg_verse_fields` |
| Bindings / ToText | `verse` / `umg_view_bindings` |

### After authoring

1. `workspace_list_verse_errors` — clean Problems.
2. Remind the user: configure Project Settings if needed →
   `Build > Export Localization` (see `export`).
3. Or rely on Private Version with Build Localization enabled
   (`private_version`).

### Anti-patterns

| Do not | Do instead |
|--------|------------|
| `SetText("Hello")` / raw `string` | Named `<localizes>` → `message` |
| English in a UI texture for a label | `text_block` / UMG Text + message |
| Only `Message(ConcatenatedEnglish)` for all UI | Named literals + typed args |
| Claiming MCP ran Export Localization | Guide the user through the menu |
| Ducky `translate_ui_*` for island copy | This pack — island PO / L10N |
