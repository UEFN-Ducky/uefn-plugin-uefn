---
description: "Quests — the 43.00 Progression API (publishable): make a quest in the Fortnite quest UI (BR-style toast, Quests tab, tracking), quest / basic_quest / objective / progress_objective, quest_collection / fort_quest_collection, participants and quest_participant_info (Contribute / Observe / Receive), per-player vs group progress, quest_reward + GrantEvent, categories, chaining quests, a compiled coin quest, the traps, and how quests sit next to the XP / economy packs"
metadata:
  order: 25
  label: "Game systems — quests (Progression API, 43.00)"
  default_enabled: false
  load_condition: "Making a quest, quest line, objective, mission, achievement or challenge; showing quests in the Fortnite quest UI / Quests tab / quest toast; quest rewards; anything with quest, objective, quest_collection, basic_quest, progress_objective, fort_quest_collection"
---

## Quests — the Progression API (43.00)

43.00 takes the Progression API out of Experimental, so islands that use it **publish**.
Quests show in the real Fortnite quest UI: a toast top-left when progress changes or a
quest completes, and the island's own section in the **Quests** tab (category icon, name,
description, sub-categories, each quest with progress and rewards, trackable on the HUD).
Every name below is from the 43.00 digests; the coin quest compiled with 0 errors in UEFN
43.00 (Nov 1 2026). 42.x quest code does not compile on 43.00 (renames: `compile_errors`).

### The pieces

| Piece | Module | What it is |
|-------|--------|-----------|
| `objective` | `/Verse.org/Progression` | Trackable work: `State` (`Inactive` / `Active` / `Complete`), `Activate()`, `Deactivate()`, `Complete(Reason)`, `GetProgress():message`, events `ActivateEvent`, `ProgressEvent`, `CompleteEvent`, `DeactivateEvent` |
| `progress_objective` | `/UnrealEngine.com/Progression` | Counter objective: `Progress` / `RequiredProgress` (set at construction), `SetProgress(F)` (clamped to `0…Required`), `SetRequiredProgress(F)`; completes at `Progress >= RequiredProgress`; `GetProgress()` = "X / Y" |
| `quest` | `/Verse.org/Progression` | An `objective` with participants: `Join(Participant, Info)`, `Abandon(Participant)`, `CanJoin` / `CanAbandon` vetoes, `JoinEvent` / `AbandonEvent`; belongs to one `Collection` (set in the archetype) |
| `basic_quest` | `/UnrealEngine.com/Progression` | "Do X, get Y": holds an `Objective` (`has_objective`) and `Rewards` (`has_quest_rewards`); **completes itself** when the objective completes and **grants its rewards** on a `succeed_objective_reason`; enrolls `agent_quest_participant` joiners as objective contributors |
| `quest_collection` / `fort_quest_collection` | `/Verse.org/Progression` / `/Fortnite.com/Progression` | Source of truth: `Quests:[quest][]quest_membership`, `Participants:[quest_participant][]quest_membership`, `JoinEvent`, `AbandonEvent`, `CompleteEvent:listenable(quest_complete_event_data{Quest, Reason})`. **Only quests in a `fort_quest_collection` show in the Fortnite UI**, and only if they implement `has_description` |
| `agent_quest_participant{Agent := A}` | `/Verse.org/Progression` | A player **or NPC** as a participant. Subclass `quest_participant` for a team identity |
| `quest_participant_info{}` | `/Verse.org/Progression` | Per-membership flags, all `true` by default: `Contribute` (can progress it), `Observe` (sees it in the UI), `Receive` (gets rewards). Archetype `quest_participant_info{Contribute := false, Receive := false}` compiles; change later with `SetContribute` / `SetObserve` / `SetReceive` |
| `quest_membership` | `/Verse.org/Progression` | `Quest`, `Participant`, `Info` — what collection maps and reward grants hand you |
| `quest_reward` | `/UnrealEngine.com/Progression` | Subclass it; override `OnGrant(Memberships)<transacts>`; `GrantEvent:listenable(quest_reward_grant_event_data{Reward, Recipients})`. Built-in `entitlement_quest_reward{Entitlement, Quantity}` |
| `complete_objective_reason` | `/Verse.org/Progression` | `succeed_objective_reason{}` (grants rewards) / `fail_objective_reason{}` (grants nothing); subclass either to carry data (a medal tier) |
| `fort_quest_category` | `/Fortnite.com/Progression` | A Quests-tab section: `SortOrder:rational` (lower first), `Parent:?quest_category` for sub-categories, plus icon/name/description |
| `has_quest_presentation` | `/UnrealEngine.com/Progression` | Optional on a quest: `ShowNotification` (toast), `AllowFavorite` (trackable), `Categories`; extends `has_icon` + `has_description` |

Results: `Join` returns `result(quest_membership, []quest_error)`, `Activate` / `Complete`
return `result(void, []objective_error)`. Statement position may ignore them; to check,
`if (not Quest.Activate().GetSuccess[]): …`.

