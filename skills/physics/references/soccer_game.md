---
description: "Build a physics soccer island — ball FortPhysics, goals, volumes, trackers, HUD, Verse game_manager"
metadata:
  order: 50
  label: "Soccer game"
  default_enabled: false
  load_condition: "Making a soccer, football, or pickaxe ball goal game with UEFN physics"
---

# Make a physics soccer game

Players shove/hit a physics ball into opponent goals with the pickaxe.

## 1. Project

1. New island (Blank recommended; optional grassy `M_FortniteLandscape_Customizable` on GridPlanes).
2. Project Settings → Experimental/Beta Access → **Physics** on.
3. Island Settings (example 2v2-ish):

| Setting | Value |
|---------|--------|
| Max Players | 6 |
| Teams | Team Index: 2 |
| Team Size | Split Evenly |
| Join In Progress | Spawn |
| Invincibility | true |
| Allow Building | None |
| Start With Pickaxe | true |

Pair MaxPlayers with one Player Spawn Pad per slot (`islandsettings` skill).

## 2. Soccer ball

1. Import mesh (e.g. `.glb`) → open static mesh → Simple Collision → sphere
   (Radius ~102, Block All, center 0).
2. Scripted Asset Actions → Convert to Prop → Stone → place Blueprint prop.
3. + Add → **Fort Physics**:

| Option | Value |
|--------|--------|
| Simulate Physics | true |
| Override Mass | true |
| Mass | 20 |
| Linear Damping | 0.1 |
| Angular Damping | 0.3 |
| Impulse On Hit Multiplier | 3.0 |

## 3. Field

- Prefab pitch (e.g. Recreation Soccer Field) + two goals (scale ~1.5× if needed).
- Six Player Spawners: 3× Team Index 1, 3× Team Index 2; Visible in Game false.
- **Barrier** enclosure: Zone Shape **Hollow Box**; bottom below ground so spawns work.

## 4. Devices

Two **Volume** devices behind goals (`Team_A_Goal`, `Team_B_Goal`) — enable Physics Events.
Example size: Width 0.6, Depth 2.2, Height 1.0 (tune to goal mouth).

| Device | Notes |
|--------|--------|
| Tracker Score Team A/B | Stat Score; Sharing Team; titles Team A/B Score |
| HUD Message A/B | Center; scoring cue; “Team A/B Goal!!!” |
| Air Vent ×2 near goals | Knockup Force Multiplier ~0.1 to clear ball |

## 5. Verse game_manager

Folder: `Verse/Soccer/` (not Verse root). Editable refs: two volumes, two trackers,
two HUD messages, ball `creative_prop`.

```verse
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/SpatialMath }

game_manager := class(creative_device):
    @editable TeamAGoal:volume_device = volume_device{}
    @editable TeamBGoal:volume_device = volume_device{}
    @editable TrackerScoreTeamA:tracker_device = tracker_device{}
    @editable TrackerScoreTeamB:tracker_device = tracker_device{}
    @editable HUDMessageGoalTeamA:hud_message_device = hud_message_device{}
    @editable HUDMessageGoalTeamB:hud_message_device = hud_message_device{}
    @editable FootballA:creative_prop = creative_prop{}

    OnBegin<override>()<suspends>:void=
        TeamAGoal.PropEnterEvent.Subscribe(OnTeamAGoalEnter)
        TeamBGoal.PropEnterEvent.Subscribe(OnTeamBGoalEnter)

    OnTeamAGoalEnter(Prop:creative_prop):void=
        HUDMessageGoalTeamB.Show()
        TrackerScoreTeamB.SetValue(TrackerScoreTeamB.GetValue() + 1)
        spawn{ResetBall()}

    OnTeamBGoalEnter(Prop:creative_prop):void=
        HUDMessageGoalTeamA.Show()
        TrackerScoreTeamA.SetValue(TrackerScoreTeamA.GetValue() + 1)
        spawn{ResetBall()}

    ResetBall()<suspends>:void=
        HidePos := vector3{X := 880.0, Y := 4000.0, Z := 200.0}
        if (FootballA.TeleportTo[HidePos, IdentityRotation()]) {}
        Sleep(3.0)
        ResetPos := vector3{X := 0.0, Y := 0.0, Z := 400.0}
        if (FootballA.TeleportTo[ResetPos, IdentityRotation()]) {}
        FootballA.SetLinearVelocity(vector3{})
        FootballA.SetAngularVelocity(vector3{})
```

Confirm event names with digests. Tweak Hide/Reset vectors to the field center.
Optionally zero velocity after teleport (`SetLinearVelocity` / `SetAngularVelocity`).

Wire editables → compile → PIE: shove/hit ball, score triggers HUD + tracker + reset.
