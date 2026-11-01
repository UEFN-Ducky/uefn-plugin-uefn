---
description: "How to tell a folder is an Unreal Engine game project or engine source tree (GenerateProjectFiles.*, *.uproject, Engine/ dir, .mcp.json) and which conventions to default to — Epic's SessionStart hook as a rule"
metadata:
  order: 5
  label: "Detecting an Unreal project"
  default_enabled: false
  load_condition: "Working in a folder that may be a UE project or engine source tree, before suggesting C++ or editor work"
---

# Detecting an Unreal project

Epic's plugin ships this as a SessionStart hook (`hooks/unreal-context.sh`); here it is a rule.

Walk up from the working folder; the first directory with any of these is the project root:

- `GenerateProjectFiles.bat` / `.sh` / `.command`
- any `*.uproject`

A bare `Engine` directory is **not** a marker — the source tree has `Engine/Source/Runtime/Engine`, so walking up from a Runtime module would stop at `Source/Runtime` and misidentify the root.

At the root:

- Has an `Engine/` directory → **engine source tree**; otherwise a **game project**, named by its `.uproject`.
- `.mcp.json` present → the MCP client config exists. Absent → run `ModelContextProtocol.GenerateClientConfig ClaudeCode` in the editor console (`setup`).

Then default to UE conventions — C++/`UObject` patterns, Slate, UHT reflection (`UCLASS` / `UPROPERTY` / `UFUNCTION`) — and use `core` for anything that drives the editor.

UEFN islands also have a `.uproject` but are Fortnite projects: Verse, no C++ → the `uefn` and `verse` packs.
