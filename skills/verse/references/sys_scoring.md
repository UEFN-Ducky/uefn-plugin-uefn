---
description: "Score keeping & leaderboards — persistent vs per-session scores, the reference-class trick for cheap updates, sorting without rebuilding arrays, per-player leaderboard canvases, rank rewards, and king of the hill"
metadata:
  order: 22
  label: "Game systems — scoring & leaderboards"
  default_enabled: false
  load_condition: "Building score keeping, kill/death tracking, streaks, leaderboards, ranks, rank-based rewards, or a king-of-the-hill / zone-control score"
---

## Score keeping & leaderboards

Two layers, chosen by lifetime. Names below are generic — adapt them to your game.

### Persistent stats vs per-session scores

| | Persistent (survives sessions) | Per-session (this match only) |
|--|-------------------------------|-------------------------------|
| Type | `class<final><persistable>` in `PlayerStatsMap` | plain `class()` in `[agent]score` map |
| Update | rebuild table + `set` into weak_map (immutable) | mutate the retrieved instance in place |
| Holds | lifetime totals (`Kills`, `HighestStreak`, `Points`, `RoundsPlayed`) | this-match counters (`Kills`, `Deaths`, `Points`) |

**Persistent** — rebuild-and-store through a persistence manager (see
`persistence`); one method per stat, all guarded by the `if:` player lookup:

```verse
player_stats := class<final><persistable>:
    Kills <public> : int = 0
    HighestStreak <public> : int = 0
    Points <public> : int = 0

# copy the table, swapping only the stats block
UpdatePlayerStats(OldTable : game_player_table, NewStats : player_stats)<transacts> : game_player_table =
    game_player_table{ Version := OldTable.Version, Stats := NewStats }   # …carry every other field the same way (Verse has no /* */ comments)

stats_save_service := class():
    AddKill(Agent : ?agent) : void =
        if:
            RealAgent := Agent?
            Player := player[RealAgent]
            OldTable := PlayerStatsMap[Player]
        then:
            NewStats := player_stats{ Kills := OldTable.Stats.Kills + 1, HighestStreak := OldTable.Stats.HighestStreak, Points := OldTable.Stats.Points }
            if (set PlayerStatsMap[Player] = UpdatePlayerStats(OldTable, NewStats)) {}
```

**Per-session** — a `class` is a **reference type**, so mutating a field on the
instance you pulled from the map *sticks* without writing back. This is the cheap
path for fast-changing session scores:

```verse
session_score := class():          # NOT a struct — must be a reference
    var Kills : int = 0
    var Points : int = 0

score_manager := class():
    var Scores : [agent]session_score = map{}
    InitializeScore<public>(Agent : agent) : void =
        if (not Scores[Agent]):
            if (set Scores[Agent] = session_score{}) {}
    AddKill<public>(Agent : agent) : void =
        if (Score := Scores[Agent]):
            set Score.Kills += 1            # mutates the stored object directly
    GetAllScores<public>()<transacts> : [agent]session_score = Scores
    RemoveScore<public>(Agent : agent) : void =            # call on player leave
        var NewMap : [agent]session_score = map{}
        for (A -> S : Scores, A <> Agent):
            if (set NewMap[A] = S) {}
        set Scores = NewMap
```

> If you used a `struct` here, `set Score.Kills += 1` would edit a *copy* and the
> map would never change. Reference semantics is the whole trick — use `class`.

Typical flow: `score_manager` subscribes to the player manager's elimination event
(see `sys_player_data`), bumps the session score, and also calls the persistent
`AddKill` so both layers stay in sync.

### Building a leaderboard (snapshot → sort)

Snapshot the score map into a display `struct` with a for-expression, then sort.
Each entry's place is how many entries are ahead of it; no array is rebuilt inside
a loop:

