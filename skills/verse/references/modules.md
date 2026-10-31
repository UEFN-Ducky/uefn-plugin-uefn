---
description: "Project structure — module declarations, using {} imports (engine paths vs project modules), how folders map to modules, making nested and asset folders <public> (Script error 3593), module-level var rules, parse order for generic classes, moving files, and cross-file references"
metadata:
  order: 11
  label: "Modules, using & file layout"
  default_enabled: true
  load_condition: "Creating or moving .verse files, module declarations, using imports, or referencing a type/manager in another folder — ALWAYS before writing a new Verse file"
---

## Modules, `using` & file layout

Verse groups code into **modules**; `using` brings names into scope. Declare your
module tree in one place and import both engine APIs and your own modules. The
module/type names below are generic placeholders — name yours to fit your project.

### HARD RULE — folders before files

**Never dump new `.verse` files at `Content/Verse/` (or `Verse/`) root.**

| Allowed at Verse root | Everything else |
|----------------------|-----------------|
| `module_declarations.verse` (optional; module blocks + `<public>` folder declarations) | One **system folder** per concern |
| Tiny shared `helpers.verse` (optional) | Devices, managers, HUD builders, shops, … |

Canonical template folders (use these names when they fit):

| Folder | For |
|--------|-----|
| `Verse/PlayerCore/` | `player_manager`, `game_player`, persistence |
| `Verse/NPCCore/` | prey/hunter registries, NPC spawn controller |
| `Verse/Economy/` | currency / economy manager + device |
| `Verse/Progression/` | XP / levels |
| `Verse/Shop/` | shop device + canvas |
| `Verse/TimeTracker/` | playtime |
| `Verse/MatchTimer/` | match / round timer |
| `Verse/Tycoon/` | generators / tycoon |

Workflow for **new** code:

1. `workspace_list_dir("Verse")` — see what folders already exist.
2. Prefer `verse_template_list` → `verse_template_apply(id)` (creates the pack folder).
3. Hand-write: `workspace_write_file("Verse/<System>/<file>.verse", …)` — parents are created automatically.
4. A new folder is a new module automatically — nothing to declare.
5. Load this file (`modules`) whenever you organize across folders.

Wrong: `Verse/economy_shop.verse`, `Verse/shop_hud_device.verse`, `Verse/game_session.verse`  
Right: `Verse/Shop/economy_shop.verse`, `Verse/Shop/shop_hud_device.verse`, `Verse/PlayerCore/game_session.verse`

### `using` — two kinds of import

```verse
# Engine / standard-library paths (leading slash, vendor domain)
using { /Verse.org/Simulation }
using { /Fortnite.com/Devices }
using { /Fortnite.com/Characters }
using { /UnrealEngine.com/Temporary/SpatialMath }
using { /Verse.org/Random }
using { /Fortnite.com/UI }

# Your own modules (no leading slash — resolved by module name)
using { PlayerDevices }
using { Services.PlayerProgressionManager }
using { GameDevices.Gameplay }
```

Rules of thumb:

- **Leading `/`** = engine/stdlib (`/Fortnite.com/…`, `/UnrealEngine.com/…`,
  `/Verse.org/…`). Which one provides a type is in the digests — the `using`
  paths there are exactly what you import.
- **No leading `/`** = one of your own modules (e.g. `PlayerDevices`,
  `GameDevices.Gameplay`). Import the module that *contains* the type/manager
  you're calling.
- Missing a `using` → "unknown identifier" for a name that exists. Add the import
  the digest/source shows.

### Common engine imports (what each unlocks)

| `using` | Gives you |
|---------|-----------|
| `/Verse.org/Simulation` | core sim, events, `Sleep`, `spawn` machinery |
| `/Fortnite.com/Devices` | `creative_device`, `trigger_device`, granters, buttons |
| `/Fortnite.com/Characters` | `fort_character`, elimination/damage events |
| `/Fortnite.com/UI` + `/UnrealEngine.com/Temporary/UI` | canvas & widgets |
| `/UnrealEngine.com/Temporary/SpatialMath` | `vector3`, `rotation`, `Distance` |
| `/UnrealEngine.com/Marketplace` | entitlements, `MakePriceVBucks`, `BuyOffer`, `GrantEntitlement` (v42.20 — **not** island Coins; `/Fortnite.com/Marketplace` is deprecated aliases) |

`/UnrealEngine.com/Conversations` (module since 40.00; mainstream in 42.30) — `persona_component`, `ai_session`, `prompt_binding_definition`, voices, `ai_error`s, `@ai_description` (`sys_conversations`).
| `/Verse.org/Chat` | `voice_channel` (v42.20), `text_channel` + `text_message_style` (v42.40), `AddChatChannel` / `GetTextChannels` on the simulation entity — `sys_chat_channels`, `sys_text_chat` |
| `/Verse.org/Random` | `GetRandomInt`, random selection |
| `/Verse.org/Colors` (+ `/NamedColors`) | `color`, named colors |