### Editor setup

Nothing to place for the quest itself — no quest device. Put the code on a Verse device
(below) or a Scene Graph component, and wire whatever feeds progress (triggers, item
pickups, guard spawners, `scene_event`s from child entities). Imported **textures** are
only needed for icons (`has_icon.Icon:texture` has no default — see Traps).

### Example — a BR-style coin quest in the Fortnite quest UI (compiled, 43.00)

One quest **per player** (each has their own counter), listed in the Quests tab, toast
on each pickup and on completion. Each coin is a `trigger_device` (set its "Times Can
Trigger" / per-agent options so a coin counts once per player).

```verse
using { /Verse.org/Simulation }
using { /Verse.org/Presentation }       # has_description (without it: 3506)
using { /Verse.org/Progression }        # quest, objective, participants
using { /UnrealEngine.com/Progression } # basic_quest, progress_objective, quest_reward
using { /Fortnite.com/Progression }     # fort_quest_collection (the Fortnite UI)
using { /Fortnite.com/Devices }

CoinQuestName<localizes>:message = "Coin Hunt"
CoinQuestDesc<localizes>:message = "Pick up 5 coins anywhere on the island."
CoinQuestShort<localizes>:message = "Pick up 5 coins"

# has_description is all the Fortnite quest UI needs to list a quest.
coin_quest := class(basic_quest, has_description):
    QuestID:int = 1                       # quests don't persist: save this id + progress yourself
    var Name<override>:message = CoinQuestName
    var Description<override>:message = CoinQuestDesc
    var ShortDescription<override>:message = CoinQuestShort

coin_quest_device := class(creative_device):
    @editable CoinTriggers:[]trigger_device = array{}
    @editable CoinsRequired:float = 5.0

    Collection:fort_quest_collection = fort_quest_collection{}
    var Objectives:[agent]progress_objective = map{}

    OnBegin<override>()<suspends>:void =
        for (T : CoinTriggers):
            T.TriggeredEvent.Subscribe(OnCoin)
        Collection.CompleteEvent.Subscribe(OnQuestDone)
        GetPlayspace().PlayerAddedEvent().Subscribe(GiveQuest)
        for (Player : GetPlayspace().GetPlayers()):
            GiveQuest(Player)

    # One quest per player = per-player progress.
    GiveQuest(Player:player):void =
        if (not Objectives[Player]):
            Obj := progress_objective{RequiredProgress := CoinsRequired}
            Quest := coin_quest{Collection := Collection, Objective := Obj}
            if (set Objectives[Player] = Obj) {}
            Quest.Join(agent_quest_participant{Agent := Player}, quest_participant_info{})
            Quest.Activate()

    OnCoin(MaybeAgent:?agent):void =
        if (Agent := MaybeAgent?, Obj := Objectives[Agent]):
            Obj.SetProgress(Obj.Progress + 1.0)    # clamps at RequiredProgress; basic_quest completes itself

    OnQuestDone(Data:quest_complete_event_data):void =
        if (coin_quest[Data.Quest], succeed_objective_reason[Data.Reason], Memberships := Collection.Quests[Data.Quest]):
            for (M : Memberships, M.Info.Receive?, P := agent_quest_participant[M.Participant]):
                PayCoinQuest(P.Agent)

    # Hook for the economy / progression packs (GetCurrencyProvider / GetXPAwarder).
    PayCoinQuest(Agent:agent):void =
        Print("Coin Hunt complete")
```

Order that works: build the objective → build the quest with `Collection` and `Objective`
in the archetype → `Join` → `Activate`. `basic_quest` activates the objective for you.

### Icons, categories, toast and tracking

With an imported texture (`Textures.T_Coin`), add `has_quest_presentation` and a category.
This shape compiled on 43.00 with the texture passed at construction:

```verse
QuestsCategoryName<localizes>:message = "Island Quests"

island_quest_category := class(fort_quest_category):
    SortOrder<override>:rational = 0
    var Name<override>:message = QuestsCategoryName
    var Description<override>:message = QuestsCategoryName
    var ShortDescription<override>:message = QuestsCategoryName

shown_coin_quest := class(basic_quest, has_quest_presentation):
    var Name<override>:message = CoinQuestName
    var Description<override>:message = CoinQuestDesc
    var ShortDescription<override>:message = CoinQuestShort
    var ShowNotification<override>:logic = true    # toast
    var AllowFavorite<override>:logic = true       # trackable on the HUD

# Root category, then a sub-category ("Part 1") under it:
#   Root := island_quest_category{Icon := Textures.T_Island}
#   Part1 := island_quest_category{Icon := Textures.T_Coin, Parent := option{Root}}
#   Quest := shown_coin_quest{Icon := Textures.T_Coin, Collection := Collection,
#                             Objective := Obj, Categories := array{Part1}}
```

Without `has_quest_presentation`: notifications on, favorites allowed, no category.

### Per-player vs group progress

| Want | Do |
|------|----|
| Each player progresses alone (BR dailies, achievements) | One quest + objective **per player** (example above) |
| Whole squad / server shares one counter | **One** quest; every player `Join`s it; feed one objective |
| Teammates (even NPC guards) help, only the player is rewarded | Helpers join with `quest_participant_info{Observe := false, Receive := false}` |
| See another team's quest progress, no reward | Join with `quest_participant_info{Contribute := false, Receive := false}` |
| Count only contributors' actions | Objective `class(progress_objective, has_objective_contributors)`; check `Contributors.Find[Agent]` before `SetProgress` (`basic_quest.OnJoin` enrolls joiners whose `Info.Contribute` is true) |

### Rewards

- `basic_quest` grants `Rewards` (set with `Quest.SetRewards(array{…})`) to memberships
  whose `Info.Receive` is true, once, on a succeeding completion.
- **`OnGrant` is `<transacts>`.** Item grants (`Inventory.AddItemDistribute(Item{})`) fit
  there. Anything `no_rollback` or `<suspends>` (accolades `Award`, UI, `Sleep`, our
  economy pack's calls) does **not**: keep `OnGrant` empty and run a spawned loop on
  `GrantEvent`:

```verse
gold_quest_reward := class(quest_reward):
    Amount:int = 100
    OnGrant<override>(Memberships:[]quest_membership)<transacts>:void = {}

    Paying()<suspends>:void =                      # spawn{ Reward.Paying() } once
        loop:
            Result := GrantEvent.Await()
            for (M : Result.Recipients, P := agent_quest_participant[M.Participant]):
                PayGold(P.Agent, Amount)            # GetCurrencyProvider() from player_manager
```

  `quest_reward` needs `Icon`, `Name`, `Description`, `ShortDescription` at construction
  (`gold_quest_reward{Icon := Textures.T_Gold, Name := …}`), so a reward always needs a
  texture. No texture? Pay from `Collection.CompleteEvent` instead (the example's
  `PayCoinQuest`) — the quest still shows, just without a reward line.
- Raw `quest` (not `basic_quest`): add `has_objective, has_quest_rewards` yourself,
  override `OnJoin` → `(super:)OnJoin(…)` then `AddContributor`, and `OnComplete` →
  `(super:)OnComplete(Reason)` then `GrantRewards(Memberships)`. Its archetype must pass
  `Categories := array{}` (3600 otherwise).
- Medals / tiers: `medal_reason := class(succeed_objective_reason){Medal:medal}`; swap
  `SetRewards(…)` to the earned tier, then `Quest.Complete(medal_reason{Medal := …})`.
  `fail_objective_reason{}` completes with no rewards. A commanded `Complete()` works at
  any progress.

### Quest lines (chain the next quest)

Listen on `Collection.CompleteEvent` (it fires for **every** quest in the collection), cast
`Data.Quest` to the **previous stage's class**, check `succeed_objective_reason[Data.Reason]`,
then give the next quest to `Collection.Quests[Data.Quest]` memberships whose
`Info.Receive?` (skip NPC helpers with `player[M.Participant…Agent]`). Before giving a quest
on spawn, check `Collection.Participants` so a respawn doesn't hand out a duplicate.

### Next to our XP / economy packs

Quests are **goals and UI**, not storage. Keep the island's XP, levels and currency in
`progression` / `economy` (`sys_progression`, `sys_economy`): a quest's completion calls
`PlayerManager.GetXPAwarder()` / `GetCurrencyProvider()` (from a `GrantEvent` loop or the
collection's `CompleteEvent`). Never build an XP table inside quest rewards. **Quests are
not persistable**: on leave, quest state is gone. To resume, store a `QuestID` + progress
float in the player's persistable table (`persistence`) and rebuild the quest with
`SetProgress` on rejoin.

### Traps (from the 43.00 build and Epic-style tutorials)

- `has_description` / `has_icon` need `using { /Verse.org/Presentation }` / `/Verse.org/Assets`.
- `has_icon.Icon` is `var Icon:texture` with **no default**: every category, presented quest
  and reward needs a real imported texture at construction.
- The Verse LSP flags every `listenable.Await()` (`GrantEvent`, `DeactivateEvent`,
  `TriggeredEvent` …) as "Unknown member `Await`"; the UEFN build accepts it. Trust
  `workspace_compile_verse` (`compile_errors`).
- `Entity.AwaitRoundStart()` (seen in tutorials) is not a 43.00 API — a project helper.
- `Entity.FindDescendantComponents(t)` is a generator: iterate it, or `first(X : Gen) { X }`.
- Persist progress yourself; re-give quests on rejoin, not on every respawn.
- Old 42.x names (`JoinQuest`, `progress_quest_objective`, `SetRequiredCount`, `GrantReward`)
  are gone (`compile_errors` 3506 table).
