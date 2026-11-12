---
description: "Writing a persona for a talking NPC: what goes in Personality and Knowledge, a layout that works (identity, voice, what it knows, what it does in the game, rules), game facts it must be told, scripted lines, how it names the player, moderation, voice description, a full example and a test list"
metadata:
  order: 2
  label: "Conversations: writing the persona"
  default_enabled: false
  load_condition: "Writing or fixing a talking NPC's personality or knowledge text, an NPC that rambles, breaks character, offers things the game cannot give, or answers the wrong way; choosing or describing its voice"
---

## Writing the persona

The model plays whatever the text describes, and it knows nothing else. A vague text gives a vague character. Write this text in the editor (`setup`) and test it in the Prompt Editor; only text that must change during the game belongs in Verse (`behaviors`).

### A layout that works

Use the same headings and the same markdown every time. The model reads markdown well, and a pattern it has seen once it follows again. Bold (`**word**`) marks what matters most.

```
# Identity
You are **Mara**, the only weapons dealer on this island. You are in your forties, calm and proud of your stock.

# How you talk
Short sentences, at most two per reply. Dry humor. You never use slang.
Example: "Good eye. That one never jams."

# What you know
You sell exactly three items: a pump shotgun, a shockwave hammer and an assault rifle. They are free.
The vault behind you is locked. You do not know the code.

# What you do
When a player asks for an item you sell, say you are handing it over.
When a player asks for anything else, say you do not stock it.
If a player is rude, answer once, then stay polite.

# Rules
Never offer an item that is not in your list.
Never ask the player to repeat themselves.
```

### What each part is for

| Part | Why |
|---|---|
| Identity | A clear role, values and traits. Without it every NPC sounds the same |
| How you talk | Length limit, tone and one or two example lines. Examples set rhythm better than adjectives |
| What you know | Every game fact it may mention: stock, prices, places, other characters. It sees nothing of the level |
| What you do | The situations you expect, each with what to do. This is what lines up with your structured output (`structured_output`) |
| Rules | The few things it must never do. Say the important ones twice in different places |

### Things that are easy to miss

- **It only offers what you list.** If the shop has three items, name the three. Otherwise it invents stock your code cannot give.
- **Length:** say it ("at most two sentences"). Long replies make players wait and talk over it.
- **The player's name:** it calls the player by their outfit's name unless the text gives another name or says not to use one.
- **A line that must be said word for word:** write the line, then "Say only this, nothing else." Without that it adds its usual offers.
- **Other talking NPCs:** it knows about them only if the text says who they are.
- **Questions players always ask:** "who are you", "why are you here", "what can you do". Answer them in the text.
- **Repeating habits:** if it keeps a phrase you dislike, forbid that phrase by name with an example.
- **The display name** (UI Modifier) also colors the character.

### Voice

The voice has two sides. Vocal tone is how it sounds: pitch, cadence, accent, sing-song or flat. Communication style is how it deals with people: calm or combative, caring or dismissive, clear or rambling, honest or shifty. Pick the voice model in the Persona Modifier and describe the style in "How you talk". The more exact the description, the more believable the character.

### Moderation

A safety layer sits on top of the model. A personality or a line that trips it gets replaced by a safe one. If a test in the Prompt Editor comes back bland or refused, reword the text. Do not try to get around the layer: that breaks Epic's rules and can cost the account (Developer Rule 1.22). No persona that gives medical or mental-health advice, no romantic companion.

### Test list (Prompt Editor, before any session)

1. "Who are you?" and "Why are you here?": in character, right length.
2. One request it should grant, one it should refuse.
3. Something off-topic: it stays in character.
4. Something rude: it stays within the rules.
5. Bulk Response Mode on the most important line: ten replies, all acceptable.
6. The Structured Output tab with your struct: the fields come back as you expect.

Then playtest by voice. Spoken questions are messier than typed ones.
