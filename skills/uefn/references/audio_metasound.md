---
description: "Audio via Epic MCP (43.00): import wav/ogg/mp3 as SoundWaves (SoundWaveToolset.ImportFile), MetaSound presets for background music, ambience loops and one-shot SFX (MetaSoundAuthoringToolset: FindMetaSoundAssets, CreateSourcePresetBuilder, SetDefaults, BuildToAsset, Attach/Commit/Detach), playing them with the Audio Player device and Verse audio_player_device.Play(), tested results and traps"
metadata:
  order: 5
  label: "Audio: SoundWaves + MetaSound (43.00 MCP)"
  default_enabled: false
  load_condition: "Make or import background music, ambience, a loop, a sound effect / SFX / one-shot, a horn or alarm sound; MetaSound, SoundWave, wav / mp3 / ogg import; Audio Player device sound setup"
---

# Audio: SoundWaves + MetaSound via Epic MCP (43.00)

Tested live in UEFN 43.00 (claudeduckytest, Nov 1 2026). Results per step are marked
**tested** / **fails** below. Toolsets: `EditorToolset.SoundWaveToolset` (1 tool) and
`MetaSoundToolset.MetaSoundAuthoringToolset` (8 tools) — `epic_toolsets`. Call
`unreal__describe_toolset` first; one mutating `unreal__call_tool` per turn.

**Play sounds with the Creative Audio Player device** (`creative_devices`), never Speakers
or prop meshes. MetaSound is only how you make or tune the sound asset.

## 1. Import an audio file — tested

```
unreal__call_tool(toolset_name="EditorToolset.SoundWaveToolset", tool_name="ImportFile", arguments={
  "folderPath": "<content_root>/Audio",          # get_project_info().content_root, never /Game
  "assetName":  "SW_Theme",
  "sourceFile": "C:\\…\\theme.wav"})             # absolute path on disk
# → {"returnValue": [{"refPath": "<content_root>/Audio/SW_Theme.SW_Theme"}]}
```

Accepts wav, aif, aiff, ogg, flac, opus, mp3. The user supplies the file (or the Ducky audio
tools make it); never download one. Tested: a 1 s 22 kHz mono wav imported in one call.

## 2. New MetaSound = a preset over a built-in parent

`FindMetaSoundAssets{pattern, maxResults}` lists the parents you may use. In UEFN 43.00 it
returns only **built-in** MetaSounds, all read-only:

| Parent | Use |
| --- | --- |
| `/Metasound/DefaultAssets/Sources/MSS_PlayRandom_Loop.MSS_PlayRandom_Loop` | music, ambience, any loop |
| `/Metasound/DefaultAssets/Sources/MSS_PlayRandom_Oneshot.MSS_PlayRandom_Oneshot` | one-shot SFX (has `OnFinished`) |
| `/Armory/Items/Weapons/Audio/MSS_Armory_WeaponSound*` | weapon sounds (custom weapons) |

```
CreateSourcePresetBuilder{presetName: "ThemeBuilder", referencedSourcePath: <parent>}   # tested
# returns the document; its "inputs" are the whole overridable set:
#   Sounds (WaveAsset:Array), PitchBase, PitchRandomSpread, VolumeBase, VolumeRandomSpread, UE.Source.OnPlay
SetDefaults{builderName: "ThemeBuilder", defaults: [                                     # tested
  {"node": "", "pin": "Sounds",     "value": "[\"<content_root>/Audio/SW_Theme.SW_Theme\"]", "page": ""},
  {"node": "", "pin": "VolumeBase", "value": "-6", "page": ""}]}
# → {"bOk": true, "applied": 2}
BuildToAsset{builderName: "ThemeBuilder", assetName: "MSS_Theme",
             packagePath: "<content_root>/Audio", author: "UEFN-Ducky"}                   # FAILS in 43.00, see below
```

`CreatePatchPresetBuilder{presetName, referencedPatchPath}` is the same for MetaSoundPatch parents.

### Presets to use

| Sound | Parent | Defaults |
| --- | --- | --- |
| Background music | `MSS_PlayRandom_Loop` | `Sounds` = one track (several = random pick per loop), `VolumeBase` ≈ -6, spreads 0 |
| Ambience bed | `MSS_PlayRandom_Loop` | `Sounds` = 2–4 variations, `VolumeBase` ≈ -12 … -18, small `VolumeRandomSpread` |
| One-shot SFX | `MSS_PlayRandom_Oneshot` | `Sounds` = 2–5 variations, `PitchRandomSpread` small, `VolumeRandomSpread` small so repeats don't sound identical |

