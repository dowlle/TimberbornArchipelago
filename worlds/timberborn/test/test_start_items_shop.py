"""Starting blueprints (#4), badwater gating for Explosives and Extract (#1)
and permanent IDs."""
import json
from pathlib import Path
import unittest

from BaseClasses import CollectionState

from . import TimberbornTestBase
from ..Items import PROGRESSION_BLUEPRINTS, get_building_names, item_name_to_id
from ..Locations import location_name_to_id
from ..Rules import (BADWATER_SOURCES, EXPLOSIVES_CONSUMERS, EXTRACT_CONSUMERS,
                     building_prerequisite_blueprints, wonder_blueprints)

FIXTURES = Path(__file__).parent / "fixtures"


def _names(items) -> list[str]:
    return [item.name for item in items]


class StartingItemChecks:
    expected_start: set[str] = set()

    def test_start_inventory(self):
        start = _names(self.multiworld.precollected_items[self.player])
        self.assertEqual(set(start), self.expected_start)
        self.assertEqual(len(start), len(self.expected_start))
        self.assertEqual(self.world.fill_slot_data()["starting_items"], start)

    def test_starting_items_left_the_pool(self):
        pool = _names(self.multiworld.itempool)
        for name in self.expected_start - {"Progressive Platforms"}:
            self.assertNotIn(name, pool)
        self.assertEqual(len(self.multiworld.itempool),
                         len(self.multiworld.get_unfilled_locations(self.player)))

    def test_platform_unlocks_in_logic(self):
        state = CollectionState(self.multiworld)
        for building in ("Forester", "Stairs", "Platform"):
            self.assertTrue(state.has(f"Blueprint: {building}", self.player), building)
        self.assertFalse(state.has("Blueprint: Double Platform", self.player))

    def test_force_early_keeps_levee_and_gear_workshop(self):
        early = self.multiworld.early_items[self.player]
        self.assertEqual(early.get("Blueprint: Levee"), 1)
        self.assertEqual(early.get("Blueprint: Gear Workshop"), 1)
        self.assertNotIn("Blueprint: Forester", early)
        self.assertNotIn("Blueprint: Stairs", early)


class TestFolktailsStartingItems(StartingItemChecks, TimberbornTestBase):
    options = {"faction": 0, "progressive_items": 2}
    expected_start = {"Blueprint: Forester", "Blueprint: Stairs", "Progressive Platforms"}

    def test_progressive_platforms_gives_first_step(self):
        self.assertEqual(_names(self.multiworld.itempool).count("Progressive Platforms"), 2)


class TestIronTeethStartingItems(StartingItemChecks, TimberbornTestBase):
    options = {"faction": 1, "progressive_items": 0}
    expected_start = {"Blueprint: Forester", "Blueprint: Stairs", "Blueprint: Platform"}


class TestIronTeethStartingItemsProgressive(StartingItemChecks, TimberbornTestBase):
    options = {"faction": 1, "progressive_items": 2}
    expected_start = {"Blueprint: Forester", "Blueprint: Stairs", "Progressive Platforms"}


class StartingItemsOffChecks:
    def test_nothing_precollected(self):
        self.assertEqual(self.multiworld.precollected_items[self.player], [])
        self.assertEqual(self.world.fill_slot_data()["starting_items"], [])
        pool = _names(self.multiworld.itempool)
        self.assertIn("Blueprint: Forester", pool)
        self.assertIn("Blueprint: Stairs", pool)

    def test_forester_and_stairs_forced_early(self):
        early = self.multiworld.early_items[self.player]
        for name in ("Forester", "Stairs", "Levee", "Gear Workshop"):
            self.assertEqual(early.get(f"Blueprint: {name}"), 1, name)


class TestFolktailsStartingItemsOff(StartingItemsOffChecks, TimberbornTestBase):
    options = {"faction": 0, "starting_blueprints": 0}


class TestIronTeethStartingItemsOff(StartingItemsOffChecks, TimberbornTestBase):
    options = {"faction": 1, "starting_blueprints": 0}


# ---------------------------------------------------------------------------
# Badwater gating (#1)
# ---------------------------------------------------------------------------

