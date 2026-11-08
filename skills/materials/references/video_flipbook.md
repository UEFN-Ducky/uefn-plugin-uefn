---
description: "Video file → working in-game video screen: ffmpeg flipbook sheets, M_VideoFlipbook, screen mesh, Verse playback synced to an Audio Player, editor placeholder"
metadata:
  order: 14
  label: "Video → flipbook screen"
  default_enabled: false
  load_condition: "User posts or names a video, or asks for a video player, TV, cinema, billboard or flipbook video screen"
---

## Video → flipbook screen

The user posts a video (or names one, e.g. "MyClip on Desktop"). Make, in one run: flipbook
sheets, a flipbook material, a screen mesh, a Verse device that plays it in sync with an Audio
Player, and an editor placeholder showing frame 1. Do it all yourself; the user only supplies the file.

### Hard limits

| Rule | Why |
|---|---|
| Sheets are **power-of-two, max 2048²** | Non-POT import is refused; 4096 textures are invalid in-game |
| Sheet textures: `TEXTUREGROUP_UI`, **NoMipmaps**, **NeverStream** | World group must stream (blurry, popping frames); UI group keeps 2048 resident |
| **Pad, don't stretch** (`pad=2048:2048`) | Tiles keep exact pixels; material `Rows = 2048 / tileH` (fractional is fine) |
| Pick the frame **in Verse from elapsed time**, never the material `Time` node | One clock for every client and the audio, no drift |
| Audio = **Audio Player device** (`audio_player_device.Play()`) | `sound_component` can't be constructed from Verse |
| Use **Ducky's bundled ffmpeg** | A system (WinGet) ffmpeg/ffprobe may be broken |
| Cut files go to `%LOCALAPPDATA%/UEFN-Ducky/video/<Name>/` | Never inside the island's Content |

### 1. Probe and plan the grid

`ffprobe` the file for fps, duration and size. Pick a tile keeping the aspect so a **4×N grid fits 2048**:
16:9 → tile **512×304**, 4 cols × 6 rows (1824 tall, padded to 2048) = **24 frames per sheet**.
Total frames = fps × duration (477 frames at 30 fps → 20 sheets). Keep 30 fps for smooth playback;
each sheet is ~16 MB resident, so above ~40 sheets drop to 24/15 fps or a smaller tile and say so.

### 2. Cut sheets and audio (terminal)

```bash
ffmpeg -i "<video>" -vf "fps=30,scale=512:304,tile=4x6,pad=2048:2048" -start_number 0 "<out>/T_<Name>_%02d.png"
ffmpeg -i "<video>" -vn -ac 2 -ar 48000 "<out>/A_<Name>.wav"
```

### 3. Import

- `import_asset` each PNG to `<content_root>/VideoScreen/Sheets/` (`replace_existing=true` when re-cutting; Epic TextureToolset ImportFile refuses existing names).
- LODGroup `TEXTUREGROUP_UI`, MipGen `NoMipmaps`, `NeverStream=true`, sRGB on. `validate_uefn_asset` the first and last sheet.
- Import the WAV as sound wave `A_<Name>`.

### 4. Material `M_VideoFlipbook` (Unlit, ~12 nodes)

Parameters: `Sheet` (Texture), `Frame` (Scalar), `Cols` (Scalar, 4), `Rows` (Scalar, 2048 / tileH).

```text
col = fmod(Frame, Cols)          row = floor(Frame / Cols)
UV  = (TexCoord0 + float2(col, row)) / float2(Cols, Rows)
Emissive Color = TextureSample(Sheet, UV).rgb        Shading Model = Unlit
```

Build with `create_material` + `add_material_expression` + `connect_material_nodes`, wire every pin,
`layout_material_expressions`, `validate_uefn_asset`. Verse sees class `M_VideoFlipbook` with
`var Sheet:texture`, `var Frame:float`, `var Cols:float`, `var Rows:float`.

### 5. Screen mesh `SM_VideoScreen`

Write a quad OBJ to `.ducky/video/SM_VideoScreen.obj` with one material group `ScreenMat`.
**OBJ import has no axis conversion: UE = (x, −y, z).** Author it upright, facing −X:

