from typing import Optional

from worlds.AutoWorld import World, WebWorld
from BaseClasses import Region, Location, Item, ItemClassification, Tutorial, CollectionState
from .Items import (TimberbornItem, item_table, item_name_to_id,
                    get_blueprint_items, get_building_names,
                    BLUEPRINT_ITEMS, FILLER_ITEMS, TRAP_ITEMS, BOOSTS,
                    SCOUT_ITEMS)
from .Locations import (TimberbornLocation, location_table, location_name_to_id,
                        ALL_BUILDING_NAMES,
                        POPULATION_LOCATIONS, WELLBEING_LOCATIONS,
                        SURVIVAL_LOCATIONS, FT_WONDER_LOCATIONS,
                        IT_WONDER_LOCATIONS)
from .Options import TimberbornOptions
from .ProgressiveItems import get_progressive_chains, get_building_to_progressive
from .BuildingTiers import get_building_tier
from .Rules import set_rules


import re


def _milestone_type(name: str) -> str:
    if name.startswith("Population:"):
        return "population"
    elif name.startswith("Well-being:"):
        return "wellbeing"
    elif name.startswith("Survival:"):
        return "survival"
    elif name.startswith("Wonder:"):
        return "wonder"
    return "unknown"


def _milestone_threshold(name: str) -> int:
    """Extract numeric threshold from milestone name (e.g. 'Reach 10 Beavers' -> 10)."""
    if "First Beaver Born" in name:
        return 1
    if "First Beaver Grown Up" in name:
        return 1
    if "Complete" in name:
        return 1
    m = re.search(r"(\d+)", name)
    return int(m.group(1)) if m else 0


class TimberbornWebWorld(WebWorld):
    theme = "dirt"
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Timberborn for Archipelago.",
        "English",
        "setup_en.md",
        "setup/en",
        ["your-name-here"]
    )]


