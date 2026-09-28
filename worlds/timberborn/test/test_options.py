import unittest
from collections import Counter

from test.general import setup_multiworld

from . import TimberbornTestBase
from .. import TimberbornWorld


class TestCompleteWonder(TimberbornTestBase):
    options = {"goal_selection": {"Wonder"}}

    def test_wonder_location_exists(self):
        loc_names = {loc.name for loc in self.multiworld.get_locations(self.player)}
        self.assertIn("Wonder: Complete Earth Recultivator", loc_names)


class TestReachPopulation(TimberbornTestBase):
    options = {"goal_selection": {"Population"}, "population_goal": 50}

    def test_slot_data_goal(self):
        slot_data = self.world.fill_slot_data()
        self.assertIn("Population", slot_data["goals"])
        self.assertEqual(slot_data["population_goal"], 50)


class TestSurviveCycles(TimberbornTestBase):
    options = {"goal_selection": {"Droughts"}, "drought_cycles_goal": 10}

    def test_slot_data_goal(self):
        slot_data = self.world.fill_slot_data()
        self.assertIn("Droughts", slot_data["goals"])
        self.assertEqual(slot_data["drought_cycles_goal"], 10)


class TestIncludeTraps(TimberbornTestBase):
    options = {"include_traps": 1}

    def test_traps_in_pool(self):
        trap_names = {item.name for item in self.multiworld.itempool
                      if "Trap:" in item.name}
        self.assertGreater(len(trap_names), 0, "No trap items found with traps enabled")


class TestNoTraps(TimberbornTestBase):
    options = {"include_traps": 0}

    def test_no_traps_in_pool(self):
        trap_items = [item for item in self.multiworld.itempool
                      if "Trap:" in item.name]
        self.assertEqual(len(trap_items), 0,
                         f"Found {len(trap_items)} trap items with traps disabled")


TRAP_NAMES = {"Trap: Hazardous Weather", "Trap: Hungry Beavers", "Trap: Thirsty Beavers"}


def _trap_items(test):
    return [item.name for item in test.multiworld.itempool
            if item.player == test.player and "Trap:" in item.name]


class TestDefaultTrapWeights(TimberbornTestBase):
    def test_default_weights(self):
        options = self.world.options
        self.assertEqual((options.hazardous_weather_trap_weight.value,
                          options.hungry_beavers_trap_weight.value,
                          options.thirsty_beavers_trap_weight.value), (50, 30, 20))

    def test_default_mix_only_has_the_three_traps(self):
        traps = _trap_items(self)
        self.assertEqual(len(traps), 10)
        self.assertLessEqual(set(traps), TRAP_NAMES)


class TestDefaultTrapCountIronTeeth(TimberbornTestBase):
    options = {"faction": "iron_teeth"}

    def test_default_trap_count(self):
        traps = _trap_items(self)
        self.assertEqual(len(traps), 10)
        self.assertLessEqual(set(traps), TRAP_NAMES)


class TestTrapPercentageZero(TimberbornTestBase):
    options = {"trap_percentage": 0}

    def test_no_traps(self):
        self.assertEqual(_trap_items(self), [])
        self.assertEqual(len(self.multiworld.itempool),
                         len(self.multiworld.get_unfilled_locations(self.player)))


class TestTrapPercentageHundred(TimberbornTestBase):
    """Every filler slot is a trap; the inherited fill tests show the seed still generates."""
    options = {"trap_percentage": 100}

    def test_all_filler_slots_are_traps(self):
        names = [item.name for item in self.multiworld.itempool if item.player == self.player]
        self.assertFalse([name for name in names if name.startswith("Package:")])
        self.assertEqual(len(_trap_items(self)), 69)
        self.assertEqual(names.count("Skip"), 3)


class TestTrapPercentageWithWeights(TimberbornTestBase):
    options = {"trap_percentage": 50, "hazardous_weather_trap_weight": 0,
               "thirsty_beavers_trap_weight": 0}

    def test_count_and_mix(self):
        # 50% of 69 filler slots is 34.5, rounded half up to 35.
        self.assertEqual(_trap_items(self), ["Trap: Hungry Beavers"] * 35)


class TestNoWeatherTraps(TimberbornTestBase):
    options = {"hazardous_weather_trap_weight": 0}

    def test_no_weather_traps(self):
        traps = _trap_items(self)
        self.assertEqual(len(traps), 10)
        self.assertNotIn("Trap: Hazardous Weather", traps)
        self.assertEqual(set(traps) - {"Trap: Hungry Beavers", "Trap: Thirsty Beavers"}, set())


