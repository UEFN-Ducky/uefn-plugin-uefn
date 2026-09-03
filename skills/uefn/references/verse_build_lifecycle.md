---
description: "Verse build wait, digest vs VM relink, VERSE_DEAD, and the 9002/9000 digest-deadlock recovery"
metadata:
  order: 9
  label: "Verse build lifecycle"
  default_enabled: false
  load_condition: "WinError 10054 on compile, Script error 9002/9000, Script linking is incomplete, VERSE_DEAD component, or a new mesh/prefab class is missing from the digest"
---

# Verse build lifecycle

UEFN compiles and relinks Verse **asynchronously**. The MCP socket going away
during a build is expected. Patching a digest is forbidden and does not help.

## `WinError 10054` means the build started

```
Error executing tool workspace_compile_verse:
[WinError 10054] An existing connection was forcibly closed by the remote host
```

UEFN tears down the bridge socket **because it is now compiling and relinking**.
This is not a dropped connection and not a failure.

1. **Do not retry** `workspace_compile_verse`. Retrying restarts the cycle.
2. Wait minutes (a large project takes minutes, not 30 seconds).
3. Poll a **read-only** signal: `list_verse_types` / `search_verse_digest` /
   `workspace_list_verse_errors`. Never send another mutator while waiting.
4. The build is done when the new class names appear (or Problems is clean).

The same wait applies to a user clicking **Build Verse Code** in UEFN.

## Digest regenerated ≠ Verse VM relinked

`Assets.digest.verse` updating (or `list_verse_types` listing a new class) does
**not** mean the live Verse VM has linked that class.

Epic `ValkyrieToolset.EntityToolset` add-component (via `unreal__call_tool`) can still fail with:

```
create_asset_component_from_asset_path failed for '…'. The asset must live in
the PROJECT's own content (it needs a digest-generated Verse class) — Fortnite
/Game content will not work.
```

even after the digest is correct. That needs **another Verse build** (and the
10054 wait), not a retry of the EntityToolset add-component call and not a digest edit.

## `VERSE_DEAD_*` components

The EntityToolset add-component call can return a broken component:

- `class`: `VERSE_DEAD_Prefabs-Chunks-…`
- `class_path`: `/Engine/Transient.VERSE_DEAD_…`

That is a stale class after a VM relink. Check `class_path` on every result.

Recover: `reload_listener` → wait for it → destroy the temp entity (EntityToolset) → recreate
the entity → add the component again (EntityToolset). Do not keep attaching to the dead
component.

## Digest deadlock (9002 → 9000 cascade)

A Verse file that `using` / constructs a class that does not exist yet fails
the build. The build is the only thing that regenerates the digest that would
define that class. First failure:

```
Script error 9002: Unable to import resolve '/Project/…/EP_Thing.EP_Thing_C'.
```

Then every later error becomes:

```
Script error 9000: SolarisRuntime is provided with a set of new link tasks,
but a previous link task did not complete successfully: Unable to import resolve '…'
```

Unrelated assets look broken. **Do not patch the digest.** Break the cycle from
the Verse side, in this order:

1. **Comment out** the problem Verse: the `using { … }` imports and every
   reference to the unresolvable classes. The file must compile with those
   references absent.
2. **Rebuild Verse and wait** (10054 = started). The build now succeeds, so
   UEFN regenerates the digest at the new asset paths.
3. **Confirm the digest is fresh** with `list_verse_types` /
   `search_verse_digest` for one of the new class names. Do not skip this —
   it is what proves step 2 worked.
4. **Uncomment** the imports and references, then rebuild again. Only now do
   they resolve, because the classes exist in the regenerated digest.

After step 4, a fresh digest still does not mean the VM relinked. If
the EntityToolset add-component call rejects a class that `list_verse_types` already shows,
build once more — do not retry the attach in a loop.

## Prefabs and linking

`create_prefab_from_entities` saves the asset immediately. Its Verse class
appears in `Assets.digest.verse` only after the next Verse build, and is
usable by EntityToolset add-component / `using` only after the VM relinks (another
build if the first one only refreshed the digest).

Prefab packaging is five serial calls, **one per assistant message**:
Epic `ValkyrieToolset.EntityToolset` via `unreal__call_tool` (tool names from
`unreal__describe_toolset`): create root entity → create child entity → add component →
`create_prefab_from_entities` → destroy the temp instance (EntityToolset). The removed
Ducky entity tools no longer exist.
`save_directory` every 5–10 prefabs. Never `execute_python` loops that
package many prefabs in one script — that freezes UEFN.

## Related

- Serial editor ops: `skill_read_subskill("uefn", "batch_commands")`
- Digest search (read-only): `skill_read_subskill("verse", "digests")`
