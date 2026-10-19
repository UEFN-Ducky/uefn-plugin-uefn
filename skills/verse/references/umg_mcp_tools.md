---
description: "UMG MCP tools — probe-first workflow, create/inspect/tree/bindings, what is scriptable vs designer-only, crash bans for ToolsetRegistry schema dumps"
metadata:
  order: 65
  label: "UMG MCP tools workflow"
  default_enabled: false
  load_condition: "Using umg_* MCP tools to create or edit Widget Blueprints, inspect Verse fields on a UW_*, or scaffold a widget tree"
---

## UMG MCP tools workflow

**Probe first:** `ducky_get_status` → when `epic_mcp_online` use nested `unreal__*`
`UMGToolSet.UMGToolSet` / `MVVMToolset.MVVMToolset` / `VerseFieldsToolset.VerseFieldsToolset`
(describe then call). Listener `umg_*` is second. Never `execute_python`
`ToolsetRegistry.get_all_toolset_json_schemas()` (hard-crash).

Listener-backed tools gated by the **verse** Store plugin.

### Probe first

```
ducky_get_status
# epic_mcp_online → unreal__describe_toolset({ "toolset_name": "UMGToolSet.UMGToolSet" })
umg_capabilities()   # listener second
```

Returns class presence (`WidgetBlueprint`, `UMGToolSet`, `MVVMEditorSubsystem`, …), known UMGToolSet tool names, and notes. **Never** call from `execute_python`:

- `ToolsetRegistry.get_all_toolset_json_schemas()`
- `ToolsetRegistry.get_toolset_json_schema(...)`

Those dumps hard-crash UnrealEditorFortnite (`EXCEPTION_ACCESS_VIOLATION`). The umg_* tools call `execute_tool` with **small known payloads only**.

Also: `uefn_editor_python_hints(topic="umg")`.

### Tool map