class TestOnlyWeatherTraps(TimberbornTestBase):
    options = {"hungry_beavers_trap_weight": 0, "thirsty_beavers_trap_weight": 0}

    def test_only_weather_traps(self):
        self.assertEqual(_trap_items(self), ["Trap: Hazardous Weather"] * 10)


class TestAllTrapWeightsZero(TimberbornTestBase):
    options = {"hazardous_weather_trap_weight": 0, "hungry_beavers_trap_weight": 0,
               "thirsty_beavers_trap_weight": 0}

    def test_no_traps_and_full_pool(self):
        self.assertEqual(_trap_items(self), [])
        self.assertEqual(len(self.multiworld.itempool),
                         len(self.multiworld.get_unfilled_locations(self.player)))


class TestTrapWeightsZeroMatchesTrapsOff(unittest.TestCase):
    """All weights 0 and trap_percentage 0 fill the pool exactly like include_traps off."""

    def test_same_pool_as_traps_off(self):
        def pool(options):
            mw = setup_multiworld(TimberbornWorld, seed=4242, options=options)
            return sorted(item.name for item in mw.itempool if item.player == 1)

        off = pool({"include_traps": 0})
        self.assertFalse([name for name in off if "Trap:" in name])
        for options in ({"hazardous_weather_trap_weight": 0, "hungry_beavers_trap_weight": 0,
                         "thirsty_beavers_trap_weight": 0},
                        {"trap_percentage": 0}):
            with self.subTest(options=options):
                self.assertEqual(pool(options), off)


class TestTrapDrawDeterminism(unittest.TestCase):
    """The same seed and options give the same traps; the weights shape the mix."""

    @staticmethod
    def _traps(seed, options=None):
        mw = setup_multiworld(TimberbornWorld, seed=seed, options=options or {})
        return [item.name for item in mw.itempool if item.player == 1 and "Trap:" in item.name]

    def test_same_seed_same_traps(self):
        options = {"hazardous_weather_trap_weight": 10, "hungry_beavers_trap_weight": 70}
        self.assertEqual(self._traps(31337, options), self._traps(31337, options))

    def test_weights_shape_the_mix(self):
        counts = Counter()
        for seed in range(20):
            counts.update(self._traps(5000 + seed))
        # 200 draws at 50/30/20: the order holds with a wide margin.
        self.assertGreater(counts["Trap: Hazardous Weather"], counts["Trap: Hungry Beavers"])
        self.assertGreater(counts["Trap: Hungry Beavers"], counts["Trap: Thirsty Beavers"])
        self.assertGreater(counts["Trap: Thirsty Beavers"], 0)


class TestShopLayout(TimberbornTestBase):
    """Default generation always produces a branching shop layout."""

    def test_slot_data_has_shop_layout(self):
        slot_data = self.world.fill_slot_data()
        self.assertIn("shop_layout", slot_data)

    def test_shop_region_exists(self):
        region_names = {r.name for r in self.multiworld.regions}
        self.assertIn("Shop", region_names)

    def test_skip_count_in_slot_data(self):
        slot_data = self.world.fill_slot_data()
        self.assertIn("skip_count", slot_data)
        self.assertEqual(slot_data["skip_count"], 3)  # default


class TestMaxScienceCost(TimberbornTestBase):
    options = {"max_science_cost": 10000}

    def test_max_price_matches_option(self):
        max_price = max(e["price"] for e in self.world.shop_layout)
        self.assertEqual(max_price, 10000)


class TestGoodsDeliveryDefault(TimberbornTestBase):
    """goods_delivery defaults to the District Center (0) in slot_data."""

    def test_default_is_district_center(self):
        from ..Options import GoodsDelivery
        # The client (GoodsDeliveryOption.cs) reads 0 as district_center and 1 as storage.
        self.assertEqual(GoodsDelivery.option_district_center, 0)
        self.assertEqual(GoodsDelivery.option_storage, 1)
        self.assertEqual(self.world.fill_slot_data()["goods_delivery"], 0)


class TestGoodsDeliveryStorage(TimberbornTestBase):
    options = {"goods_delivery": "storage"}

    def test_storage_in_slot_data(self):
        self.assertEqual(self.world.fill_slot_data()["goods_delivery"], 1)
