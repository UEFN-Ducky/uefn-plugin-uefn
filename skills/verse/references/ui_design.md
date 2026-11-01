---
description: "Game UI design craft for UEFN — make every HUD, menu, shop and popup look designed, not AI-made: a five-line direction from the game, nine passes (spacing, color, icons, copy, type, layout, details, visuals, motion) mapped to UMG / Verse UI Kit, game exceptions (readable over the world, safe zone, gamepad, touch, rarity colors), signs of slop and a done checklist. Adapted from unslop by Damir Sokolovsky (CC BY 4.0)"
metadata:
  order: 58
  label: "UI design — make game UI look designed"
  default_enabled: false
  load_condition: "Designing, building, polishing or reviewing any UEFN UI — HUD, menu, shop, inventory, dialog, toast, scoreboard — before choosing its layout, colors, text or animations"
---

## UI design — make game UI look designed

The mechanics live in `verse_ui_kit` and the `umg_*` files. This file is the taste: which size, which color, which word, and when a screen is done. Load it before you lay out a screen, and run its checklist before you report the screen finished.

AI-made game UI fails the same way every time: every panel glows, every label shouts `!!`, five shades of purple, a pulsing button, spacing typed at random, and a HUD that could belong to any island. Craft keeps the chrome quiet and puts the richness into the one thing the player must read right now.

