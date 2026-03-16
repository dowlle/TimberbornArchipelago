# Timberborn Archipelago Setup Guide

## Required Software

- [Timberborn](https://store.steampowered.com/app/1062090/Timberborn/) (experimental branch)
- [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases) (latest release)
- The Timberborn Archipelago mod (installed via Steam Workshop or mod.io)

## Installing the Mod

1. Subscribe to the **Timberborn Archipelago** mod on Steam Workshop, or download the `.zip` from mod.io.
2. Launch Timberborn. The mod should appear in the built-in Mod Manager — enable it.
3. Restart the game after enabling.

## Connecting to the Server

1. Start or load a game with the Archipelago mod enabled.
2. Click the **AP** button in the bottom bar to open the AP Shop.
3. Use the connection panel (bottom-right) to enter your server details:
   - **Server**: hostname or IP (e.g. `archipelago.gg`)
   - **Port**: your session's port number
   - **Slot Name**: your player name from the YAML
   - **Password**: leave blank if not set
4. Click **Connect**. The AP Shop will populate with your seed's layout.
5. Connection data is saved automatically — the game will auto-reconnect on future loads.

## Playing

- The **AP Shop** has 4 branching paths (A, B, C, D). Each path has sequential locations with escalating science costs.
- Buy locations in order within each path — you can freely switch between paths.
- Higher-tier locations are gated by progression items (Gear Workshop, Scavenger Flag, etc.).
- **Skip** items let you check a location without spending science.
- **Milestones** (population, well-being, survival, wonder) trigger automatically as you play.
- Buildings unlock in your toolbar as you receive blueprint items from the multiworld.

## Important: Faction Selection

If you set `faction: iron_teeth` or `faction: random` in your YAML, make sure Iron Teeth is **unlocked in your game first** (requires reaching average well-being 8 in a Folktails game). The mod will block connection if you load the wrong faction.

## YAML Configuration

Download the [template YAML](../player-settings) and configure your options:

```yaml
game: Timberborn
name: YourName
Timberborn:
  faction: folktails               # folktails | iron_teeth | random (IT must be unlocked first!)
  goal_selection:                   # pick any combination of victory conditions
    - Wonder
  goal_requirement: any             # any (complete one) | all (complete all)
  population_goal: 100              # target for Population goal
  population_mode: beavers_only     # beavers_only | bots_only | beavers_and_bots
  drought_cycles_goal: 25           # target for Droughts goal
  badtide_cycles_goal: 10           # target for Badtides goal
  wellbeing_goal: 15                # target for Well-being goal
  bots_goal: 10                     # target for Bots goal
  water_storage_goal: 5000          # target for Water Storage goal
  randomization_style: shuffle      # shuffle | grand_chaos
  drought_difficulty: 3             # 1 (easy) to 5 (brutal)
  include_traps: true
  max_science_cost: 5000            # max price for the most expensive shop location (1000-20000)
  skip_count: 3                     # number of Skip items in the pool (0-10)
  progressive_items: on             # off | grouped_random | on
  include_population_milestones: true
  include_wellbeing_milestones: true
  include_survival_milestones: true
  include_wonder_milestone: true
```