```text
v 0 168 0
v 0 -168 0
v 0 -168 200
v 0 168 200
vt 0 0
vt 1 0
vt 1 1
vt 0 1
vn -1 0 0
g ScreenMat
usemtl ScreenMat
f 1/1/1 2/2/1 3/3/1 4/4/1
```

Match the width:height to the video. Import, confirm the slot is named `ScreenMat`, validate.
Verse exposes it as Scene Graph mesh component `SM_VideoScreen` with `var ScreenMat`.

### 6. Verse device `Content/Verse/VideoPlayer/video_screen_device.verse`

```verse
using { /Fortnite.com/Devices }
using { /Verse.org/Assets }
using { /Verse.org/Simulation }
using { /Verse.org/SceneGraph }
using { /<project mount>/VideoScreen }
using { /<project mount>/VideoScreen/Sheets }

video_screen_device<public> := class(creative_device):
    @editable
    Audio<public>:audio_player_device = audio_player_device{}
    @editable
    Loop<public>:logic = true

    FPS:float = 30.0
    FramesPerSheet:int = 24
    TotalFrames:int = 477

    OnBegin<override>()<suspends>:void =
        Mat := M_VideoFlipbook{}
        set Mat.Cols = 4.0
        set Mat.Rows = 2048.0 / 304.0
        SheetTex:[]texture = array{T_Name_00, T_Name_01}   # every sheet, in order
        if (Sim := GetSimulationEntity[]):
            Screen := entity{}
            Mesh := SM_VideoScreen{Entity := Screen, Collidable := false}
            set Mesh.ScreenMat = Mat
            Screen.AddComponents(array{Mesh})
            Sim.AddEntities(array{Screen})
            Screen.SetGlobalTransform(GetGlobalTransform())   # device position/rotation/scale = screen
            loop:
                PlayOnce(Mat, SheetTex)
                if (not Loop?) { break }

    PlayOnce(Mat:M_VideoFlipbook, SheetTex:[]texture)<suspends>:void =
        Audio.Play()
        Start := GetSimulationElapsedTime()
        var ShownFrame:int = -1
        var ShownSheet:int = -1
        loop:
            Frame := Floor[(GetSimulationElapsedTime() - Start) * FPS] or 0
            if (Frame >= TotalFrames) { break }
            if (Frame <> ShownFrame, SheetIdx := Quotient[Frame, FramesPerSheet], Tex := SheetTex[SheetIdx]):
                if (SheetIdx <> ShownSheet):
                    set Mat.Sheet = Tex
                    set ShownSheet = SheetIdx
                set Mat.Frame = (Frame - SheetIdx * FramesPerSheet) * 1.0
                set ShownFrame = Frame
            Sleep(0.0)
```

Verse traps:
- `using { /Verse.org/Assets }` is required for `texture`.
- Never name a local `Sheets`: it clashes with the `Sheets` asset module.
- Arrays are `array{...}`; an indented `array:` block becomes tuples.
- The offline checker reports false "scoped access / internal module" errors on asset modules. Trust `workspace_compile_verse` (real build SUCCESS).

### 7. Place and wire

1. Audio Player (`Device_CRD_AudioPlayer_C`, AddToSceneFromClass) next to the screen. Set its sound with ObjectToolset SetProperties `{"audio": "<path>/A_<Name>.A_<Name>"}` (the device's Audio option rejects custom waves). Sync Player Audio on, Restart Audio When Activated on, Play On Hit off.
2. Place the Verse device and wire `Audio` (Epic SetDeviceProperty value `{"refPath": ...}`, or `wire_verse_device_ref`). Read back with `get_verse_editables`.
3. **Editor placeholder** so it shows before play: `MI_VideoPreview` (instance of `M_VideoFlipbook`, Sheet = sheet 00, Frame 0, same Cols/Rows) on a static `SM_VideoScreen` actor.
4. Put the Verse device **2 cm in front** of the placeholder with the **same rotation and scale**. The runtime screen spawns from the device transform and covers the placeholder. When the user resizes or moves the placeholder, copy its transform onto the device again (keep the 2 cm offset).
5. `save_all_dirty`, then `take_high_res_screenshot` to show it.

### Done when

`workspace_compile_verse` SUCCESS · `validate_uefn_asset` VALID on the material, mesh and first/last
sheet · `get_verse_editables` shows `Audio` wired · a screenshot shows frame 1 on the placeholder.
Say a live session test was not run unless you ran one.
