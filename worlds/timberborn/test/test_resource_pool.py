import json
from pathlib import Path
import unittest

from BaseClasses import CollectionState, ItemClassification

from . import TimberbornTestBase
from ..Items import (RESOURCE_PACKAGES, PROGRESSION_BLUEPRINTS, item_name_to_id, item_table,
                     get_resource_package_weights, scale_package_amount)
from ..Locations import (RESOURCE_MILESTONE_LOCATIONS, location_name_to_id,
                         get_resource_milestones)
from ..Rules import RESOURCE_CHAINS, parse_resource_milestone, resource_chain_blueprints
from .. import _RESOURCE_GOOD_IDS

FIXTURES = Path(__file__).parent / "fixtures"

# GoodCollection.Common + faction collection from the 1.1 blueprints.
_COMMON_GOODS = {"Badwater", "Berries", "Dirt", "Explosives", "Extract", "Fireworks", "Gear",
                 "Log", "MetalBlock", "PineResin", "Plank", "ScrapMetal", "Water"}
FACTION_GOODS = {
    "Folktails": _COMMON_GOODS | {
        "Antidote", "Biofuel", "Book", "BotChassis", "BotHead", "BotLimb", "Bread", "Carrot",
        "Catalyst", "CattailCracker", "CattailFlour", "CattailRoot", "Chestnut", "Dandelion",
        "GrilledChestnut", "GrilledPotato", "GrilledSpadderdock", "MaplePastry", "MapleSyrup",
        "Paper", "Potato", "PunchCard", "Spadderdock", "SunflowerSeeds", "TreatedPlank",
        "Wheat", "WheatFlour"},
    "IronTeeth": _COMMON_GOODS | {
        "Algae", "AlgaeRation", "BotChassis", "BotHead", "BotLimb", "CanolaOil", "CanolaSeeds",
        "Cassava", "Coffee", "CoffeeBean", "Corn", "CornRation", "Eggplant", "EggplantRation",
        "FermentedCassava", "FermentedMushroom", "FermentedSoybean", "Grease", "Kohlrabi",
        "MangroveFruit", "MetalPart", "Mushroom", "Soybean", "TreatedPlank"},
}
EXCLUDED_PACKAGE_GOODS = {"Badwater", "BotChassis", "BotHead", "BotLimb"}
PROMOTED = {"Gristmill", "Aquatic Farmhouse", "Printing Press", "Herbalist", "Badwater Pump",
            "Centrifuge", "Food Factory", "Oil Press", "Coffee Brewery", "Grease Factory",
            "Deep Badwater Pump"}
LEGACY_FILLER = {"Filler: 50 Logs", "Filler: 20 Planks", "Filler: 10 Gears", "Filler: 20 Bread",
                 "Filler: 5 Metal Blocks", "Filler: 10 Treated Planks", "Filler: 5 Scrap Metal"}


def _good_of(milestone: str) -> str:
    return parse_resource_milestone(milestone)[0]


class TestPermanentIdsAcrossResourcePool(unittest.TestCase):
    def test_every_pre_existing_item_id_is_unchanged(self):
        before = json.loads((FIXTURES / "item_ids_before_resource_pool.json").read_text())
        self.assertEqual(len(before), 203)
        for name, code in before.items():
            with self.subTest(item=name):
                self.assertEqual(item_name_to_id[name], code)

    def test_every_pre_existing_location_id_is_unchanged(self):
        before = json.loads((FIXTURES / "location_ids_before_resource_pool.json").read_text())
        self.assertEqual(len(before), 192)
        for name, code in before.items():
            with self.subTest(location=name):
                self.assertEqual(location_name_to_id[name], code)

    def test_new_ids_are_appended_and_unique(self):
        self.assertEqual(len(item_name_to_id), 203 + len(RESOURCE_PACKAGES))
        self.assertEqual(len(set(item_name_to_id.values())), len(item_name_to_id))
        self.assertEqual(len(location_name_to_id), 192 + 71)
        self.assertEqual(len(set(location_name_to_id.values())), len(location_name_to_id))
        self.assertEqual(len(RESOURCE_MILESTONE_LOCATIONS), len(set(RESOURCE_MILESTONE_LOCATIONS)))
        self.assertEqual(location_name_to_id["Resource: Reach 500 Corn Rations"], 9_710_013)
        self.assertEqual(item_name_to_id["Package: Logs"], 9_210_007)
        for name, *_ in RESOURCE_PACKAGES:
            self.assertTrue(9_210_000 <= item_name_to_id[name] < 9_220_000, name)
            self.assertEqual(item_table[name]["classification"], ItemClassification.filler)


