---
description: "Create, edit or review an Unreal Agent Skill registered with unreal-mcp (AgentSkillToolset ListSkills/GetSkills/CreateSkill/UpdateSkill): principles, Python @agent_skill class vs UAsset skill, registration, reload, review. Not Ducky skill packs or .claude/skills"
metadata:
  order: 4
  label: "Authoring Unreal Agent Skills"
  default_enabled: false
  load_condition: "Creating, updating or reviewing an Unreal Agent Skill, a Python skill class, a skill UAsset, or CreateSkill / ListSkills / GetSkills"
---

# Authoring Unreal Agent Skills

Adapted from Epic `skills/unreal-skill` (MIT). An Agent Skill is a named bundle of instructions registered with the unreal-mcp server — distinct from Ducky skill packs and `.claude/skills/`. Using an existing one: `core` → Project skills. Authoring a toolset instead: `create_toolset`.

## Principles

- **Novel** — only what the agent does not know or cannot learn by calling a tool.
- **Collegial** — brief a knowledgeable colleague; assume Unreal knowledge. Give what is needed to act.
- **Flexible** — concepts, steps, or both, whichever is clearest.
- **Durable** — do not embed property, tool or API names that change over time; they break silently.
- **Agnostic** — no orchestration systems, role names, model names, or how the agent is wired up.
- **Parsimonious** — every token costs context; cut anything that would not be missed.

## Before you write

1. **Exists already?** `AgentSkillToolset.ListSkills`, then `GetSkills` on anything relevant. Covered → point the user to it.
2. **Pick the path:**
   - **Python class** — the skill belongs to a code plugin: lives with its Python toolsets, version-controlled, registers when the plugin loads.
   - **UAsset** — project-specific and not in a plugin: create it via `CreateSkill`, no code.

## Structure

- **Description** — loaded at discovery, before the body. One or two sentences: what it covers, when it applies.
- **Instructions** — the payload the agent follows when the skill is active. Assume the agent discovers tools at runtime (`list_toolsets` / `describe_toolset` / `call_tool`); never hardcode a toolset list.

## Python skills

A `UAgentSkill` subclass in a plugin Python file. Class docstring = Description; `instructions` class attribute = Instructions.

```python
import unreal

from toolset_registry.agent_skill import agent_skill

_INSTRUCTIONS = (
    'Do X before Y, because Z.\n'
    'Always verify the result after performing the operation.\n'
)

@agent_skill
class MySkill(unreal.AgentSkill):
    """Provides guidance on doing X in Unreal Engine.
    Apply this skill whenever the user wants to accomplish X."""

    instructions = _INSTRUCTIONS
```

**Registration:** skills register on import. Unless told otherwise, put skill files in a `skills/` subfolder of the plugin's Python package, import each explicitly in that subfolder's `__init__.py`, and make `init_unreal.py` import the `skills` package.

**Reload** after edits (the editor will not see changes otherwise): enable Edit → Project Settings → Plugins → Python → Enable Remote Execution, then

```bash
python Engine/Plugins/Experimental/ToolsetRegistry/Content/Python/toolset_registry/tests/reload_remote.py your_plugin
```

## UAsset skills

A `UAgentSkill` instance saved as a Content Browser asset, via `AgentSkillToolset` (always `ListSkills` first):

- **Create:** `CreateSkill` — `FolderPath` (Content Browser folder, e.g. `/Game/Skills/`), `AssetName` (PascalCase, e.g. `MyWorkflowSkill`), `Description`, `Details` (an `FAgentSkillDetails` with `Instructions`).
- **Update:** `UpdateSkill` — `SkillPath` (e.g. `/Game/Skills/MyWorkflowSkill.MyWorkflowSkill_C`), `Description`, `Details`.

UEFN: only if `AgentSkillToolset` shows in `list_toolsets` (it is not in the 42.40 catalog), and the folder goes under the island's `content_root`, never an invented `/Game/...`.

## Review

`GetSkills` on its path, then read Description and Instructions together as the agent will:

- **Description:** would an agent reading only this know whether to activate it for a given task?
- **Instructions:** do they teach something the tools cannot, briefly enough to be worth the context?