`VolumeBase` and the pitch inputs are floats (defaults 0). Values go as bare strings; arrays
as JSON strings.

## 3. Edit an existing MetaSound

```
FindMetaSoundAssets{pattern: "<name>"} → pick one with bIsReadOnly: false
AttachBuilderToAsset{assetPath, builderName: "EditTheme", page: "Default"}
SetDefaults{builderName: "EditTheme", defaults: [...]}
CommitBuilderToAsset{builderName: "EditTheme"}        # saves back to the same asset
DetachBuilderFromAsset{builderName: "EditTheme"}      # always, even after a failure
```

Not tested: the island had no writable MetaSound (all 5 listed are read-only built-ins).

## 4. Play it

- **Audio Player device** (classic Creative device): place it with
  `ValkyrieFortniteToolset.DeviceToolset.PlaceDevice`, then `ListClassicDeviceOptions` →
  `SetClassicDeviceOption` (sound asset, looping, volume, who hears it), one option per call. Not
  `SetDeviceProperty`: in 43.00 that only takes a Verse `creative_device`. Recipe: `creative_devices`.
- **Verse:** `@editable Music:audio_player_device = audio_player_device{}` then
  `Music.Play()` / `Music.Stop()`; `Play(Agent)` / `Stop(Agent)` only with *Heard by Instigator*;
  `Register(Agent)` / `Unregister` / `UnregisterAll` for registered-player hearing;
  `Enable` / `Disable` (Disable also stops playback). Music: play once at round start on a looping
  sound, never re-`Play` in a loop.

## Tested results (43.00)

| Step | Result |
| --- | --- |
| `SoundWaveToolset.ImportFile` (wav) | **works** |
| `FindMetaSoundAssets{pattern: ""}` | **works**: 5 results, all built-in, all `bIsReadOnly: true` |
| `CreateSourcePresetBuilder` (Loop and Oneshot parents) | **works**, returns inputs + topology |
| `SetDefaults` with `node` = input name | **rejected**: "Cannot set a node input default on preset builder … only graph-input defaults can be overridden" |
| `SetDefaults` with `node: ""`, `pin` = input name | **works** (`applied: 2`) |
| `BuildToAsset` (`packagePath` = content root or a subfolder, with or without defaults) | **fails**: "Failed to build asset '<path>'", no reason in the log (`LogScript` repeats it) |
| Attach / Commit / Detach | not testable (no writable MetaSound) |
| `AssetToolset.Delete{path: <folder>}` cleanup | **works** (arg is `path`, not `assetPath`) |

**Until `BuildToAsset` works:** import the SoundWave and set it directly on the Audio Player device
(`SetClassicDeviceOption`), using the device's loop and volume options. That covers music, ambience
and one-shots without a MetaSound. Use a preset only for random variation and pitch spread. Report the
build failure; don't retry it.

## Traps

- **The builder is a shared singleton.** An attached builder is the engine's single builder for that
  asset, so the open MetaSound editor and other agents share its state. Use one unique `builderName`
  per job and always `DetachBuilderFromAsset` (uncommitted edits are lost).
- **The page is stated, not inherited.** Pass `page: "Default"` to `AttachBuilderToAsset` unless the
  asset is paged; an unknown page fails without attaching. On mutators an optional page is only
  checked: a wrong page fails the call rather than editing another graph.
- **Presets are topology-read-only.** Only graph-input defaults change (`node: ""`). A node pin in
  `SetDefaults` aborts the **whole** call, not one item.
- **The restricted editor refuses some parents.** UEFN lists and accepts only parents whose chain ends
  at a built-in MetaSound. A project's own MetaSound can't parent a preset, and the preset creators /
  Attach refuse what `FindMetaSoundAssets` does not list.
- `BuildToAsset` on an *attached* builder forks a new asset instead of saving; use `CommitBuilderToAsset`.
- Array defaults on node pins don't render in the MetaSound editor (they still apply).
- Content root only: `<content_root>/…` from `get_project_info()`; `/Game/…` breaks cook.
