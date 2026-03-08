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
