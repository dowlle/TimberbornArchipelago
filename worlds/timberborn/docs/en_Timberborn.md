# Timberborn

## Where is the settings page?

The [player settings page for this game](../player-settings) contains all the options for configuring your randomizer experience.

## What does randomization do to this game?

Building blueprints that are normally unlocked through the Science system are shuffled into the multiworld item pool. An in-game **AP Shop** with 4 branching paths lets you spend Science Points to send checks to the server. Each path has sequential locations with escalating costs — you must buy them in order within each path, but can freely switch between paths.

Your colony must survive on whatever tech arrives from the multiworld while sending checks to unlock buildings for everyone else.

## What is the goal when randomized?

Pick one or more goals in Goal Selection, and whether any or all of them must be completed:
- **Wonder** *(default)*: complete your faction's Wonder (Earth Recultivator or Earth Repopulator) in this game. A wonder finished in an earlier game on the same map does not count.
- **Population**: grow your colony to the target count.
- **Droughts**: survive a number of droughts (5 to 40, default 15).
- **Badtides**: survive a number of badtides (1 to 20, default 5).
- **Well-being**: reach an average well-being level.
- **Bots**: build a number of bots.
- **Water Storage**: hold an amount of water in stock.

A drought or badtide counts when it ends, and only hazards after you connect count, for the goals and for the survival milestones.

### Survival in logic

The first badtide comes on a fixed cycle whatever items you have, so Force Early Items puts the Floodgate (or the first Progressive Flood Control) and the Medium Tank in the first sphere (with Starting Blueprints on, the default). Logic expects these buildings before it expects you to live through a hazard:

| | Droughts | Badtides |
|---|---|---|
| Early (droughts 1 to 5, badtides 1 to 3) | Levee, Floodgate, Stairs | Floodgate, Levee, Medium Tank |
| Mid (droughts 6 to 15, badtides 4 to 10) | early plus Medium Tank, Double Floodgate, Platform | early plus Double Floodgate, Contamination Sensor and the cure: Herbalist and Paper Mill (Folktails) or Decontamination Pod (Iron Teeth) |
| Late (more) | mid plus Large Tank or Triple Floodgate, and Gravity Battery, Geothermal Engine or Wind Turbine (Iron Teeth: Steam Engine) | mid plus Large Tank and a Mechanical Fluid Pump or Compact Mechanical Pump (Iron Teeth: Large Water Wheel and a Deep Mechanical Fluid Pump or Compact Mechanical Pump) |

The survival milestones use it as 1st = early, 5 = mid, 10 = late. The Droughts and Badtides goals pick the row from their target, as shown. Long goals (Wonder, Population 100 or more, Well-being 20 or more, Water Storage 5000 or more) need mid drought and early badtide survival.

## Which items can be in another player's world?

- **Blueprints** — 126 individual building unlocks (e.g., *Forester*, *Gear Workshop*, *Smelter*). With Starting Blueprints on (default), Forester, Stairs and Platform are in your starting inventory instead and unlock as soon as you connect.
- **Passive Boosts** — faster movement, increased carrying capacity, faster working speed, faster tree growth, longer life expectancy.
- **Skip** — lets you check a shop location for free (bypasses science cost).
- **Resource packages** — goods for your faction, such as *Package: Logs* (100 Logs) or *Package: Bread* (60 Bread). The Resource Package Size option scales every amount (10% to 1000%).
- **Traps** *(optional)* — negative effects like *Hazardous Weather* (triggers an early drought or badtide) or *Hungry Beavers*. Include Traps turns them on or off. Trap Percentage (0 to 100, default 15) sets how many of the filler slots, the slots left after blueprints, boosts, scouts and skips, become traps instead of resource packages. The count is rounded half up; a default seed has 69 filler slots, so 15% gives 10 traps. Three weights (0 to 100) set how often each trap type appears: Hazardous Weather 50, Hungry Beavers 30 and Thirsty Beavers 20 by default. Each trap is drawn with a chance of its weight divided by the sum of the weights. A weight of 0 removes that trap type, and with all three at 0 there are no traps.

## What does another player's item look like in my game?

The AP Shop presents abstract locations (e.g., "A-01", "B-05") with escalating science costs. Purchasing a location sends a check to the server — you don't know what item you'll send until you buy it. The shop is gated by 5 tiers that unlock as you receive key progression items (Gear Workshop, Scavenger Flag, Smelter, etc.). A blueprint is only placed in a shop slot of its own tier or higher, so a Smelter never sits in a tier 1 slot. A blueprint that a slot needs before it opens, such as the Smelter for tier 3, may sit one tier lower, and blueprints forced into the first sphere may sit in tier 1. A locked path shows what it still needs, such as the previous check, missing blueprints or more science, without revealing the item.

Buildings that use Explosives or Extract (Dynamite, Tunnel, Detonator, banners, Memory, Agora, Detailer and others) also need a badwater source in logic: Badwater Pump for Folktails, Deep Badwater Pump and Metalsmith for Iron Teeth.

## Milestone locations

In addition to shop locations, milestone locations trigger automatically as you play:

- **Population milestones** — first beaver born, first grown up, reaching 10/25/50/100/200 beavers
- **Well-being milestones** — reaching well-being levels 5/10/15/20
- **Survival milestones** — surviving 1st/5th/10th drought, 1st/5th/10th badtide, counted when each hazard ends
- **Wonder milestone** — completing your faction's Wonder in this game
- **Resource milestones** — reaching a stock of a good, such as 25 Gears or 500 Logs. Resource Milestone Set picks classic (13), lite (31) or full (61, default). Each is in logic once you have the buildings that produce the good.

Each milestone type can be toggled on/off in the YAML settings.

## When the player receives an item, what happens?

Items received from the server are applied immediately to your current session. Blueprints become available in the build menu and passive boosts apply globally.

Resource packages are delivered according to the Goods Delivery option:
- **district_center** *(default)*: into the District Center with the most beavers, the way the game gives your starting goods. Its workers haul the goods to storage, builders can use them right away, and beavers eat and drink from it. Goods it does not take go to storage.
- **storage**: into finished storage buildings that take the good and have room.

In both modes, goods that find no place wait and are delivered as soon as there is room.
