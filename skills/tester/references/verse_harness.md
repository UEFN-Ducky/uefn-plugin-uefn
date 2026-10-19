---
description: "In-game Verse assert harness — ExpectEqual / ExpectTrue / ExpectInRange"
metadata:
  label: Verse harness
  default_enabled: true
  load_condition: "Writing leveling/movement asserts, scaffolding DuckyTests, or parsing [DUCKY-TEST] results"
  order: 20
---

# Verse test harness

## Scaffold

`verse_test_scaffold` writes `Verse/DuckyTests/ducky_test_device.verse` with:

- `ExpectEqual(Name, Actual, Expected)`
- `ExpectTrue(Name, Condition)`
- `ExpectInRange(Name, Actual, Lo, Hi)`

Each call `Print`s `[DUCKY-TEST] PASS|FAIL name: detail`. `OnBegin` runs `RunAllTests()`.

## Authoring cases

Prefer the MCP tool (no hand-editing required):

```
verse_test_add_case(
  name="leveling.level2_xp",
  kind="equal",
  actual="XpForLevel2",
  expected="250",
  setup_line="XpForLevel2 := 250",
)
verse_test_add_case(
  name="movement.walk_speed",
  kind="in_range",
  actual="WalkSpeed",
  lo="100.0",
  hi="2000.0",
  setup_line="WalkSpeed := 600.0",
)
```

Or put real formulas in `RunAllTests()` via `workspace_write_file` on `Verse/DuckyTests/*.verse`.

After edits: `workspace_list_verse_errors` → `verse_test_run` (compile + push) → place the device once if missing → `tester_get_results` / `verse_test_results`. Never ask the user to play a session.

## Results

`tester_get_results` / `verse_test_results` tails the editor log for `[DUCKY-TEST]` and returns `{passed, failed, results[]}`. Failures must be fixed in the same turn when you own the harness file.
