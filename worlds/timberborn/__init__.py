from worlds.AutoWorld import World, WebWorld
from BaseClasses import Region, Location, Item, ItemClassification, Tutorial
from .Items import (TimberbornItem, item_table, item_name_to_id,
                    BLUEPRINT_ITEMS, FILLER_ITEMS, TRAP_ITEMS, BOOSTS)
from .Locations import (TimberbornLocation, location_table, location_name_to_id,
                        ALL_SCIENCE_LOCATIONS, ALL_MILESTONE_LOCATIONS)
from .Options import TimberbornOptions
from .Rules import set_rules


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
    (Folktails faction. Iron Teeth support planned for a future version.)
    """

    game = "Timberborn"
    web = TimberbornWebWorld()
    options_dataclass = TimberbornOptions

    item_name_to_id = item_name_to_id
    location_name_to_id = location_name_to_id

    # Set during create_regions when shop_style == branching
    shop_layout: list[dict] | None = None

    def create_regions(self) -> None:
        menu = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu)

        # Milestones region — always present
        game_region = Region("Timberborn", self.player, self.multiworld)
        self.multiworld.regions.append(game_region)
        menu.connect(game_region)

        for loc_name in ALL_MILESTONE_LOCATIONS:
            loc_id = location_name_to_id[loc_name]
            game_region.locations.append(
                TimberbornLocation(self.player, loc_name, loc_id, game_region)
            )

        if self.options.shop_style.value == 1:  # branching
            from .ShopLayout import generate_shop_layout
            self.shop_layout = generate_shop_layout(
                self,
                list(ALL_SCIENCE_LOCATIONS),
                self.options.max_science_cost.value,
            )
            shop_region = Region("Shop", self.player, self.multiworld)
            self.multiworld.regions.append(shop_region)
            menu.connect(shop_region)

            for entry in self.shop_layout:
                loc_name = entry["location_name"]
                loc_id = location_name_to_id[loc_name]
                loc = TimberbornLocation(self.player, loc_name, loc_id, shop_region)
                shop_region.locations.append(loc)

            # Create event locations for sequential enforcement within paths.
            # For each non-last location in a path, create a separate event
            # location (address=None) with a locked progression item.  The next
            # real location's access rule requires state.has(event_name).
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
                        # Event location: same region, no address (won't be sent
                        # to client or count toward pool).
                        event_loc = TimberbornLocation(
                            self.player, event_name, None, shop_region
                        )
                        event_loc.place_locked_item(
                            TimberbornItem(event_name, ItemClassification.progression,
                                           None, self.player)
                        )
                        shop_region.locations.append(event_loc)

        else:  # flat
            self.shop_layout = None
            for loc_name in ALL_SCIENCE_LOCATIONS:
                loc_id = location_name_to_id[loc_name]
                game_region.locations.append(
                    TimberbornLocation(self.player, loc_name, loc_id, game_region)
                )

    def create_items(self) -> None:
        # Event locations (locked items) don't need pool items, so count only
        # locations that are NOT events (i.e., have no pre-placed item).
        unfilled = len(self.multiworld.get_unfilled_locations(self.player))
        items_created = 0

        # --- Blueprint items ---
        for item_name in BLUEPRINT_ITEMS:
            self.multiworld.itempool.append(self.create_item(item_name))
            items_created += 1

        # --- Boost items ---
        for name, classification in BOOSTS:
            self.multiworld.itempool.append(self.create_item(name))
            items_created += 1

        # --- Skip items (branching shop only) ---
        if self.options.shop_style.value == 1:
            for _ in range(self.options.skip_count.value):
                if items_created >= unfilled:
                    break
                self.multiworld.itempool.append(self.create_item("Skip"))
                items_created += 1

        # --- Trap items (only if option enabled) ---
        if self.options.include_traps:
            for name, classification, count in TRAP_ITEMS:
                for _ in range(count):
                    if items_created >= unfilled:
                        break
                    self.multiworld.itempool.append(self.create_item(name))
                    items_created += 1

        # --- Filler — pad to match location count ---
        filler_needed = unfilled - items_created
        if filler_needed > 0:
            filler_cycle = [name for name, _, count in FILLER_ITEMS for _ in range(count)]
            for i in range(filler_needed):
                name = filler_cycle[i % len(filler_cycle)]
                self.multiworld.itempool.append(self.create_item(name))

    def create_item(self, name: str) -> Item:
        data = item_table[name]
        return TimberbornItem(name, data["classification"], data["id"], self.player)

    def get_filler_item_name(self) -> str:
        filler_names = [name for name, _, _ in FILLER_ITEMS]
        return self.random.choice(filler_names)

    def set_rules(self) -> None:
        set_rules(self)

    def fill_slot_data(self) -> dict:
        data = {
            "goal": self.options.goal.value,
            "randomization_style": self.options.randomization_style.value,
            "include_traps": bool(self.options.include_traps.value),
            "population_goal": self.options.population_goal.value,
            "survival_cycles_goal": self.options.survival_cycles_goal.value,
            "drought_difficulty": self.options.drought_difficulty.value,
            "faction": "Folktails",  # hard-coded for v1; IronTeeth planned
            "shop_style": self.options.shop_style.value,
        }
        if self.shop_layout is not None:
            # Send layout WITHOUT location names — client sees only abstract paths
            data["shop_layout"] = [
                {
                    "path": e["path"],
                    "level": e["level"],
                    "price": e["price"],
                    "tier": e["tier"],
                    "location_id": location_name_to_id[e["location_name"]],
                }
                for e in self.shop_layout
            ]
            data["skip_count"] = self.options.skip_count.value
        return data
