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
2. Click the **Archipelago** button in the top-left HUD or in the Pause Menu.
3. Enter your server details:
   - **Server**: hostname or IP (e.g. `archipelago.gg`)
   - **Port**: your session's port number
   - **Slot Name**: your player name from the YAML
   - **Password**: leave blank if not set
4. Click **Connect**. A confirmation message appears in the in-game console.

## YAML Configuration

Download the [template YAML](../player-settings) and configure your options:

```yaml
game: Timberborn
name: YourName
Timberborn:
  goal: complete_wonder          # complete_wonder | reach_population | survive_cycles
  randomization_style: shuffle   # shuffle | grand_chaos
  population_goal: 100           # used when goal is reach_population
  survival_cycles_goal: 30       # used when goal is survive_cycles
  drought_difficulty: 3          # 1 (easy) to 5 (brutal)
  include_traps: true
```
