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

    def create_regions(self) -> None:
        menu = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu)

        game_region = Region("Timberborn", self.player, self.multiworld)
        self.multiworld.regions.append(game_region)

        menu.connect(game_region)

        # Science locations — one per science-costed building
        for loc_name in ALL_SCIENCE_LOCATIONS:
            loc_id = location_name_to_id[loc_name]
            game_region.locations.append(
                TimberbornLocation(self.player, loc_name, loc_id, game_region)
            )

        # Milestone locations — population, wellbeing, survival, wonder
        for loc_name in ALL_MILESTONE_LOCATIONS:
            loc_id = location_name_to_id[loc_name]
            game_region.locations.append(
                TimberbornLocation(self.player, loc_name, loc_id, game_region)
            )

    def create_items(self) -> None:
        total_locations = len(location_name_to_id)
        items_created = 0

        # --- Blueprint items ---
        for item_name in BLUEPRINT_ITEMS:
            self.multiworld.itempool.append(self.create_item(item_name))
            items_created += 1

        # --- Boost items ---
        for name, classification in BOOSTS:
            self.multiworld.itempool.append(self.create_item(name))
            items_created += 1

        # --- Trap items (only if option enabled) ---
        if self.options.include_traps:
            for name, classification, count in TRAP_ITEMS:
                for _ in range(count):
                    self.multiworld.itempool.append(self.create_item(name))
                    items_created += 1

        # --- Filler — pad to match location count ---
        filler_needed = total_locations - items_created
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
        return {
            "goal": self.options.goal.value,
            "randomization_style": self.options.randomization_style.value,
            "include_traps": bool(self.options.include_traps.value),
            "population_goal": self.options.population_goal.value,
            "survival_cycles_goal": self.options.survival_cycles_goal.value,
            "drought_difficulty": self.options.drought_difficulty.value,
            "faction": "Folktails",  # hard-coded for v1; IronTeeth planned
        }