class TimberbornWorld(World):
    """
    Timberborn is a city-building survival game where you manage a colony of
    beavers through droughts and badtides. Building blueprints that normally
    cost Science Points are shuffled into the multiworld — you must survive on
    whatever tech arrives while sending checks to unlock buildings for others.
    Supports Folktails and Iron Teeth factions.
    """

    game = "Timberborn"
    web = TimberbornWebWorld()
    options_dataclass = TimberbornOptions

    item_name_to_id = item_name_to_id
    location_name_to_id = location_name_to_id

    # Set during create_regions
    faction: str | None = None
    shop_layout: list[dict] | None = None
    active_milestones: list[str] | None = None
    resolved_goals: set[str] | None = None
    _progressive_chains: dict[str, tuple[str, ...]] | None = None

    def create_regions(self) -> None:
        from .ShopLayout import generate_shop_layout

        # Determine faction
        self.faction = "IronTeeth" if self.options.faction.value == 1 else "Folktails"

        # Resolve progressive item chains based on option
        prog_opt = self.options.progressive_items.value
        if prog_opt == 2:  # on
            self._progressive_chains = get_progressive_chains(self.faction, True)
        elif prog_opt == 1:  # grouped_random
            all_chains = get_progressive_chains(self.faction, True)
            self._progressive_chains = {
                name: chain for name, chain in all_chains.items()
                if self.random.choice([True, False])
            }
        else:  # off
            self._progressive_chains = {}

        menu = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu)

        # Milestones region
        game_region = Region("Timberborn", self.player, self.multiworld)
        self.multiworld.regions.append(game_region)
        menu.connect(game_region)

        # Build active milestone list based on options
        self.active_milestones = []
        if self.options.include_population_milestones:
            self.active_milestones.extend(POPULATION_LOCATIONS)
        if self.options.include_wellbeing_milestones:
            self.active_milestones.extend(WELLBEING_LOCATIONS)
        if self.options.include_survival_milestones:
            self.active_milestones.extend(SURVIVAL_LOCATIONS)
        # Force-enable Wonder milestone if Wonder goal is active
        wonder_locs = IT_WONDER_LOCATIONS if self.faction == "IronTeeth" else FT_WONDER_LOCATIONS
        if self.options.include_wonder_milestone or "Wonder" in self.options.goal_selection.value:
            self.active_milestones.extend(wonder_locs)

        for loc_name in self.active_milestones:
            loc_id = location_name_to_id[loc_name]
            game_region.locations.append(
                TimberbornLocation(self.player, loc_name, loc_id, game_region)
            )

        # Victory event locations for client-tracked goals.
        # The client sends these events when in-game conditions are met.
        from .Rules import _resolve_goals
        self.resolved_goals = _resolve_goals(self)
        client_goals = self.resolved_goals - {"Wonder"}
        for goal_name in sorted(client_goals):
            event_name = f"Victory: {goal_name}"
            event_loc = TimberbornLocation(self.player, event_name, None, game_region)
            event_loc.place_locked_item(
                TimberbornItem(event_name, ItemClassification.progression, None, self.player)
            )
            game_region.locations.append(event_loc)

        # Branching shop — 4 paths with sequential ordering
        building_names = get_building_names(self.faction)
        self.shop_layout = generate_shop_layout(
            self,
            building_names,
            self.options.max_science_cost.value,
            self.options.science_cost_multiplier.value,
        )
        shop_region = Region("Shop", self.player, self.multiworld)
        self.multiworld.regions.append(shop_region)
        menu.connect(shop_region)

        for entry in self.shop_layout:
            loc_name = entry["location_name"]
            loc_id = location_name_to_id[loc_name]
            loc = TimberbornLocation(self.player, loc_name, loc_id, shop_region)
            shop_region.locations.append(loc)

        # Event locations for sequential enforcement within paths.
        path_levels: dict[str, list[tuple[int, str]]] = {}
        for entry in self.shop_layout:
            path = entry["path"]
            if path not in path_levels:
                path_levels[path] = []
            path_levels[path].append((entry["level"], entry["location_name"]))
        for path in path_levels:
            path_levels[path].sort()

        for path, entries in path_levels.items():
            for idx, (level, loc_name) in enumerate(entries):
                if idx < len(entries) - 1:
                    event_name = f"Event: {loc_name} Checked"
                    event_loc = TimberbornLocation(
                        self.player, event_name, None, shop_region
                    )
                    event_loc.place_locked_item(
                        TimberbornItem(event_name, ItemClassification.progression,
                                       None, self.player)
                    )
                    shop_region.locations.append(event_loc)

    def create_items(self) -> None:
        # Event locations (locked items) don't need pool items, so count only
        # locations that are NOT events (i.e., have no pre-placed item).
        unfilled = len(self.multiworld.get_unfilled_locations(self.player))
        items_created = 0

        # --- Blueprint items (faction-specific, with progressive swaps) ---
        blueprint_items = get_blueprint_items(self.faction, self._progressive_chains)
        for item_name in blueprint_items:
            self.multiworld.itempool.append(self.create_item(item_name))
            items_created += 1

        # Essential buildings must be available from sphere 1 (if option enabled)
        if self.options.force_early_items:
            self.multiworld.early_items[self.player]["Blueprint: Forester"] = 1
            self.multiworld.early_items[self.player]["Blueprint: Stairs"] = 1
            self.multiworld.early_items[self.player]["Blueprint: Levee"] = 1
            self.multiworld.early_items[self.player]["Blueprint: Gear Workshop"] = 1

            # Randomly sample survival buildings into early spheres.
            # Each category picks 1 random candidate per seed for variety.
            # Only picks buildings whose construction tier is achievable from
            # the already-forced early items (Gear Workshop → T2 is buildable).
            if self.options.extra_early_survival:
                self._force_random_early_survival()

        # --- Boost items ---
        for name, classification in BOOSTS:
            if items_created >= unfilled:
                break
            self.multiworld.itempool.append(self.create_item(name))
            items_created += 1

        # --- Scout items ---
        for name, classification in SCOUT_ITEMS:
            if items_created >= unfilled:
                break
            self.multiworld.itempool.append(self.create_item(name))
            items_created += 1

        # --- Dynamic skip & trap counts ---
        # Remaining slots after blueprints + boosts + scouts are split between
        # skips, traps, and filler.  Skips and traps are capped to fit.
        remaining = unfilled - items_created
        skip_requested = self.options.skip_count.value
        trap_requested = sum(c for _, _, c in TRAP_ITEMS) if self.options.include_traps else 0
        total_requested = skip_requested + trap_requested

        if total_requested > remaining:
            # Scale both down proportionally, skips first
            skip_actual = min(skip_requested, remaining // 2)
            trap_actual = min(trap_requested, remaining - skip_actual)
        else:
            skip_actual = skip_requested
            trap_actual = trap_requested

        for _ in range(skip_actual):
            self.multiworld.itempool.append(self.create_item("Skip"))
            items_created += 1

        if trap_actual > 0:
            # Build flat trap list and trim to budget
            trap_pool = [name for name, _, count in TRAP_ITEMS for _ in range(count)]
            self.random.shuffle(trap_pool)
            for name in trap_pool[:trap_actual]:
                self.multiworld.itempool.append(self.create_item(name))
                items_created += 1

        # --- Filler — pad to match location count ---
        filler_needed = unfilled - items_created
        if filler_needed > 0:
            filler_cycle = [name for name, _, count in FILLER_ITEMS for _ in range(count)]
            for i in range(filler_needed):
                name = filler_cycle[i % len(filler_cycle)]
                self.multiworld.itempool.append(self.create_item(name))

    # -----------------------------------------------------------------
    # Early survival items — random per seed
    # -----------------------------------------------------------------

    # Categories of buildings that help early survival.
    # Picked from per seed so each run feels different.
    _EARLY_SURVIVAL_CATEGORIES: dict[str, dict[str, list[str]]] = {
        "Folktails": {
            "housing":   ["Mini Lodge", "Double Lodge", "Triple Lodge"],
            "food":      ["Aquatic Farmhouse", "Gristmill", "Beehive"],
            "wellbeing": ["Lido", "Herbalist"],
        },
        "IronTeeth": {
            "housing":   ["Rowhouse", "Large Barrack", "Large Rowhouse"],
            # IT has no low-tier food buildings; free FarmHouse covers basics
            "wellbeing": ["Double Shower", "Scratcher", "Swimming Pool"],
        },
    }

    def _force_random_early_survival(self) -> None:
        """Pick one random building per survival category into early items.

        Only considers buildings whose construction tier is achievable
        from the already-forced early items (Gear Workshop is forced,
        so T1-T2 are buildable).  Skips buildings consumed by active
        progressive chains — those arrive as progressive items instead.

        Milestones provide extra sphere-0 locations.  Without them,
        only 4 shop slots are reachable and the core 4 early items
        already fill those, so we skip the extras to avoid fill errors.
        """
        if not self.active_milestones:
            return

        max_early_tier = 2  # Gear Workshop is forced -> T2 is buildable
        categories = self._EARLY_SURVIVAL_CATEGORIES.get(self.faction, {})
        prog_buildings = get_building_to_progressive(
            self.faction, bool(self._progressive_chains))

        for cat_name, candidates in categories.items():
            eligible = [
                b for b in candidates
                if get_building_tier(b, self.faction) <= max_early_tier
                and b not in prog_buildings
            ]
            if not eligible:
                continue
            pick = self.random.choice(eligible)
            self.multiworld.early_items[self.player][f"Blueprint: {pick}"] = 1

    def create_item(self, name: str) -> Item:
        data = item_table[name]
        return TimberbornItem(name, data["classification"], data["id"], self.player)

    def get_filler_item_name(self) -> str:
        filler_names = [name for name, _, _ in FILLER_ITEMS]
        return self.random.choice(filler_names)

    def set_rules(self) -> None:
        set_rules(self)

    def collect_item(self, state: CollectionState, item: Item,
                     remove: bool = False) -> Optional[str]:
        """Map progressive item receipts to concrete building names.

        When a player receives "Progressive Platforms", the first receipt
        adds "Blueprint: Platform" to state, the second adds
        "Blueprint: Double Platform", etc.  Rules.py checks the concrete
        building names, so logic works transparently.
        """
        if item.advancement and self._progressive_chains and item.name in self._progressive_chains:
            chain = self._progressive_chains[item.name]
            if remove:
                for building in reversed(chain):
                    bp = f"Blueprint: {building}"
                    if state.has(bp, item.player):
                        return bp
            else:
                for building in chain:
                    bp = f"Blueprint: {building}"
                    if not state.has(bp, item.player):
                        return bp
            return None
        return super().collect_item(state, item, remove)

    def fill_slot_data(self) -> dict:
        data = {
            "goals": sorted(self.resolved_goals),
            "goal_requirement": self.options.goal_requirement.value,  # 0=any, 1=all
            "randomization_style": self.options.randomization_style.value,
            "include_traps": bool(self.options.include_traps.value),
            "trap_mode": self.options.trap_mode.value,  # 0=queue, 1=skip
            "population_goal": self.options.population_goal.value,
            "population_mode": self.options.population_mode.value,
            "drought_cycles_goal": self.options.drought_cycles_goal.value,
            "badtide_cycles_goal": self.options.badtide_cycles_goal.value,
            "wellbeing_goal": self.options.wellbeing_goal.value,
            "bots_goal": self.options.bots_goal.value,
            "water_storage_goal": self.options.water_storage_goal.value,
            "drought_difficulty": self.options.drought_difficulty.value,
            "faction": self.faction,
            "science_cost_multiplier": self.options.science_cost_multiplier.value,
            "skip_count": self.options.skip_count.value,
            "progressive_chains": {
                name: list(chain)
                for name, chain in (self._progressive_chains or {}).items()
            },
            "shop_layout": [
                {
                    "path": e["path"],
                    "level": e["level"],
                    "price": e["price"],
                    "tier": e["tier"],
                    "location_id": location_name_to_id[e["location_name"]],
                    "building_name": e["building_name"],
                }
                for e in self.shop_layout
            ],
            "milestones": [
                {
                    "name": loc_name,
                    "location_id": location_name_to_id[loc_name],
                    "type": _milestone_type(loc_name),
                    "threshold": _milestone_threshold(loc_name),
                }
                for loc_name in self.active_milestones
            ],
        }
        return data
