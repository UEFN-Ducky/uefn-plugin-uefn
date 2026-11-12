---
description: "LLM NPCs / conversations (persona_component): moved to the `conversations` skill. This page only says where each part now lives"
metadata:
  order: 15
  label: "Conversations / LLM NPCs (moved)"
  default_enabled: false
  load_condition: "NPCs that talk (LLM, AI-powered, persona, conversation, voiced character, quest giver that listens, haggling, narrator), the Persona Modifier, structured output, @ai_description"
---

## Conversations: LLM-powered NPCs

Talking NPCs have their own skill now: **`conversations`**. Load it instead of this page.

| Want | Load |
|---|---|
| The whole picture: where each thing is done, the build order, what to check when it does not work | `skill_read_subskill("conversations", "core")` |
| The character definition, Persona Modifier, voice, Prompt Editor | `skill_read_subskill("conversations", "setup")` |
| Writing the personality | `skill_read_subskill("conversations", "persona_prompts")` |
| Letting players talk to it (group, voice channel, conversation target) | `skill_read_subskill("conversations", "players_and_channels")` |
| Its words changing the game (`RegisterAction`, `Session.Prompt`) | `skill_read_subskill("conversations", "structured_output")` |
| Speaking on game events, facing the speaker, captions | `skill_read_subskill("conversations", "behaviors")` |
| Every name from the digest | `skill_read_subskill("conversations", "verse_api")` |

Ready-made Verse: `verse_template_apply("llm_npc_shopkeeper")` and `verse_template_apply("llm_npc")`.

`AppendToPersonality`, `RegisterPromptBinding` and `ResponseType` do not exist (error 3506): use `SetPersonality` and `RegisterAction`.
