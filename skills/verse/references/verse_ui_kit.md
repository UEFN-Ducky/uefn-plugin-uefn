---
description: "Epic's Verse UI Kit, with Epic's own rules for agents — the default for all UEFN UI: kit widgets inside your own UW_ screen, custom (kit) buttons only, styling through named slots, one shared int click event per control group, ui_helper_function_library driver, focus / Back / gamepad rules, naming, editor steps with Ducky tools, manual steps, done checklist"
metadata:
  order: 59
  label: "Epic Verse UI Kit — default for all UI"
  default_enabled: false
  load_condition: "Building or changing any UEFN UI — HUD, menu, shop, settings, dialog, list, grid, toast, button or input prompt — or the project has a VerseUIKit folder / UW_Button_Basic"
---

## Epic Verse UI Kit — default for all UI

The Verse UI Kit is Epic's set of UMG widgets plus small Verse classes. You build every screen in UMG from the kit's widgets and drive it from Verse. This page is Epic's own guidance for agents using the kit, with the Ducky tool for each step. The other UI subskills (`umg_*`, `ui`, the `sys_*` canvas files) follow it; where they differ, this page wins.

**The kit's assets win over this page.** People edit UMG by hand and kit updates change widgets. When an asset disagrees with this page, trust the asset and tell the user what differs. The kit ships its own `AGENTS.md` in its root folder — read it (`workspace_read_file`) when it is there; it is the newest copy of these rules. Don't edit it (kit updates replace it); project notes go in the project's own instructions.

### Buttons are always custom (HARD)

Every clickable control is a kit button (`UW_Button_Basic`, `UW_Button_Toggle`, the checkbox / toggle / radio controls, `UW_Shared_CloseButton`) or a small widget of your own built on one. Inside, the kit's buttons are UEFN Custom Buttons (`UIFrameworkCustomButtonWidget`) — that is how Epic builds them and how we build them.

Never:

- UMG preset buttons `LoudButton` / `QuietButton` / `RegularButton` (`VerseFortniteUIFrameworkButton_Loud` / `_Quiet` / `_Regular`). `build_widget_tree` refuses them.
- Verse `button_loud` / `button_quiet` / `button_regular`.

No kit in the project yet: a UEFN `CustomButton` with your own image slots (`umg_layout`). A screen that must be built in Verse code: the chrome-less Verse `button` (`sys_custom_buttons`).

### Before you start

1. **Find the kit.** `search_assets("UW_Button_Basic")`. The path up to `/VerseUIKit/` is the kit root. UEFN mounts projects under their own root, not `/Game`. Verse names the same folders as modules: `VerseUIKit.Widgets.Buttons.ToggleButton`.
   Not found: tell the user the project has no Verse UI Kit and ask them to add it. Never copy or imitate kit widgets by hand. Until it is added, build with UMG Custom Buttons by these same rules (`umg_widgets`).
2. **Check the tools.** `ducky_get_status` → `epic_mcp_online`. With UEFN open and Epic's editor tools online you edit widgets, bindings and materials yourself (*Editor steps*). Without them, write the Verse and give the user numbered steps for the UMG work. Tool coverage changes between UEFN versions: check `unreal__describe_toolset` before deciding a tool can't do something. Server unreachable: tell the user — don't treat the task as unsupported.
3. **Look before you change.** Read the widget's tree, Verse fields and bindings first: `get_widget_blueprint_info`, `list_verse_fields`, `list_widget_bindings`.
4. **Start from an example.** Every kit widget has a working example: a `UW_*_Example` screen (or the composite itself) and a Verse class in `Verse/<Category>/*_example.verse` under the kit root. Copy one into your folder (`duplicate_asset`); never start blank.

### Rules — MUST

Breaking these gives broken or unusable UI, or damages the user's project.