### Folders ARE modules

Every folder under `Content/Verse` is **implicitly** a module named after the
folder, and a `.verse` file's code belongs to the module of the folder it sits in
(`Verse/PlayerCore/*.verse` → `using { PlayerCore }`;
`Verse/GameDevices/Gameplay/*.verse` → `using { GameDevices.Gameplay }`). This is
how every shipped template pack works: no `:= module` line anywhere, just folders.
Top-level `Verse/*` folders reach each other with no declaration.

Explicit `Name := module:` blocks are for **sub-modules inside one file**
(grouping helpers), a module that has no folder, or making a folder public:

```verse
# inside a single file, optional grouping
Helpers<public> := module:
    Clamp01(X : float)<computes> : float = Max(0.0, Min(1.0, X))
```

- Only `<public>` members cross folder/module boundaries — mark them explicitly.
- Reference a nested folder by dotted path in `using`:
  `using { GameDevices.Gameplay.UI }`.

### Make a folder `<public>` when another folder cannot reach it (Script error 3593)

Declare the folder `<public>` in a `.verse` file of the folder **that contains
it** — normally `module_declarations.verse` — nesting the path down from that
file's folder. It merges with the real folder; it is **not** a duplicate
definition (an island declaring 37 existing folders this way builds clean).

```verse
# Content/Verse/module_declarations.verse
ArmoryWeapons<public> := module:          # Content/Verse/ArmoryWeapons (prefab assets)
GameDevices<public> := module:
    Gameplay<public> := module:
        UI<public> := module:             # Content/Verse/GameDevices/Gameplay/UI
```

```verse
# Content/modules.verse — for folders beside Verse/ (Content/SceneGraph/CustomWeapons)
SceneGraph<public> := module:
    CustomWeapons<public> := module:
```

- Never put the declaration inside the folder it names — a file in
  `Verse/PlayerCore/` declaring `PlayerCore<public> := module:` creates
  `PlayerCore.PlayerCore`.
- **Asset folders need it.** Assets.digest generates every asset folder module
  with no access specifier (`Materials := module:`), so a nested folder of
  materials, meshes or prefabs (`EP_*`) gives 3593 from your code until each
  folder on its path is declared `<public>`. The asset classes themselves are
  `<scoped>` to the whole island and need nothing. Custom weapons:
  `sys_owned_weapons`.
- Build Verse after adding the declaration, then `search_verse_digest` the
  asset to copy its exact path.

### Cross-file references

Once you `using` a module, its `<public>` types, functions, and module-level
values are in scope by name:

```verse
using { PlayerDevices }                 # brings in player_manager, PlayerStatsMap, …
# …
@editable MyPlayerManager : player_manager = player_manager{}
AllPlayers := MyPlayerManager.GetAllGamePlayers()
```

- Only `<public>` members cross module boundaries — mark them explicitly.
- A module-level `var` must be a `weak_map`: `var PlayerStatsMap<public> :
  weak_map(player, player_stats) = map{}` (persistent) or `weak_map(session, t)`
  (one value for this match, not saved). A plain `var Count : int` outside a class
  is 3502 "Module-scoped `var` must have `weak_map` type". Session state belongs on a manager device instead — reach for
  `weak_map(session, …)` only when there is no device to hold it.
- Imported module-level `var`s are shared global state. Keep them `<public>` only
  when other systems truly need them; persistent ones count toward the four-map
  cap (`persistence`).

### Generic classes — classes above functions

A function placed above a generic (parametric) class **in the same file** fails
with 3502 "Can't access a function from a preceding type". List the generic
classes first, helpers below them (`classes`). Folder order does not matter: a
folder that sorts before `Archetypes/` uses its generic classes without error
(verified with verse-lsp, 42.40). Keeping them in one shared folder is for
organisation.

### Moving files

A placed device's class path is its folder path. Moving or renaming its `.verse`
file breaks every placed instance and its wiring — choose the folder before the
first build (`devices`). Plain classes and helpers can move freely; rebuild after.

### File organization conventions

- One system per folder, one `creative_device` subclass per gameplay concern.
- Split UI construction into a `*_canvas` / `*_canvas_builder` file **in that same system folder**, separate from logic.
- Keep persistence types + the shared `weak_map` together in `PlayerCore` (or your player folder).
- Put small reusable functions/wrappers in a shared `helpers.verse` at Verse root only when many systems need them — not every one-off utility.