Adapted from **unslop** by Damir Sokolovsky ([@heydamir](https://x.com/heydamir), https://github.com/heydamir/unslop), CC BY 4.0. Keep this credit in copies. Web and plugin-panel UI use the original: `skill_read_subskill("agent-skills", "unslop")`.

### Direction (write it before building)

Five short lines, taken from the game itself, never from what is trending. Put them in the plan step or the reply before the first widget.

- **Game.** What the player does, in one sentence (`race hover-carts through a flooded city`).
- **Character.** Two or three concrete words (`loud, quick, a bit silly` or `tense, quiet, cold`). Not allowed: clean, modern, sleek, epic, premium.
- **World.** The place or material the island belongs to. It tints the panels and picks the accent: a pirate island near rope, brass and sea; a sci-fi arena near cockpit glass and amber warning lights; a cozy farm near wood and paper.
- **Moments.** One or two places on screen that get rich color and detail: the round timer, the item card that just dropped, the boss health bar, the shop's featured item. Everything else is quiet.
- **Signature.** One small detail only this game would have, used everywhere it fits and nowhere else: coins stamped like doubloons, a fuel-gauge needle on every progress bar, keycap-style input prompts.

If the island already has a logo, colors or a font that are not slop, keep them and build around them.

### Game exceptions (where web rules don't apply)

| Web rule | In a UEFN game |
|---|---|
| Depth from surface steps, no shadows | Text and icons over the 3D world need a backing panel (ramp color at 60–85 % opacity) or a soft dark shadow/outline. Readability beats purity. |
| No uppercase, weights 400–500 | Fortnite's own voice is heavy uppercase display type. Use it for **titles, big numbers and one call to action** only. Labels, descriptions and lists stay sentence case at a normal weight. |
| Purple is slop | Rarity colors are meaning, not decoration: common grey, uncommon green, rare blue, epic purple, legendary gold. Use them only on items, and only as that rarity. |
| No glow | One glow is allowed where it means something live: an ability that is ready, an objective that is active right now. Never on frames, buttons or headers. |
| Emoji become line icons | UEFN fonts don't draw emoji at all. Every icon is a texture (`umg_ui_materials`), one set, one size, tinted to its text role. |
| No looping motion | A loop is allowed on something truly live: a timer under 10 s, a capture in progress, an incoming-damage edge. Nothing else breathes or pulses. |
| Sidebar 240–280, dense rows | Players read at TV distance with a gamepad: body text about 24 px or larger at 1080p, touch targets about 64 px, rows 56–72 tall in menus (`verse_ui_kit` — Rules SHOULD). |

### The nine passes

Finish each pass across the whole screen before the next. Values are UMG units at 1080p (slot `Padding`, `SizeBox` sizes, text size).

1. **Spacing.** Every padding, gap and fixed size is a multiple of 4 (8 is the usual step on HUDs). Same thing, same size: every row in a list has one height, every card in a grid one padding. Space inside a group is smaller than space between groups. Edge-anchored HUD clusters sit inside the `SafeZone` (`umg_layout`) with 24–48 between clusters. Padding goes on the slot, never as a text `Margin` (that fails validation, `umg_style`).
2. **Color.** One neutral ramp tinted toward the world: deepest panel, panel, raised (selected row / input), hairline (text at 8 %), and three text roles: primary, secondary, muted. One accent for the primary action, the selection and the one number that matters. Semantic colors only for meaning (heal green, damage red, rarity). No hue-to-hue gradients, gradient text or colored glows on chrome. Colors live in the kit's slot material instances (`M_UI_Rectangle` parameters, `umg_ui_materials`) or as Verse `color` constants in one place, never typed per widget.
3. **Icons.** One icon set, one size (32 or 48 on HUDs, 24 in lists), tinted to the text role, never their own colors. Same icon box width in every row so labels line up. Drop icons that add nothing.
4. **Copy.** Every word is a `<localizes>` message or localizable UMG text (`umg_style`). Titles name the thing (`Shop`, `Round 3`), not a greeting. No `!!`, no exclamation marks except one real win moment (`Victory`). Short labels: `Buy`, `Equip`, `Back`. A change says what it compares to (`+250 since last round`). No hype words (epic, ultimate, insane) unless that is literally the item's name. Mock data looks real: `1,240 coins`, never `123456`.
5. **Type.** The kit's fonts or the island's real brand font. Few sizes: about 24 body, 32 labels on HUD, 48–64 key figures, 72–96 one hero title. Hierarchy from size and color, not from making everything heavy. Numbers in one format across the screen (all `1,240` or all `1.2K`, never both), and counters keep their width while they change.
6. **Layout.** HUD: corners and edges only, the center stays clear for the crosshair and the action; the most important live value takes the top-center or the corner the player's eye already visits. Menus: one primary action and at most one secondary per screen; `Back` closes (`umg_navigation`). Lists and grids use `StackBox` / grid slots (`umg_layout`), never hand-placed offsets. Vary the sizes: one featured item card bigger than the rest beats a uniform grid.
7. **Details.** Nested radius: inner corner = outer corner − padding, never below 4 (set on the slot material's corner parameter). Controls 8–12, cards 12–16, panels 16–24; not everything a pill. Counts and meta are quiet muted text, not glowing badges. Hover and gamepad focus look the same and stay inside the palette (`verse_ui_kit`). State is never color alone: pair it with an icon, a check or position. The signature detail appears where it belongs.
8. **Visuals.** No filler: no glossy orbs, nebula backdrops, circuit lines or floating cubes behind a menu. The moment is a real thing from the game: the item render, the character portrait, the map. Generated art only for key art, a loading screen or an empty state, and only with the user's spend approval (`imk_gateway_generate`, `ducky_generate_image`). Never bake words into textures.
9. **Motion.** Widget animations (`umg_animations`) only explain something: a panel fades and rises 8–12 px on open (200–300 ms), a press scales to 0.97 (100–150 ms), a number tweens when it changes, a toast slides in from the edge it lives on. One ease-out curve. At most one entrance per screen, with a small stagger (40–60 ms, at most six items). No bounce, no looping pulse on things that aren't live, no `hover:scale` on whole cards.

### Signs of slop (audit before and after)

- Purple-to-blue or neon gradients on panels, buttons or the selected row
- Every panel with a colored glow or outline; nothing stands out because everything does
- Five near-identical tints for text
- `!!`, `WELCOME BACK, PLAYER!`, `Unlock EPIC rewards!!` and uppercase tracked labels on every line
- Emoji or `[ICON]` placeholders where an icon texture should be
- Spacing like 13, 7, 31; rows of different heights in one list
- Mixed number formats (`1,240` next to `1.2K` next to `01240`)
- A pulsing or breathing button that isn't time-critical; everything flying in from different sides
- A uniform grid of identical cards with the same glow
- A HUD that would still fit if you swapped the island's name for another island's

### Done checklist

- [ ] The five-line direction is written and every pass follows it
- [ ] All spacing on the 4 scale; equal things have equal sizes; HUD inside the safe zone, center clear
- [ ] One tinted ramp, three text roles, one accent; semantic and rarity colors only where they mean something
- [ ] Text readable over the brightest and darkest parts of the island (backing panel or shadow)
- [ ] No emoji, one icon set at one size
- [ ] All text localizable; no `!!`, no greeting titles, no hype words, plausible numbers in one format
- [ ] Nested radii add up; focus and hover are visible and identical
- [ ] No filler visuals; no looping motion on things that aren't live; one entrance per screen
- [ ] Looked at it: a screenshot of the screen in the designer or a session (`take_high_res_screenshot`, or `playtester_check` in game) was compared with this list
- [ ] Template check: swap the island's name for another's. Still fits? Push the world, the moment and the signature harder

Then run the `verse_ui_kit` Done checklist for the mechanics.