- **Gamepad, keyboard and mouse.** Every interactive screen gives focus to its first control when it opens (or the safest default, such as Cancel on a destructive confirm). Every control is reachable by gamepad and arrow keys, focus is always visible, and Back closes the screen. See *Input*.
- **Build your own screens; leave kit widgets alone.** Put kit widgets inside your own screen and style them from there. Edit a kit widget only when the user asks — then `get_referencers` and update every screen that uses it.
- **No hidden values.** Never set Verse fields or properties directly on a nested widget instance. UEFN doesn't show those in the Details panel, so nobody can see or change them. Use a named slot, a Verse field on your screen bound to the child, or Verse code.
- **Style through slots.** Change a kit widget's look by filling its named slots with your own images (material instances). Styles then preview in the designer and the kit stays reusable.
- **Player-facing text is localizable.** Text set from Verse is a `<localizes>` message. Text typed in UMG goes in text blocks or `message` fields, never baked into textures (`localization` / `ui_ready`).
- **Leave it working.** Compile each changed widget, save it, then build Verse — the compiler reads *saved* assets. Report errors; never hide them. "Unknown member" for a field that exists and is saved: open that widget once (`open_asset_in_uefn`) and build again (`umg_verse_field_events`); still failing → stop and tell the user. Never move or rename assets to work around it.
- **Ask first** before deleting assets, renaming named slots, restructuring a kit widget, or changing project settings (such as turning on Python for the editor tools). An asset with unsaved changes you didn't make, or checked out by someone else: stop and ask. Save only what you changed.
- **Say what you couldn't do.** List every manual step (*Manual steps*) instead of leaving work half-done.

### Rules — SHOULD

