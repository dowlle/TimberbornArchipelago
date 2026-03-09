from . import TimberbornTestBase
from ..Items import BLUEPRINT_ITEMS, item_name_to_id, ALL_FT_BLUEPRINTS
from ..Locations import (ALL_SCIENCE_LOCATIONS, ALL_MILESTONE_LOCATIONS,
                         ALL_BUILDING_NAMES, location_name_to_id,
                         POPULATION_LOCATIONS, WELLBEING_LOCATIONS,
                         SURVIVAL_LOCATIONS, WONDER_LOCATIONS)
from ..ShopLayout import BASE_SCIENCE, NUM_PATHS


class TestDefaultGeneration(TimberbornTestBase):
    """Default options should produce a valid world with branching shop."""

    def test_item_count_matches_location_count(self):
        item_count = len(self.multiworld.itempool)
        location_count = len(self.multiworld.get_unfilled_locations(self.player))
        self.assertEqual(item_count, location_count,
                         f"Item pool ({item_count}) != locations ({location_count})")

    def test_all_blueprint_items_in_pool(self):
        pool_names = {item.name for item in self.multiworld.itempool}
        for bp_name in BLUEPRINT_ITEMS:
            self.assertIn(bp_name, pool_names, f"Missing blueprint item: {bp_name}")

    def test_correct_blueprint_count(self):
        self.assertEqual(len(ALL_FT_BLUEPRINTS), 126, "Expected 126 Folktails blueprints")

    def test_all_shop_locations_created(self):
        """Every shop layout entry should map to a created location."""
        loc_names = {loc.name for loc in self.multiworld.get_locations(self.player)}
        for entry in self.world.shop_layout:
            self.assertIn(entry["location_name"], loc_names,
                          f"Missing shop location: {entry['location_name']}")

    def test_all_milestone_locations_created(self):
        loc_names = {loc.name for loc in self.multiworld.get_locations(self.player)}
        for ms_loc in ALL_MILESTONE_LOCATIONS:
            self.assertIn(ms_loc, loc_names, f"Missing milestone location: {ms_loc}")

    def test_total_location_count(self):
        self.assertEqual(len(ALL_BUILDING_NAMES), 126)
        self.assertEqual(len(ALL_MILESTONE_LOCATIONS), 18)
        # Total pre-allocated shop slots + milestones
        total = len(location_name_to_id)
        expected_slots = 4 * 40  # NUM_PATHS * SLOTS_PER_PATH
        self.assertEqual(total, expected_slots + 18,
                         f"Expected {expected_slots + 18} total location IDs, got {total}")

    def test_no_duplicate_item_ids(self):
        ids = list(item_name_to_id.values())
        self.assertEqual(len(ids), len(set(ids)), "Duplicate item IDs found")

    def test_no_duplicate_location_ids(self):
        ids = list(location_name_to_id.values())
        self.assertEqual(len(ids), len(set(ids)), "Duplicate location IDs found")

    def test_building_to_blueprint_correspondence(self):
        """Every building name should have a matching 'Blueprint: X' item."""
        for building in ALL_BUILDING_NAMES:
            bp_name = f"Blueprint: {building}"
            self.assertIn(bp_name, item_name_to_id,
                          f"Building '{building}' has no matching blueprint item")


class TestBranchingGeneration(TimberbornTestBase):
    """Branching shop should produce valid layout."""
    options = {"skip_count": 3}

    def test_shop_layout_exists(self):
        self.assertIsNotNone(self.world.shop_layout)
        self.assertEqual(len(self.world.shop_layout), 126)

    def test_shop_layout_in_slot_data(self):
        slot_data = self.world.fill_slot_data()
        self.assertIn("shop_layout", slot_data)
        self.assertEqual(len(slot_data["shop_layout"]), 126)

    def test_shop_layout_has_4_paths(self):
        paths = {e["path"] for e in self.world.shop_layout}
        self.assertEqual(paths, {"A", "B", "C", "D"})

    def test_path_sizes(self):
        path_counts = {}
        for e in self.world.shop_layout:
            path_counts[e["path"]] = path_counts.get(e["path"], 0) + 1
        for path, count in path_counts.items():
            self.assertIn(count, [31, 32],
                          f"Path {path} has {count} locations (expected 31-32)")

    def test_prices_monotonically_increasing(self):
        sorted_by_pos = sorted(self.world.shop_layout, key=lambda e: e["global_pos"])
        for i in range(1, len(sorted_by_pos)):
            self.assertGreaterEqual(
                sorted_by_pos[i]["price"], sorted_by_pos[i - 1]["price"],
                f"Price not monotonic at global_pos {sorted_by_pos[i]['global_pos']}"
            )

    def test_prices_in_range(self):
        max_science = self.world.options.max_science_cost.value
        for e in self.world.shop_layout:
            self.assertGreaterEqual(e["price"], BASE_SCIENCE)
            self.assertLessEqual(e["price"], max_science)

    def test_all_tiers_present(self):
        tiers = {e["tier"] for e in self.world.shop_layout}
        self.assertTrue(tiers.issuperset({1, 2}), f"Expected at least tiers 1-2, got {tiers}")

    def test_skip_items_in_pool(self):
        skip_items = [i for i in self.multiworld.itempool if i.name == "Skip"]
        self.assertEqual(len(skip_items), 3)

    def test_slot_data_has_building_names(self):
        """slot_data shop_layout should contain building_name for client display."""
        slot_data = self.world.fill_slot_data()
        for entry in slot_data["shop_layout"]:
            self.assertIn("building_name", entry)
            self.assertIn("location_id", entry)
            self.assertIn("path", entry)
            self.assertIn("level", entry)
            self.assertIn("price", entry)
            self.assertIn("tier", entry)

    def test_location_names_are_shop_format(self):
        """Location names should be in 'Shop: X-NN' format."""
        for entry in self.world.shop_layout:
            loc_name = entry["location_name"]
            self.assertRegex(loc_name, r"^Shop: [A-D]-\d{2}$",
                             f"Location name '{loc_name}' not in Shop format")