class TestBadwaterConsumerData(unittest.TestCase):
    def test_consumers_from_blueprints(self):
        # BuildingCost with Explosives: Dynamite, Double/Triple Dynamite, Tunnel, Detonator.
        self.assertEqual(EXPLOSIVES_CONSUMERS, {"Dynamite", "Double Dynamite", "Triple Dynamite",
                                                "Tunnel", "Detonator"})
        # BuildingCost, consumed good, nutrient or only recipe with Extract.
        self.assertEqual(EXTRACT_CONSUMERS, {
            "Double Dynamite", "Triple Dynamite", "Tunnel", "Detonator", "Memory",
            "Pole Banner", "Square Banner", "Agora", "Detailer", "Decontamination Pod",
            "Advanced Breeding Pod", "Grease Factory"})

    def test_prerequisites_include_the_badwater_source(self):
        for faction in ("Folktails", "IronTeeth"):
            names = set(get_building_names(faction))
            for building in sorted((EXPLOSIVES_CONSUMERS | EXTRACT_CONSUMERS) & names):
                with self.subTest(faction=faction, building=building):
                    required = set(building_prerequisite_blueprints(building, faction))
                    self.assertTrue(set(BADWATER_SOURCES[faction]) <= required)
                    if building in EXPLOSIVES_CONSUMERS:
                        self.assertIn("Explosives Factory", required)
                    if building in EXTRACT_CONSUMERS:
                        self.assertIn("Centrifuge", required)
        self.assertEqual(set(building_prerequisite_blueprints("Dynamite", "Folktails")),
                         {"Badwater Pump", "Explosives Factory", "Smelter", "Scavenger Flag",
                          "Gear Workshop", "Forester"})
        self.assertEqual(set(building_prerequisite_blueprints("Memory", "IronTeeth")),
                         {"Metalsmith", "Deep Badwater Pump", "Centrifuge", "Smelter",
                          "Gear Workshop", "Forester"})
        self.assertEqual(building_prerequisite_blueprints("Dance Pit", "IronTeeth"), ("Metalsmith",))
        self.assertEqual(building_prerequisite_blueprints("Refinery", "Folktails"), ())

    def test_every_required_blueprint_is_progression(self):
        required = set()
        for faction in ("Folktails", "IronTeeth"):
            for building in get_building_names(faction):
                required.update(building_prerequisite_blueprints(building, faction))
            required.update(wonder_blueprints(faction))
        for building in sorted(required):
            with self.subTest(building=building):
                self.assertIn(f"Blueprint: {building}", PROGRESSION_BLUEPRINTS)

    def test_folktails_wonder_needs_extract_and_paper(self):
        self.assertTrue({"Badwater Pump", "Centrifuge", "Medium Tank", "Paper Mill"}
                        <= set(wonder_blueprints("Folktails")))
        self.assertFalse({"Badwater Pump", "Deep Badwater Pump"} & set(wonder_blueprints("IronTeeth")))


def _collect_all_but(test, names):
    """collect_all_but on a fresh state, so calls do not accumulate."""
    test.multiworld.state = CollectionState(test.multiworld)
    test.collect_all_but(names)


class BadwaterGateChecks:
    faction = "Folktails"

    def _slot(self, building: str) -> str:
        return next(e["location_name"] for e in self.world.shop_layout
                    if e["building_name"] == building)

    def test_each_consumer_slot_needs_badwater(self):
        consumers = sorted((EXPLOSIVES_CONSUMERS | EXTRACT_CONSUMERS)
                           & set(get_building_names(self.faction)))
        self.assertTrue(consumers)
        for source in BADWATER_SOURCES[self.faction]:
            _collect_all_but(self, [f"Blueprint: {source}"])
            for building in consumers:
                with self.subTest(source=source, building=building):
                    self.assertFalse(self.can_reach_location(self._slot(building)))
        _collect_all_but(self, [])
        for building in consumers:
            with self.subTest(building=building, all_items=True):
                self.assertTrue(self.can_reach_location(self._slot(building)))

    def test_first_slots_have_no_prerequisites(self):
        for e in self.world.shop_layout:
            if e["tier"] == 1:
                self.assertEqual(building_prerequisite_blueprints(e["building_name"], self.faction), (),
                                 e["location_name"])

    def test_explosives_factory_and_centrifuge_gate_their_consumers(self):
        for producer, consumers in (("Explosives Factory", EXPLOSIVES_CONSUMERS),
                                    ("Centrifuge", EXTRACT_CONSUMERS)):
            _collect_all_but(self, [f"Blueprint: {producer}"])
            for building in sorted(consumers & set(get_building_names(self.faction))):
                with self.subTest(producer=producer, building=building):
                    self.assertFalse(self.can_reach_location(self._slot(building)))


class TestPrerequisiteBuildingsLeaveFirstSlots(unittest.TestCase):
    def test_layout_tier(self):
        from ..ShopLayout import layout_tier
        self.assertEqual(layout_tier("Agora", "Folktails"), 3)  # tier 1, needs Extract
        self.assertEqual(layout_tier("Detailer", "Folktails"), 4)
        self.assertEqual(layout_tier("Bench", "Folktails"), 1)
        self.assertEqual(layout_tier("Dance Pit", "IronTeeth"), 5)


class TestFolktailsBadwaterGates(BadwaterGateChecks, TimberbornTestBase):
    options = {"faction": 0, "progressive_items": 0}

    def test_wonder_needs_badwater(self):
        _collect_all_but(self, ["Blueprint: Badwater Pump"])
        self.assertFalse(self.can_reach_location("Wonder: Complete Earth Recultivator"))
        self.assertBeatable(False)
        _collect_all_but(self, [])
        self.assertTrue(self.can_reach_location("Wonder: Complete Earth Recultivator"))
        self.assertBeatable(True)


class TestIronTeethBadwaterGates(BadwaterGateChecks, TimberbornTestBase):
    options = {"faction": 1, "progressive_items": 0}
    faction = "IronTeeth"


# ---------------------------------------------------------------------------
# Permanent IDs
# ---------------------------------------------------------------------------

class TestIdsStable(unittest.TestCase):
    def test_fixture_ids_unchanged(self):
        for fixture, table in (("item_ids_before_1_1.json", item_name_to_id),
                               ("item_ids_before_resource_pool.json", item_name_to_id),
                               ("location_ids_before_resource_pool.json", location_name_to_id)):
            before = json.loads((FIXTURES / fixture).read_text())
            self.assertTrue(before, fixture)
            for name, code in before.items():
                with self.subTest(fixture=fixture, name=name):
                    self.assertEqual(table[name], code)
