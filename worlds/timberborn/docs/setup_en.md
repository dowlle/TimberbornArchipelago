# Timberborn Archipelago Setup Guide

## Required Software

- [Timberborn](https://store.steampowered.com/app/1062090/Timberborn/) 1.1 or newer
- [Archipelago](https://github.com/ArchipelagoMW/Archipelago/releases) 0.6.7 or newer
- The Timberborn Archipelago mod, from the [mod releases](https://github.com/dowlle/timberborn-modding/releases)

## Installing the Mod

1. Download `Archipelago.zip` from the latest [mod release](https://github.com/dowlle/timberborn-modding/releases) and extract it into `Documents/Timberborn/Mods/`, so you end up with a `Mods/Archipelago/` folder. Replace any older version.
2. Launch Timberborn. The mod should appear in the built-in Mod Manager; enable it.
3. Restart the game after enabling.

## Connecting to the Server

1. Start or load a game with the Archipelago mod enabled.
2. Click the **AP** button in the bottom bar to open the AP Shop.
3. Enter your server details in the connection fields of the AP Shop:
   - **Host**: hostname or IP (e.g. `archipelago.gg`, or `localhost` for a server on your own PC)
   - **Port**: your session's port number
   - **Slot**: your player name from the YAML
   - **Password**: leave blank if not set
4. Click **Connect**. The AP Shop will populate with your seed's layout.
5. Connection data is saved with your game, and the mod reconnects when you load that save.

## Playing

- The **AP Shop** has 4 branching paths (A, B, C, D). Each path has sequential locations with escalating science costs.
- Buy locations in order within each path; you can freely switch between paths.
- Higher-tier locations are gated by progression items (Gear Workshop, Scavenger Flag, etc.).
- **Skip** items let you check a location without spending science.
- **Milestones** (population, well-being, survival, wonder) trigger automatically as you play.
- Buildings unlock in your toolbar as you receive blueprint items from the multiworld.

## Important: Faction Selection

The mod unlocks both factions, so you can play Iron Teeth without unlocking it in a Folktails game first. Start your colony with the faction from your YAML: the mod blocks the connection if you load the wrong faction.

## YAML Configuration

Download the [template YAML](../player-settings) and configure your options:

```yaml
game: Timberborn
name: YourName
Timberborn:
  faction: folktails               # folktails | iron_teeth | random
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
  include_traps: true               # master switch for traps
  trap_percentage: 15               # % of filler slots that become traps (0-100)
  hazardous_weather_trap_weight: 50 # relative weight of each trap type (0-100, 0 removes it)
  hungry_beavers_trap_weight: 30
  thirsty_beavers_trap_weight: 20
  max_science_cost: 5000            # max price for the most expensive shop location (1000-20000)
  skip_count: 3                     # number of Skip items in the pool (0-10)
  progressive_items: on             # off | grouped_random | on
  include_population_milestones: true
  include_wellbeing_milestones: true
  include_survival_milestones: true
  include_wonder_milestone: true
```
