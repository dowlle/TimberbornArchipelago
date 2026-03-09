from . import TimberbornTestBase


class TestCompleteWonder(TimberbornTestBase):
    options = {"goal": 0}

    def test_wonder_location_exists(self):
        loc_names = {loc.name for loc in self.multiworld.get_locations(self.player)}
        self.assertIn("Wonder: Complete Earth Recultivator", loc_names)


class TestReachPopulation(TimberbornTestBase):
    options = {"goal": 1, "population_goal": 50}

    def test_slot_data_goal(self):
        slot_data = self.world.fill_slot_data()
        self.assertEqual(slot_data["goal"], 1)
        self.assertEqual(slot_data["population_goal"], 50)


class TestSurviveCycles(TimberbornTestBase):
    options = {"goal": 2, "survival_cycles_goal": 10}

    def test_slot_data_goal(self):
        slot_data = self.world.fill_slot_data()
        self.assertEqual(slot_data["goal"], 2)
        self.assertEqual(slot_data["survival_cycles_goal"], 10)


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


class TestShopStyleFlat(TimberbornTestBase):
    options = {"shop_style": 0}

    def test_slot_data_shop_style(self):
        slot_data = self.world.fill_slot_data()
        self.assertEqual(slot_data["shop_style"], 0)
        self.assertNotIn("shop_layout", slot_data)

    def test_no_shop_region(self):
        region_names = {r.name for r in self.multiworld.regions}
        self.assertNotIn("Shop", region_names)


class TestShopStyleBranching(TimberbornTestBase):
    options = {"shop_style": 1}

    def test_slot_data_shop_style(self):
        slot_data = self.world.fill_slot_data()
        self.assertEqual(slot_data["shop_style"], 1)
        self.assertIn("shop_layout", slot_data)

    def test_shop_region_exists(self):
        region_names = {r.name for r in self.multiworld.regions}
        self.assertIn("Shop", region_names)

    def test_skip_count_in_slot_data(self):
        slot_data = self.world.fill_slot_data()
        self.assertIn("skip_count", slot_data)
        self.assertEqual(slot_data["skip_count"], 3)  # default


class TestMaxScienceCost(TimberbornTestBase):
    options = {"shop_style": 1, "max_science_cost": 10000}

    def test_max_price_matches_option(self):
        max_price = max(e["price"] for e in self.world.shop_layout)
        self.assertEqual(max_price, 10000)