class TestMilestoneSets(unittest.TestCase):
    def test_counts_per_faction_and_set(self):
        for faction in ("Folktails", "IronTeeth"):
            with self.subTest(faction=faction):
                classic, lite, full = (get_resource_milestones(faction, s) for s in (0, 1, 2))
                self.assertEqual((len(classic), len(lite), len(full)), (13, 31, 61))
                self.assertTrue(set(classic) <= set(lite) <= set(full))

    def test_faction_split(self):
        ft, it = get_resource_milestones("Folktails"), get_resource_milestones("IronTeeth")
        self.assertIn("Resource: Reach 500 Bread", ft)
        self.assertNotIn("Resource: Reach 500 Bread", it)
        self.assertIn("Resource: Reach 500 Corn Rations", it)
        self.assertNotIn("Resource: Reach 500 Corn Rations", ft)
        self.assertEqual(len(set(ft) & set(it)), 12 + 26)
        self.assertEqual(set(ft) | set(it), set(RESOURCE_MILESTONE_LOCATIONS))
        for faction, names in (("Folktails", ft), ("IronTeeth", it)):
            for name in names:
                with self.subTest(faction=faction, milestone=name):
                    good = _good_of(name)
                    self.assertIn(_RESOURCE_GOOD_IDS[good], FACTION_GOODS[faction])
                    self.assertIn(good, RESOURCE_CHAINS[faction])

    def test_every_chain_blueprint_is_progression(self):
        required = set()
        for faction in ("Folktails", "IronTeeth"):
            for name in get_resource_milestones(faction):
                good, threshold = parse_resource_milestone(name)
                required.update(resource_chain_blueprints(good, threshold, faction))
        self.assertTrue(PROMOTED <= required)
        for building in sorted(required):
            with self.subTest(building=building):
                self.assertIn(f"Blueprint: {building}", PROGRESSION_BLUEPRINTS)


class TestPackageAmounts(unittest.TestCase):
    def test_scale_rounds_half_up_with_minimum_one(self):
        cases = [(100, 100, 100), (50, 100, 50), (15, 10, 2), (25, 10, 3), (10, 10, 1),
                 (1, 10, 1), (45, 150, 68), (60, 1000, 600), (20, 100, 20), (10, 33, 3)]
        for base, percent, expected in cases:
            with self.subTest(base=base, percent=percent):
                self.assertEqual(scale_package_amount(base, percent), expected)

    def test_package_goods_belong_to_faction(self):
        for faction in ("Folktails", "IronTeeth"):
            weights = get_resource_package_weights(faction)
            self.assertEqual(sum(weights.values()), 56)
            goods = {good for name, good, *_ in RESOURCE_PACKAGES if name in weights}
            self.assertTrue(goods <= FACTION_GOODS[faction], goods - FACTION_GOODS[faction])
            self.assertFalse(goods & EXCLUDED_PACKAGE_GOODS)


class ResourcePoolChecks:
    faction = "Folktails"
    expected_locations = 211

    def test_location_count(self):
        located = [loc for loc in self.multiworld.get_locations(self.player) if loc.address]
        self.assertEqual(len(located), self.expected_locations)
        self.assertEqual(len(self.multiworld.itempool), self.expected_locations)

    def test_pool_uses_faction_packages_only(self):
        weights = get_resource_package_weights(self.faction)
        names = [item.name for item in self.multiworld.itempool]
        self.assertFalse(LEGACY_FILLER & set(names))
        packages = [n for n in names if n.startswith("Package: ")]
        self.assertTrue(packages)
        self.assertTrue(set(packages) <= set(weights))
        # Traps, boosts, scouts and skips are unchanged: every milestone
        # beyond the 23 fixed extras carries a package, plus one package for
        # each of the three starting blueprints taken out of the pool.
        self.assertEqual(len(packages), 61 + 18 - 23 + 3)

    def test_slot_data_packages_and_milestones(self):
        slot_data = self.world.fill_slot_data()
        self.assertEqual(slot_data["resource_package_percent"], 100)
        self.assertEqual(slot_data["resource_milestone_set"], 2)
        packages = slot_data["resource_packages"]
        self.assertEqual(set(packages), set(get_resource_package_weights(self.faction)))
        for name, good, base, *_ in RESOURCE_PACKAGES:
            if name in packages:
                self.assertEqual(packages[name], {"good_id": good, "amount": base})
        resource = [m for m in slot_data["milestones"] if m["type"] == "resource"]
        self.assertEqual(len(resource), 61)
        for m in resource:
            self.assertIn(m["good_id"], FACTION_GOODS[self.faction], m["name"])

    def test_each_chain_blueprint_gates_its_milestones(self):
        milestones = [n for n in self.world.active_milestones if n.startswith("Resource:")]
        chains = {n: resource_chain_blueprints(*parse_resource_milestone(n), self.faction)
                  for n in milestones}
        starting = {item.name for item in self.multiworld.precollected_items[self.player]}
        for blueprint in sorted({b for req in chains.values() for b in req}
                                - {s.removeprefix("Blueprint: ") for s in starting}):
            state = CollectionState(self.multiworld)
            for item in self.multiworld.itempool:
                if item.name != f"Blueprint: {blueprint}":
                    state.collect(item, True)
            for name, required in chains.items():
                with self.subTest(blueprint=blueprint, milestone=name):
                    reachable = self.multiworld.get_location(name, self.player).can_reach(state)
                    self.assertEqual(reachable, blueprint not in required)
        self.assertIn("Blueprint: Forester", starting)

    def test_free_chains_reachable_with_nothing(self):
        state = CollectionState(self.multiworld)
        free = [n for n in self.world.active_milestones if n.startswith("Resource:")
                and not resource_chain_blueprints(*parse_resource_milestone(n), self.faction)]
        self.assertTrue(free)
        for name in free:
            self.assertTrue(self.multiworld.get_location(name, self.player).can_reach(state), name)