```verse
leaderboard_entry := struct:
    PlayerAgent : agent
    Kills : int
    Points : int

# Number of entries ahead of Entry: more points, or the same points earlier in the list.
PlaceOf(Entries : []leaderboard_entry, Index : int, Entry : leaderboard_entry)<transacts> : int =
    Higher := for (Other : Entries, Other.Points > Entry.Points) do Other
    TiedBefore := for (J -> Other : Entries, J < Index, Other.Points = Entry.Points) do Other
    Higher.Length + TiedBefore.Length

# Highest points first; ties keep their order.
SortByPoints(Entries : []leaderboard_entry)<transacts> : []leaderboard_entry =
    Places := for (I -> Entry : Entries) do PlaceOf(Entries, I, Entry)
    for (Place := 0..Entries.Length - 1, Index := Places.Find[Place], Entry := Entries[Index]) do Entry

# caller
MakeEntry(Agent : agent, Score : session_score)<transacts> : leaderboard_entry =
    leaderboard_entry{PlayerAgent := Agent, Kills := Score.Kills, Points := Score.Points}

Snapshot := for (Agent -> Score : ScoreManager.GetAllScores()) do MakeEntry(Agent, Score)
Sorted := SortByPoints(Snapshot)
```

Fine for a lobby (up to 100 players). Rebuild the board when a score changes, not
on a timer. A sort that takes its rule as a comparator: `functions`.

### Displaying it per player

Keep a `[agent]canvas` of who has the board open; rebuild each player's canvas on
update (build text_blocks per row, hand them to a `*_canvas_builder`). Agent names
can't be stringified — pass them as a `<localizes>` message:

```verse
MessageAgent<localizes>(Agent : agent) : message = "{Agent}"
PlayerNameText.SetText(MessageAgent(Entry.PlayerAgent))   # name
KillText.SetText(Message("{Entry.Kills}"))                # numbers
```

Show/remove with the player's UI: `GetPlayerUI[Player]` →
`PlayerUI.AddWidget(Canvas, player_ui_slot{InputMode := ui_input_mode.None})` /
`RemoveWidget`. See the `ui` reference for canvas construction. Cap rows
(`MaxEntries := 10`) so the board stays readable.

### Rank-based rewards

Once sorted, reward by position — e.g. top-3 get placement effects:

```verse
rank_reward_manager := class():
    var FirstPlaceReward : visual_effect_powerup_device = visual_effect_powerup_device{}
    var SecondPlaceReward : visual_effect_powerup_device = visual_effect_powerup_device{}
    var ThirdPlaceReward : visual_effect_powerup_device = visual_effect_powerup_device{}

    AssignRankRewards(SortedAgents : []agent) : void =
        if (First := SortedAgents[0]):
            FirstPlaceReward.Pickup(First)
        if (Second := SortedAgents[1]):
            SecondPlaceReward.Pickup(Second)
        if (Third := SortedAgents[2]):
            ThirdPlaceReward.Pickup(Third)
```

Track current assignments in `[agent]int` so you can clear last round's rewards
before applying this round's.

### King of the hill

One point per second to the only player on the hill; two or more is contested and
nobody scores. `mutator_zone_device.GetAgentsInVolume()` reads who is inside, so
the scoring tick needs no enter/exit bookkeeping:

```verse
using { /Fortnite.com/Devices }
using { /Verse.org/Simulation }

king_of_the_hill_device := class(creative_device):
    @editable Hill : mutator_zone_device = mutator_zone_device{}
    @editable EndGame : end_game_device = end_game_device{}
    @editable PointsPerSecond : int = 1
    @editable PointsToWin : int = 60

    var HillPoints : [agent]int = map{}

    OnBegin<override>()<suspends> : void =
        loop:
            Sleep(1.0)
            Occupants := Hill.GetAgentsInVolume()
            if (Occupants.Length = 1, King := Occupants[0]):
                AwardHill(King)

    AwardHill(King : agent) : void =
        NewTotal := (HillPoints[King] or 0) + PointsPerSecond
        if (set HillPoints[King] = NewTotal) {}
        if (NewTotal >= PointsToWin):
            EndGame.Activate(King)
```

- Team hill: contested when the occupants belong to more than one team
  (`GetPlayspace().GetTeamCollection().GetTeam[Agent]`, `sys_teams`); award the
  team.
- Feed the points into the session `score_manager` above, and update the HUD from
  `AwardHill`, not from a separate loop.
- Remove a leaving player's entry (`SubscribePlayerRemoved`).
