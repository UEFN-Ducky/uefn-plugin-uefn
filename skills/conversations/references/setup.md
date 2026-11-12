---
description: "Editor setup for a talking NPC: NPC Character Definition (Custom type), Persona Modifier (Character Facts, voice, face animation, interruption rule), UI Modifier name, Fortnite character cosmetics, the Prompt Editor (Conversation and Bulk Response modes, Structured Output tab, export to Verse), Verse Behavior, NPC Spawner, and what the player's account needs"
metadata:
  order: 1
  label: "Conversations: editor setup"
  default_enabled: false
  load_condition: "Creating a talking NPC's character definition, adding or filling the Persona Modifier, picking a voice, naming the NPC, using the Prompt Editor, placing the NPC, or a player who cannot talk to it because of account or voice settings"
---

## Editor setup: the persona lives on the character definition

Everything on this page is done in the editor, on one asset: the **NPC Character Definition**. Verse comes after (`players_and_channels`).

### What Ducky's tools do and what the person does

| Step | Who |
|---|---|
| Create the definition for a custom mesh | `create_npc_character_definition` (animation `npc_characters`) |
| Create the definition for a Fortnite character look | The person: Content Drawer → right-click → Artificial Intelligence → NPC Character Definition |
| Add the **Persona Modifier** and the **UI Modifier**, fill them | The person, in the definition's Details. No Ducky tool adds these two modifiers. Give them the clicks below |
| Read back what is on the definition | `get_npc_definition_info` (lists the modifiers) |
| Set the Verse behavior class | `set_npc_definition_behavior`, after a clean compile |
| Point a placed spawner at the definition | `set_npc_spawner_definition` |

Ask for the modifier clicks once, in one message, then confirm with `get_npc_definition_info` and carry on.

### The definition, field by field

1. **Character type:** Custom. The Persona Modifier is only offered for the Custom NPC character type.
2. **NPC Character Modifiers → + → Persona Modifier** (the label may say experimental). This is what adds the `persona_component` to the spawned NPC. Inside it:
   - **Character Facts → Personality:** who it is and how it talks.
   - **Character Facts → Knowledge:** what it knows when the session starts.
   - **Voice:** pick one and press Play to hear it.
   - **Face animation:** on if the face should move while it speaks.
   - **Interruption rule:** what happens when someone talks while it is busy (ignore until finished, stop at once, or stop when the new reply is ready).
   - **Edit in Prompt Editor:** opens the test window.
3. **NPC Character Modifiers → + → UI Modifier → Display Name:** the name players see. The model also takes some of its character from this name, so pick it with the personality in mind.
4. **Cosmetic modifier:** the look. For a Fortnite character, add the Persona Modifier **first** and the character **second**: the character's own personality text is then filled in for you. If that text is deleted it cannot be brought back without making the asset again.
5. **NPC Character Behavior → Verse Behavior:** your `npc_behavior` class. Required: without Verse no player gets a conversation target.

One persona per definition. For a random look each spawn: Cosmetic Modifier → CharacterLook → Random Fortnite Character.

### Fortnite characters

Fortnite outfits come with a matching voice and a ready personality. Most can be edited or extended. A set of Fortnite IP characters is locked: their personality cannot be changed (Agent Jonesy, Peely, Fishstick, Midas, Raven, Mancake, Kor, Ziggy, Tomatohead, Brite Bomber, Cuddle Team Leader, Mecha Team Leader, Red Ruin Joni, Haylee Skye, The Imagined, Triggerfish, Heroic Hope when this page was written). In Verse the same rule shows as voice classes marked `<epic_internal>`: they cannot be constructed in your code (`verse_api`).

### Prompt Editor: test before any session

Open it from the Persona Modifier (Character Facts → Edit in Prompt Editor).

| Part | Use |
|---|---|
| Name, Personality Prompt | The same text as on the definition. Edits in either place show in both |
| Conversation Mode | Type what a player would say into "Prompt the persona" and read the reply |
| Bulk Response Mode | Get several replies to the same line at once, to see how much it varies. The count is the field next to the mode |
| Response Details | Click a reply: which prompt caused it and which earlier lines shaped it |
| Structured Output tab | Add a struct and its fields without code, to see what the model fills in |
| Export | Writes a Verse file with a module named after the definition: the personality as a message and the structs. Compile, then use the structs from your behavior through that module |

Loop: type the questions players will really ask ("who are you?", "why are you here?", "give me a gun"), read, fix the personality, repeat. Do this before writing Verse.

### Prompts in one place

The Personality and Knowledge text can also be set on the placed **NPC Spawner** (Details → Character Facts), where it can override what the definition says. Keep the text in one place per NPC, the definition, so nobody edits a copy that is not the one in use.

### Place it

Drag the definition from the Content Drawer into the level. That places an NPC Spawner already pointing at it.

### What a player needs

- Voice chat on in Fortnite.
- For a child's account: the parental control that allows voice and written communication with AI features. A cabined account needs a parent to finish account setup first.
- They hold the key shown on screen while they speak.

Players can report a reply: sidebar → Report → Submit a Report → Conversational AI.

Next: `persona_prompts` (what to write), then `players_and_channels` (the Verse that lets players talk).