- Hover and gamepad focus look the same (the kit's shared highlight does both).
- Focus order follows reading order, and focus lands somewhere sensible after a screen or page changes.
- Input prompts use ActionWidgets, so they show the right glyph for the player's device.
- Important UI stays inside the safe zone (about 5 % from each screen edge). Touch targets are at least ~64 px. Body text is about 24 px or larger, so it reads on a TV at 1080p.
- Don't show state by colour alone; pair it with shape, position or an icon.
- Follow the project's naming. If it has none, use the kit's (*Naming*).
- Keep Verse fields, bindings and Verse classes to the minimum the screen needs.

### How the kit works

| Piece | What it is |
|-------|------------|
| Kit widget | A reusable control in `Widgets/<Category>/` (Buttons, Inputs, Containers, Feedback, Shared). Verse fields for its state (`IsActive`, `ValueText`), named slots for its art |
| Screen | Your widget that lays out kit widgets. It owns the Verse fields your code talks to and binds them to its children (`IsToggleButton1Active` → `ToggleButton1.IsActive`) |
| Composite | A ready-made screen or panel in `Widgets/Composites/` (dialog, settings panel, item card, menu, list, grid). Use it whole or copy it as a start. Repeated buttons in the menu, list and grid are small widgets built on kit buttons, so one edit restyles every copy |
| Verse driver | A small class that creates the screen, puts it on screen, listens to its events and updates its fields |

- **Clicks.** A parent can't listen to a child's *Verse* event. Bind the child's inner native button to one **shared int event** on your screen instead, each child sending its own number: `OnToggleButtonClicked(1)`, `(2)`, … The inner button's path depends on the widget (`ToggleButton1.Main_Button.OnButtonClicked`, `Button1.Root_Button.OnButtonClicked`) — read it from the child's widget tree.
- **Counting from 1.** Option numbers start at 1; `0` means "nothing picked".
- **Showing a choice.** Prefer one `Is<Child>Selected` bool per child, bound directly and set from Verse — it needs no manual steps. One int field through `Conv_IntegerToBoolInterval` (both bounds set to the child's number) means fewer fields, but each bound is a manual step.
- **Verse modules.** Code folders are internal modules unless `ui_modules.verse` (kit root) declares them `<public>`. `VerseUIKit.Verse` (the helper library) and `VerseUIKit.Verse.Feedback` (the toast) are public; the kit's other `Verse/` folders give error 3593 from your own folder. If `using` your own widget's folder fails with 3593, declare that folder a public module the way `ui_modules.verse` does.
- **Verse driver.** Reuse `ui_helper_function_library` (in the kit's `Verse/` folder, `using { VerseUIKit.Verse }`) for showing widgets, focus, input mappings and cleaning up. Read that file for the full list before writing your own helper.

### Input

- Call `Helper.FocusWidgetForPlayer(Player, Widget)` **after** the widget is on screen, and set the screen's **Desired Focus Widget** (Class Defaults) to its first control.
- Menus turn on navigation with `Helper.AddInputMappingToPlayer(Player, UI.MenuNavigationMapping)` (`using { /Verse.org/Input }` and `{ /Verse.org/Input/UI }`). `Helper.ClearAllForPlayer` turns it off.
- **Back closes the screen.** Put the kit's `UW_Shared_CloseButton` in the screen's UMG and give the screen an `OnCloseClicked` event. Bind both of the close button's inner buttons to it: `<Child>.Close_Button.Root_Button.OnButtonClicked` (mouse, touch, A) and `<Child>.CloseAction_Button.OnButtonClicked` (Back). Then listen to `OnCloseClicked` in Verse.
- The Back prompt only fires while focus is inside the widget that holds it. A close button added *beside* a screen from Verse also needs a Verse listener: inside `if (PlayerInput := GetPlayerInput[Player]):` call `Helper.SubscribeToEvent(Player, PlayerInput.GetInputEvents(UI.Back).EndDetectEvent, OnBack)`. Listening for the release means the screen that comes back can't catch the same press.
- Tab rows and pagers send `-1` / `+1` through an `OnNavigateTab(int)` / `OnNavigatePage(int)` event, with `PrevTab_Action` / `NextTab_Action` ActionWidgets for the shoulder buttons.
- After anything that changes which controls exist (tab, page, filter), call `FocusWidgetForPlayer` again, or focus can be left on a control that just disappeared.
- Collapse empty rows so navigation skips them: bind a bool field to `Visibility` (the default conversion shows on `true` and collapses on `false`). Never leave a focusable control with no visible content.
- HUD elements and toasts use `ui_input_mode.None`, so they never steal input or block clicks.
- UI shown during gameplay uses gameplay input (`Character.*` mappings), not menu navigation. If you freeze the player (`Helper.HoldPlayerStill`), release them (`Helper.ReleasePlayer`) on **every** way out.
- Touch: `Helper.WatchInputMethodForPlayer` reports input-method changes, so a screen can switch to a touch layout (an `IsMobile` field).

### Recipe — build a screen from kit widgets

1. Create the screen in your own folder, named by *Naming*: `build_widget_tree` (omit `folder` → `{content_root}/UI`). Never inside the kit folder.
2. Add kit widgets by their class path from `list_widget_classes` (`…/VerseUIKit/Widgets/Buttons/UW_Button_Toggle.UW_Button_Toggle_C`). Lay out with `StackBox` (set `Orientation`), `Overlay`, `SizeBox`, `ScaleBox`, `ScrollBox` and `WrapBox` — UEFN has no Vertical/HorizontalBox.
3. Put labels beside label-free controls (checkbox, toggle, radio) in a horizontal `StackBox`.
4. Add Verse fields for the state you drive (`IsToggleButton1Active`) with `add_verse_field`, and bind each to its child with `bind_verse_field` (destination names from `list_bindable_properties` on that child).
5. Add one shared int event per control group: `add_verse_field(widget_path, "OnToggleButtonClicked", "event", event_parameters=["int"])`. Verse then sees `OnToggleButtonClicked<public>:event(tuple(int))`. For a no-parameter event such as `OnCloseClicked`, `duplicate_verse_field` it and clear the parameter with `edit_verse_field(..., event_parameters=[])`. If this UEFN build refuses `event` fields, `duplicate_verse_field` an existing event field and rename it (start the screen as a copy of a widget that has one).
   Bind each child's inner button to it — the inner path from step *Clicks*: `bind_widget_event(widget_path, "ToggleButton1", "Main_Button.OnButtonClicked", "OnToggleButtonClicked")`. Nested paths work two levels deep too (`CloseButton1` + `Close_Button.Root_Button.OnButtonClicked`). Check `compiled`, then confirm with `list_widget_bindings` → `events` (source path, destination field, `sends`). A path that names no widget or event raises "nothing was bound". On an older Ducky it returns `"event": "None"` with `compiled: true` instead — that is a failed bind. Binding the same click again returns `already_bound`. Every new binding sends 0 (`sends`, `manual_step` in the result); the number each child sends is always a manual step (*Manual steps*).
6. Add `UW_Shared_CloseButton` and wire it to an `OnCloseClicked` event (*Input*).
7. Set Desired Focus to the first control (*Editor steps*). The UMG tools compile and save each change and return `compiled`.

### Recipe — style a kit widget in your screen

1. Find the widget's named slots (`NamedSlot` entries in its tree: `get_widget_blueprint_info`, `list_named_slots`).
2. Create one material instance per state image from `/FNE_UI/Systems/_Materials/Shapes/M_UI_Rectangle` (ships with UEFN): `create_material_instance`. Set `StrokeTransparency` and `FillTransparency` to 1, then colour (`Color1`), shape (`CornerRoundness`) and outline (`StrokeColor1`, `StrokeThickness`) with `set_material_instance_scalar` / `set_material_instance_vector`. Reuse a composite's MIs if one already fits.
3. Put an `Image` in each slot and set its brush to the MI (`brush_material`).
4. Check the result in the designer. It shows field *defaults*, not bound states.

### Recipe — drive a screen from Verse (minimal pattern)

```verse
using { /UnrealEngine.com/Temporary/UI }
using { /Verse.org/Input }
using { /Verse.org/Input/UI }
using { /Verse.org/Simulation }
using { VerseUIKit.Verse }   # ui_helper_function_library
using { MyProject.UI.Settings }   # the module of the folder holding UW_Settings_Screen

# Shows the settings screen, flips its switches when clicked, and closes on Back.
settings_screen := class:

    var Widget<private> : UW_Settings_Screen = UW_Settings_Screen{}
    var MaybePlayer<private> : ?player = false

    Helper<private> : ui_helper_function_library = ui_helper_function_library{}

    # Puts a fresh screen on the player's display, with gamepad focus and menu navigation.
    Show<public>(Player : player) : void =
        set MaybePlayer = option{Player}
        set Widget = UW_Settings_Screen{}
        Helper.ShowFullScreen(Player, Widget)
        Helper.AddInputMappingToPlayer(Player, UI.MenuNavigationMapping)
        Helper.SubscribeToEvent(Player, Widget.OnToggleButtonClicked, OnToggleButtonClicked)
        Helper.SubscribeToEvent(Player, Widget.OnCloseClicked, OnCloseClicked)
        Helper.FocusWidgetForPlayer(Player, Widget)

    # Takes the screen down, turns off menu navigation and stops listening to it.
    Hide<public>(Player : player) : void =
        Helper.ClearAllForPlayer(Player)

    # Runs when any switch is clicked. The number says which one.
    OnToggleButtonClicked<private>(ToggleButton : tuple(int)) : void =
        case (ToggleButton(0)):
            1 => set Widget.IsToggleButton1Active = Helper.InvertLogic(Widget.IsToggleButton1Active)
            2 => set Widget.IsToggleButton2Active = Helper.InvertLogic(Widget.IsToggleButton2Active)
            _ => {}

    # Runs when the player presses Back or clicks the close button.
    OnCloseClicked<private>(Event : tuple()) : void =
        if (Player := MaybePlayer?):
            Hide(Player)
```

`Helper.SubscribeToEvent` is the kit's helper — UMG event fields themselves have no `Subscribe` on 42.x; on 43.00 `event(t)` is subscribable, so `Widget.OnX.Subscribe(Handler)` also works (`events_subscriptions`). Without the kit, await them in a loop (`umg_verse_field_events`).

**Show a toast:** `ui_feedback_toast{}.ShowSuccessToast(Player, Heading, Body)` with `using { VerseUIKit.Verse.Feedback }`. `ShowToast` takes `toast_settings` for icon, colour, duration and placement.

### Naming

Use the project's own conventions first. Otherwise the kit's:

- Widgets `UW_<Category>_<Name>` (`UW_Settings_Screen`); material instances `MI_UI_<Widget>_<Style>_<Part><State>`.
- Widget tree names put the role first and the type second: `Root_Overlay`, `Main_Button`, `Label_Text`. Numbered children are `ToggleButton1`, `ToggleButton2`; named slots are `<Role>_Slot`.
- Verse fields: bools `Is<Adjective>`, text ends `Text`, textures end `Texture`, events `On<Event>`. On screens, start with the child's name: `IsToggleButton1Active`, `Button1LabelText`.

### Writing Verse

- Classes and files are `snake_case`; fields, methods and messages are `PascalCase`. Mark only what other code needs `<public>`; keep the rest `<private>`.
- Subscribe with `Helper.SubscribeToEvent` so `ClearAllForPlayer` cleans up, and create a fresh widget each time a screen opens so it starts from its defaults.
- Remove debug `Print` calls before finishing.

### Editor steps

Ducky's UMG tools wrap Epic's editor toolsets and compile + save each widget they change (`umg_mcp_tools`). Epic's own tools are reachable as `unreal__*` when `epic_mcp_online`.

| Job | Ducky tool | Epic tool |
|-----|------------|-----------|
| Read a widget before changing it | `get_widget_blueprint_info`, `list_verse_fields`, `list_widget_bindings` | `GetWidgets`, `ListVerseFields`, `ListWidgetViewBindings` |
| Screens that use a kit widget | `get_referencers` | — |
| Set a property | `set_widget_property` (lists the real names first) | `EditorToolset.ObjectToolset`: `ListProperties`, then `SetProperties` (43.00 names) |
| Save | `save_asset(path)` for each asset you changed | `EditorToolset.AssetToolset` `SaveAsset` per path (42.x `save_assets`: an **empty list saved every unsaved asset in the project**) |
| Build Verse | `workspace_compile_verse` | `VerseToolset` `BuildAll` |
| Asset validation | `validate_uefn_asset` | — |

Verified in UEFN 42.30 (Oct 16 2026) with the Ducky tools, on stand-in kit buttons (a Custom Button inside a child widget): text, desired focus and the click bindings in the recipe all survive compile, save and reload.

- Read property names first: `set_widget_property` returns `listed_properties` with each name's value format. A wrong name fails the call ("could not be set: <name>").
- Some overrides save and compile but fail asset validation: `isFocusable` on buttons, `Margin` on text blocks. Pad the slot instead.
- Text blocks: the palette `Text` class. The tools add an `Image` and `ReplaceWidgetWithTemplate` it with `/Game/Valkyrie/UMG/UEFN_TextBlock.UEFN_TextBlock_C`. `build_widget_tree`'s `properties.text` writes localizable text with a fresh key. A `notes` entry "text: saved as a plain string, not localizable" means it could not — set it again. To set or change text later: `set_widget_property(widget_path, <text widget ref>, {"Text": "NSLOCTEXT(\"\", \"<unique 32-hex key>\", \"Play\")"})` — a new 32-hex key per text.
- Desired focus: `set_widget_property(widget_path, "<package>.Default__<Name>_C", {"DesiredFocusWidget": {"widgetName": "ToggleButton1"}})` — the class default object, value `{"widgetName": <child name>}`.
- `set_widget_property` fails with "Toolset 'ObjectTools.ObjectTools' not found" on older Ducky builds. Then call Epic's tool yourself: `unreal__call_tool(toolset_name="EditorToolset.ObjectToolset", tool_name="SetProperties", arguments={"instance": {"refPath": <ref>}, "values": "<JSON object as a string>"})`, then `UMGToolSet` `CompileWidgetBlueprint` and `save_asset` the widget. On those builds `build_widget_tree` text is a plain string: set every label this way.
- Renaming a named slot drops the content every parent put in it. Note each parent's content first and put it back after; never save a parent while its slot content is missing.
- A call that hangs for minutes usually means an editor dialog is open (often revision control). Ask the user to check the editor (`uefn_popups` lists open dialogs).

### Done checklist

- [ ] Widgets compile; your changed assets are saved; the Verse build has no errors.
- [ ] Asset validation passes (`validate_uefn_asset`), or you asked the user to run it.
- [ ] Desired focus is the first control (or the safest default); `FocusWidgetForPlayer` runs after showing.
- [ ] Every control is reachable by gamepad and arrow keys, with a visible highlight.
- [ ] Back closes the screen; movement and input are restored afterwards.
- [ ] Every clickable is a kit button (or one built on a Custom Button) — no Loud/Quiet/Regular buttons.
- [ ] No values set on nested instances; styling lives in slots.
- [ ] Manual steps listed for the user, plus anything you couldn't verify.

**Manual test for the user** (agents can't press buttons): open the screen with a gamepad connected; focus lands on the first control; the D-pad reaches every control; A activates; B/Back closes. Repeat with the mouse and with the arrow keys.

### Manual steps

Some values can only be set in the UEFN editor's panels. Do everything else, then list each one for the user with the widget, the binding and the value. Check first whether your tools can set it now.

- The number each child sends on a shared event (`Param0` in View Bindings; new bindings send 0). No tool can set it: the event's saved pins are read-only to Python and to ObjectTools (verified 42.30). Name each binding from `list_widget_bindings` → `events` and the number it must send.
- Conversion-function values, e.g. `Conv_IntegerToBoolInterval` bounds or a `Conv_SetScalarParameter` parameter name (View Bindings).
- Default values of `message` fields (Details panel).
- Keyframes in widget animations (Animations panel) when `add_animation_keys` can't reach the track.