| Tool | Job |
|------|-----|
| `umg_capabilities` | Probe classes and toolsets |
| `list_widget_classes` / `get_widget_class_info` | Palette. Call before a class name |
| `build_widget_tree` | Nested `{class, name, slot, properties, children}`. One compile |
| `set_widget_slot` | Anchors, offsets, alignment, ZOrder, padding, grid |
| `list_named_slots` / `set_named_slot_content` | Named slot fill |
| `get_widget_blueprint_info` | Tree, `slots`, animation key counts, `verse_fields`, `view_bindings` |
| `create_widget_animation` / `add_animation_keys` / `list_widget_animations` | Opacity, Color, Transform keys |
| `add_verse_field` / `list_verse_fields` | bool, int, float, string, message, color, color_alpha, texture, material, **event** (42.30, ≤1 bool/int/float param). `logic` → bool. Returns `compiled` and `verse_ready` (it opens the widget's editor once per session so fields reach Verse and click bindings save — 42.30) |
| `edit_verse_field` / `duplicate_verse_field` / `remove_verse_field` | Retype, re-default, rename, copy, delete (42.30) |
| `list_verse_field_types` | Field and event-parameter types this build accepts |
| `bind_verse_field` | Verse field → widget property; `mode` OneWayToDestination (default) / TwoWay / OneTime… |
| `bind_widget_event` | Custom Button `OnButtonClicked` / `OnButtonHighlight` / `OnButtonUnhighlight` → a Verse field (event, bool or int). `OnClicked` fails to compile in 42.30 and is remapped. Reaches into a child: `Main_Button.OnButtonClicked`. A path that binds nothing raises; a repeat returns `already_bound`; `sends` is what the event passes (new bindings send 0) |
| `list_widget_bindings` | Property `bindings` and click `events` (source path → field, `sends`) |
| `set_widget_property` | Any property on a widget, slot or class default object (Epic ObjectTools). `listed_properties` gives each value format; a wrong name fails |
| `list_bindable_properties` | Destination and event names |

### Recommended agent flow

Follow `verse_ui_kit` for what to build; this is the tool order.

1. `ducky_get_status`. Epic `unreal__*` when `epic_mcp_online`. Listener tools otherwise. Tool coverage changes between UEFN versions — `unreal__describe_toolset` before deciding a tool can't do something.
2. Find the Verse UI Kit: `search_assets("UW_Button_Basic")` (kit root = the path up to `/VerseUIKit/`). Start from its `UW_*_Example` screen or composite.
3. Look before you change: `get_widget_blueprint_info`, `list_verse_fields`, `list_widget_bindings` on every widget you will touch; `get_referencers` before editing a kit widget (ask the user first).
4. `list_widget_classes` (kit widgets come back as `UW_*_C` paths).
5. `build_widget_tree` (`verse_ui_kit` / `umg_recipes`). Folder `""` pins `{content_root}/UI`. Never invent `/Game/UI`; never build inside the kit folder.
6. `create_widget_animation` + `add_animation_keys` (your widgets only).
7. `add_verse_field` + `bind_verse_field` + `bind_widget_event` (kit: one shared int event per control group, bound to each child's inner button).
8. Localizable text and Desired Focus with `set_widget_property` (`verse_ui_kit` — Editor steps).
9. `get_widget_blueprint_info` must show anchors, `z_order`, key counts, and `view_bindings.binding_count`.
10. Save only what you changed (the UMG tools save each widget they compile; `save_asset(path)` for anything else — never a blanket save), then Verse build, then `list_verse_types(digest="assets")`. Device: `verse_template_apply("umg_widget")`.
11. `validate_uefn_asset` on each changed widget, then list the manual steps for the user.

### Epic toolsets behind these tools (42.30)

`VerseFieldsToolset` (AddVerseField with `spec{type, eventParameterTypes, defaultValue, visibility,
writeAccess, bIsVar}`, EditVerseField, DuplicateVerseField, RemoveVerseField, ListVerseFields,
GetSupportedVerseFieldTypes, BindWidgetPropertyToVerseField), `MVVMToolset` (CreateViewBinding,
CreateViewEventBinding, SetBindingMode, RemoveWidgetViewBinding, ListWidgetViewEvents, ViewModels,
FixupMVVMData), `UMGToolSet` (AddWidget, WrapWidgets, MoveWidget, RenameWidget, Replace…,
Add/Move/RemoveUIComponent, CompileWidgetBlueprint), `WidgetAnimationToolset` (create, rename,
length, AddWidgetToAnimation, RemoveWidgetBinding — 42.30 fixed it returning true for a binding
that did not exist). Full list: uefn `epic_mcp`. Prefer the Ducky tools above; they compile and
report errors.

### In-editor preview (v42.20)

Preview and interact with widgets **in the UMG editor** — do not Launch Session
just to see an animation play or button text update. Multiple in-world UMG
instances of the same class now all show Verse-bound values (pre-42.20 only
the first instance did).

### What the tools write

Tree, canvas anchors, ZOrder, image brushes, opacity/color/transform keys, Verse fields including `event` (42.30), and event→field bindings that survive a save + reload (the field tools open the widget's editor once first — without that, 42.30 saves the binding with no target). Material-parameter MovieScene tracks are not exposed; use a Verse float and `Conv_SetScalarParameter`.

Never `get_editor_property` on `WidgetTree`. Never dump a toolset JSON schema. Never patch `.uasset` bytes.

Epic's own tools, when you call them through `unreal__call_tool`:

- `editor_toolset.toolsets.object.ObjectTools`: `list_properties` before `set_properties` (`instance` + `values` as a JSON string). A wrong property name fails the call in 42.30.
- `save_assets` always gets the paths you changed. An empty list saves every unsaved asset in the project, including other people's work.
- Overrides that save and compile but fail asset validation: `isFocusable` on buttons, `Margin` on text blocks. Pad the slot instead.
- A call that hangs for minutes usually means an editor dialog is open (often revision control) — ask the user to check the editor.

### Runtime is still Verse

MCP tools edit **assets**. Showing UI in-game is always:

`GetPlayerUI[Player].AddWidget(MyUW, player_ui_slot{…})`

See `umg_widgets`.
