# Timberborn

## Where is the settings page?

The [player settings page for this game](../player-settings) contains all the options for configuring your randomizer experience.

## What does randomization do to this game?

Building blueprints that are normally unlocked through the Science system are shuffled into the multiworld item pool. An in-game **AP Shop** with 4 branching paths lets you spend Science Points to send checks to the server. Each path has sequential locations with escalating costs — you must buy them in order within each path, but can freely switch between paths.

Your colony must survive on whatever tech arrives from the multiworld while sending checks to unlock buildings for everyone else.

## What is the goal when randomized?

The goal is configurable:
- **Complete Wonder** *(default)*: Construct your faction's Wonder building (Earth Recultivator).
- **Reach Population**: Grow your colony to the target beaver count.
- **Survive Cycles**: Survive a set number of drought cycles.

## Which items can be in another player's world?

- **Blueprints** — 126 individual building unlocks (e.g., *Forester*, *Gear Workshop*, *Smelter*).
- **Passive Boosts** — faster movement, increased carrying capacity, faster working speed, faster tree growth, longer life expectancy.
- **Skip** — lets you check a shop location for free (bypasses science cost).
- **Filler** — resource care packages (50 Logs, 20 Planks, etc.).
- **Traps** *(optional)* — negative effects like *Hazardous Weather* (triggers an early drought or badtide) or *Hungry Beavers*.

## What does another player's item look like in my game?

The AP Shop presents abstract locations (e.g., "A-01", "B-05") with escalating science costs. Purchasing a location sends a check to the server — you don't know what item you'll send until you buy it. The shop is gated by 5 tiers that unlock as you receive key progression items (Gear Workshop, Scavenger Flag, Smelter, etc.).

## Milestone locations

In addition to shop locations, milestone locations trigger automatically as you play:

- **Population milestones** — first beaver born, first grown up, reaching 10/25/50/100/200 beavers
- **Well-being milestones** — reaching well-being levels 5/10/15/20
- **Survival milestones** — surviving 1st/5th/10th drought, 1st/5th/10th badtide
- **Wonder milestone** — completing the Earth Recultivator

Each milestone type can be toggled on/off in the YAML settings.

## When the player receives an item, what happens?

Items received from the server are applied immediately to your current session. Blueprints become available in the build menu; resource bundles are deposited at your nearest District Center; passive boosts apply globally.
