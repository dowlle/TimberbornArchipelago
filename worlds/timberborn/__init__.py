from typing import Optional

from worlds.AutoWorld import World, WebWorld
from BaseClasses import Region, Location, Item, ItemClassification, Tutorial, CollectionState
from .Items import (TimberbornItem, item_table, item_name_to_id,
                    get_blueprint_items, get_building_names,
                    BLUEPRINT_ITEMS, TRAP_ITEMS, BOOSTS,
                    SCOUT_ITEMS, RESOURCE_PACKAGE_GOODS,
                    RESOURCE_PACKAGE_BASE_AMOUNTS, get_resource_package_weights,
                    scale_package_amount)
from .Locations import (TimberbornLocation, location_table, location_name_to_id,
                        ALL_BUILDING_NAMES,
                        POPULATION_LOCATIONS, WELLBEING_LOCATIONS,
                        SURVIVAL_LOCATIONS, FT_WONDER_LOCATIONS,
                        IT_WONDER_LOCATIONS, get_resource_milestones)
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
    elif name.startswith("Resource:"):
        return "resource"
    return "unknown"


# Maps resource milestone display name to game GoodId string.
# Display names are the rest of the milestone name after "Reach N ".
# Mirrored by MilestoneCodec in the client; ids checked against 1.1 Goods blueprints.
_RESOURCE_GOOD_IDS: dict[str, str] = {
    "Logs":              "Log",
    "Planks":            "Plank",
    "Gears":             "Gear",
    "Bread":             "Bread",
    "Metal Blocks":      "MetalBlock",
    "Treated Planks":    "TreatedPlank",
    "Scrap Metal":       "ScrapMetal",
    "Pine Resin":        "PineResin",
    "Water":             "Water",
    "Berries":           "Berries",
    "Extract":           "Extract",
    "Explosives":        "Explosives",
    "Paper":             "Paper",
    "Grilled Potatoes":  "GrilledPotato",
    "Cattail Crackers":  "CattailCracker",
    "Maple Pastries":    "MaplePastry",
    "Books":             "Book",
    "Biofuel":           "Biofuel",
    "Antidote":          "Antidote",
    "Corn Rations":      "CornRation",
    "Fermented Cassava": "FermentedCassava",
    "Eggplant Rations":  "EggplantRation",
    "Fermented Soybean": "FermentedSoybean",
    "Kohlrabi":          "Kohlrabi",
    "Mangrove Fruit":    "MangroveFruit",
    "Metal Parts":       "MetalPart",
    "Coffee":            "Coffee",
    "Grease":            "Grease",
}

# While the Water Storage goal is active, all water packages together must stay
# under this amount (the goal's minimum), because the goal counts water in stock.
_WATER_PACKAGE_LIMIT = 500