class TestSkipCountZero(TimberbornTestBase):
    options = {"skip_count": 0}

    def test_no_skip_items(self):
        skip_items = [i for i in self.multiworld.itempool if i.name == "Skip"]
        self.assertEqual(len(skip_items), 0)


class TestNoPopulationMilestones(TimberbornTestBase):
    options = {"include_population_milestones": 0}

    def test_population_milestones_excluded(self):
        loc_names = {loc.name for loc in self.multiworld.get_locations(self.player)}
        for ms in POPULATION_LOCATIONS:
            self.assertNotIn(ms, loc_names)

    def test_other_milestones_still_present(self):
        loc_names = {loc.name for loc in self.multiworld.get_locations(self.player)}
        for ms in WELLBEING_LOCATIONS + SURVIVAL_LOCATIONS + WONDER_LOCATIONS:
            self.assertIn(ms, loc_names)


class TestNoWellbeingMilestones(TimberbornTestBase):
    options = {"include_wellbeing_milestones": 0}

    def test_wellbeing_milestones_excluded(self):
        loc_names = {loc.name for loc in self.multiworld.get_locations(self.player)}
        for ms in WELLBEING_LOCATIONS:
            self.assertNotIn(ms, loc_names)


class TestNoSurvivalMilestones(TimberbornTestBase):
    options = {"include_survival_milestones": 0}

    def test_survival_milestones_excluded(self):
        loc_names = {loc.name for loc in self.multiworld.get_locations(self.player)}
        for ms in SURVIVAL_LOCATIONS:
            self.assertNotIn(ms, loc_names)


class TestNoWonderMilestone(TimberbornTestBase):
    options = {"include_wonder_milestone": 0, "goal": 1}

    def test_wonder_milestone_excluded(self):
        loc_names = {loc.name for loc in self.multiworld.get_locations(self.player)}
        for ms in WONDER_LOCATIONS:
            self.assertNotIn(ms, loc_names)


class TestWonderForceEnabled(TimberbornTestBase):
    """When goal is complete_wonder (0), Wonder milestone is force-enabled even if toggled off."""
    options = {"include_wonder_milestone": 0, "goal": 0}

    def test_wonder_milestone_present(self):
        loc_names = {loc.name for loc in self.multiworld.get_locations(self.player)}
        self.assertIn("Wonder: Complete Earth Recultivator", loc_names)


class TestAllMilestonesDisabled(TimberbornTestBase):
    options = {
        "include_population_milestones": 0,
        "include_wellbeing_milestones": 0,
        "include_survival_milestones": 0,
        "include_wonder_milestone": 0,
        "goal": 1,
    }

    def test_no_milestones(self):
        loc_names = {loc.name for loc in self.multiworld.get_locations(self.player)}
        for ms in ALL_MILESTONE_LOCATIONS:
            self.assertNotIn(ms, loc_names)

    def test_item_count_still_matches(self):
        item_count = len(self.multiworld.itempool)
        location_count = len(self.multiworld.get_unfilled_locations(self.player))
        self.assertEqual(item_count, location_count)


class TestSlotDataMilestones(TimberbornTestBase):
    def test_milestones_in_slot_data(self):
        slot_data = self.world.fill_slot_data()
        self.assertIn("milestones", slot_data)
        self.assertEqual(len(slot_data["milestones"]), 18)

    def test_milestone_metadata_fields(self):
        slot_data = self.world.fill_slot_data()
        for ms in slot_data["milestones"]:
            self.assertIn("name", ms)
            self.assertIn("location_id", ms)
            self.assertIn("type", ms)
            self.assertIn("threshold", ms)
            self.assertIn(ms["type"], {"population", "wellbeing", "survival", "wonder"})
            self.assertGreater(ms["threshold"], 0)