class TestFolktailsResourcePool(ResourcePoolChecks, TimberbornTestBase):
    options = {"faction": 0}

    def test_chain_details(self):
        self.assertEqual(set(resource_chain_blueprints("Treated Planks", 10, "Folktails")),
                         {"Tapper's Shack", "Wood Workshop", "Gear Workshop", "Forester"})
        self.assertEqual(resource_chain_blueprints("Scrap Metal", 250, "Folktails"),
                         ("Scavenger Flag",))
        self.assertIn("Medium Tank", resource_chain_blueprints("Water", 250, "Folktails"))
        self.assertEqual(resource_chain_blueprints("Water", 100, "Folktails"), ())
        self.assertTrue({"Gristmill", "Bakery"} <= set(
            resource_chain_blueprints("Bread", 500, "Folktails")))


class TestIronTeethResourcePool(ResourcePoolChecks, TimberbornTestBase):
    options = {"faction": 1}
    faction = "IronTeeth"
    expected_locations = 210

    def test_bread_is_not_placed(self):
        names = {loc.name for loc in self.multiworld.get_locations(self.player)}
        self.assertNotIn("Resource: Reach 500 Bread", names)
        self.assertIn("Resource: Reach 500 Corn Rations", names)

    def test_chain_details(self):
        grease = set(resource_chain_blueprints("Grease", 10, "IronTeeth"))
        self.assertTrue({"Grease Factory", "Centrifuge", "Metalsmith", "Oil Press",
                         "Deep Badwater Pump", "Wood Workshop", "Smelter"} <= grease)
        self.assertNotIn("Bot Assembler", grease)
        self.assertEqual(resource_chain_blueprints("Scrap Metal", 100, "IronTeeth"), ())
        self.assertEqual(set(resource_chain_blueprints("Fermented Soybean", 50, "IronTeeth")),
                         {"Metalsmith", "Oil Press"})


class TestLiteSet(TimberbornTestBase):
    options = {"faction": 1, "resource_milestone_set": 1}

    def test_lite_counts(self):
        resource = [n for n in self.world.active_milestones if n.startswith("Resource:")]
        self.assertEqual(len(resource), 31)
        self.assertEqual(len(self.multiworld.itempool),
                         len(self.multiworld.get_unfilled_locations(self.player)))


class TestClassicSet(TimberbornTestBase):
    options = {"faction": 0, "resource_milestone_set": 0}

    def test_classic_is_original_thirteen(self):
        resource = [n for n in self.world.active_milestones if n.startswith("Resource:")]
        self.assertEqual(resource, RESOURCE_MILESTONE_LOCATIONS[:13])


class TestPackageSizeOption(TimberbornTestBase):
    options = {"faction": 0, "resource_package_size": 250}

    def test_slot_data_amounts_scaled(self):
        slot_data = self.world.fill_slot_data()
        self.assertEqual(slot_data["resource_package_percent"], 250)
        packages = slot_data["resource_packages"]
        self.assertEqual(packages["Package: Logs"], {"good_id": "Log", "amount": 250})
        self.assertEqual(packages["Package: Metal Blocks"]["amount"], 38)  # 37.5 rounds up
        self.assertEqual(packages["Package: Grilled Spadderdock"]["amount"], 113)  # 112.5


class TestMinimumPackageSize(TimberbornTestBase):
    options = {"faction": 1, "resource_package_size": 10}

    def test_every_amount_at_least_one(self):
        packages = self.world.fill_slot_data()["resource_packages"]
        self.assertEqual(packages["Package: Grease"]["amount"], 1)
        self.assertTrue(all(p["amount"] >= 1 for p in packages.values()))


class TestWaterCapWithWaterGoal(TimberbornTestBase):
    options = {"faction": 0, "goal_selection": {"Water Storage"}, "resource_package_size": 1000}

    def test_no_water_package_reaches_the_goal(self):
        names = [item.name for item in self.multiworld.itempool]
        self.assertNotIn("Package: Water", names)
        self.assertNotEqual(self.world.get_filler_item_name(), "Package: Water")


class TestWaterTotalUnderGoal(TimberbornTestBase):
    options = {"faction": 1, "goal_selection": {"Water Storage"}, "resource_package_size": 200}

    def test_total_water_under_500(self):
        water = sum(1 for item in self.multiworld.itempool if item.name == "Package: Water")
        for _ in range(50):
            if self.world.get_filler_item_name() == "Package: Water":
                water += 1
        self.assertLess(water * self.world.resource_package_amount("Package: Water"), 500)