def _milestone_good_id(name: str) -> str:
    """For Resource: milestones, return the game GoodId string. Empty for non-resource."""
    if not name.startswith("Resource:"):
        return ""
    # "Resource: Reach 500 Logs" -> "Logs"
    # "Resource: Reach 100 Metal Blocks" -> "Metal Blocks"
    m = re.search(r"Reach \d+ (.+)$", name)
    if not m:
        return ""
    display = m.group(1)
    return _RESOURCE_GOOD_IDS.get(display, "")


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
    _water_packages: int = 0
    starting_items: list[str] | None = None

    # Starting blueprints (option starting_blueprints). The platform is the
    # smallest one both factions share: Platform, 1x1x1, 6 planks, 100 science.
    STARTING_BLUEPRINTS: tuple[str, ...] = ("Forester", "Stairs", "Platform")

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
        if self.options.include_resource_milestones:
            self.active_milestones.extend(get_resource_milestones(
                self.faction, self.options.resource_milestone_set.value))

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

        # Starting blueprints leave the pool and go to the start inventory.
        self.starting_items = []
        if self.options.starting_blueprints:
            for item_name in self._starting_item_names():
                blueprint_items.remove(item_name)
                self.multiworld.push_precollected(self.create_item(item_name))
                self.starting_items.append(item_name)

        for item_name in blueprint_items:
            self.multiworld.itempool.append(self.create_item(item_name))
            items_created += 1

        # Essential buildings must be available from sphere 1 (if option enabled)
        if self.options.force_early_items:
            if not self.options.starting_blueprints:
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

        # --- Resource packages — pad to match location count ---
        filler_needed = unfilled - items_created
        for _ in range(max(0, filler_needed)):
            self.multiworld.itempool.append(self.create_item(self._draw_resource_package()))

    def _starting_item_names(self) -> list[str]:
        """Item names of the starting blueprints; a chain member gives its first step."""
        names = []
        for building in self.STARTING_BLUEPRINTS:
            progressive = next((prog for prog, chain in (self._progressive_chains or {}).items()
                                if building in chain), None)
            if progressive is not None:
                assert self._progressive_chains[progressive][0] == building, building
                names.append(progressive)
            else:
                names.append(f"Blueprint: {building}")
        return names

    # -----------------------------------------------------------------
    # Resource packages — weighted random draw per faction
    # -----------------------------------------------------------------

    def resource_package_amount(self, name: str) -> int:
        """Delivered amount of a resource package after the size option."""
        return scale_package_amount(RESOURCE_PACKAGE_BASE_AMOUNTS[name],
                                    self.options.resource_package_size.value)

    def _max_water_packages(self) -> int | None:
        """Water package cap while the Water Storage goal is active, else None."""
        if "Water Storage" not in (self.resolved_goals or set()):
            return None
        return (_WATER_PACKAGE_LIMIT - 1) // self.resource_package_amount("Package: Water")

    def _draw_resource_package(self) -> str:
        """Draw one package by faction weight, keeping total water under the cap."""
        weights = get_resource_package_weights(self.faction)
        water_cap = self._max_water_packages()
        if water_cap is not None and self._water_packages >= water_cap:
            weights.pop("Package: Water", None)
        names = list(weights)
        name = self.random.choices(names, weights=[weights[n] for n in names])[0]
        if name == "Package: Water":
            self._water_packages += 1
        return name

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

        Population milestones provide the sphere-1 budget we need: three
        T1 milestone locations (First Beaver Born, First Beaver Grown Up,
        Reach 15 Beavers) on top of the 4 tier-1 shop slots gives us
        ~7 sphere-1 reachable locations, enough to absorb the 4 core
        forced items plus up to 3 random survival extras.

        Wellbeing and survival milestones each only contribute 1 T1 slot,
        and the wonder milestone is T5. Without population milestones,
        fill overflows on grand_chaos / restrictive configs. Skip extras
        entirely unless population milestones are enabled -- the 2026-04-18
        fuzz run caught ~3% failure rate when this guard was missing.
        """
        if not self.options.include_population_milestones:
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
        return self._draw_resource_package()

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
            # Precollected blueprints; the server also sends them as items.
            "starting_items": list(self.starting_items or []),
            "science_cost_multiplier": self.options.science_cost_multiplier.value,
            "skip_count": self.options.skip_count.value,
            "resource_milestone_set": self.options.resource_milestone_set.value,
            # Percent applied to every resource package. The client treats a
            # missing value as 100 (seeds generated before this option).
            "resource_package_percent": self.options.resource_package_size.value,
            # Final delivered amount and GoodId per package item this faction
            # can receive, so the client never derives amounts from item names.
            "resource_packages": {
                name: {
                    "good_id": RESOURCE_PACKAGE_GOODS[name],
                    "amount": self.resource_package_amount(name),
                }
                for name in get_resource_package_weights(self.faction)
            },
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
                    "good_id": _milestone_good_id(loc_name),  # non-empty for resource milestones
                }
                for loc_name in self.active_milestones
            ],
            # Maps each shop location_id (as string key) to the actual AP item name
            # placed there by the multiworld fill algorithm. The client uses this to
            # show the real item when a Scout reveals a path, instead of the layout's
            # original building_name which may differ after fill.
            # Only covers this world's own locations (planner-known). Items from other
            # players' games appear under their AP item name.
            "shop_placements": {
                str(location_name_to_id[e["location_name"]]): (
                    self.multiworld.get_location(e["location_name"], self.player).item.name
                    if self.multiworld.get_location(e["location_name"], self.player).item is not None
                    else e["building_name"]
                )
                for e in self.shop_layout
            },
        }
        return data
