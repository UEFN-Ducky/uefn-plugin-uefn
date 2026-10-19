---
name: uefn-logs
description: Read the real UEFN Output Log (Verse Print / LogVerse lines from play sessions) and the Fortnite client log. Use when a play test "did nothing", to see what Verse printed, or to feed logs into a workflow agent.
---

# UEFN Logs

Verse `Print("...")` from a live session shows up in the UEFN Output Log as
`LogVerse: : <text>`. `get_editor_log` does NOT read that file — use these tools.

Files read (from disk, read-only):
- editor: `%LOCALAPPDATA%/UnrealEditorFortnite/Saved/Logs/UnrealEditorFortnite.log`
- client: `%LOCALAPPDATA%/FortniteGame/Saved/Logs/FortniteGame.log`

## Tools
| Tool | Use |
|------|-----|
| `uefn_logs_sources` | Which files exist and their size |
| `uefn_logs_mark(name)` | Remember the log end before a session |
| `uefn_logs_wait(pattern, fail_pattern, timeout_sec)` | Block until a line appears (stops early on FAIL) |
| `uefn_logs_capture(pattern, mark, max_lines)` | Matching lines since the mark (+ `prompt` for an agent) |
| `uefn_logs_last` | Last capture made by a workflow |

Default pattern: `\[ARRIVAL\]|\[PLAYERCORE\]|LogVerse: .*(Error|error|FAIL)|Script error|VerseRuntime`.
No mark → reads the last ~2 MB of the log.

## Workflow nodes
- `uefn-logs.mark` → put before `uefn.game.start`.
- `uefn-logs.wait` → never aborts; branch on `found` / `failed` / `timed_out`.
- `uefn-logs.capture` → outputs `text`, `lines`, `prompt`, and file `uefn_log_capture.txt`;
  wire into `pipeline.agent` so a ducky diagnoses the run.

Tag your Verse prints (`[ARRIVAL] ...`, `[PLAYERCORE] ...`) so one regex finds the whole flow.
