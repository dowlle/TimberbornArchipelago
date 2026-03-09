from . import TimberbornTestBase
from ..Items import BLUEPRINT_ITEMS, item_name_to_id, ALL_FT_BLUEPRINTS
from ..Locations import (ALL_SCIENCE_LOCATIONS, ALL_MILESTONE_LOCATIONS,
                         location_name_to_id)
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
        self.assertEqual(len(ALL_FT_BLUEPRINTS), 125, "Expected 125 Folktails blueprints")

    def test_all_science_locations_created(self):
        loc_names = {loc.name for loc in self.multiworld.get_locations(self.player)}
        for sci_loc in ALL_SCIENCE_LOCATIONS:
            self.assertIn(sci_loc, loc_names, f"Missing science location: {sci_loc}")

    def test_all_milestone_locations_created(self):
        loc_names = {loc.name for loc in self.multiworld.get_locations(self.player)}
        for ms_loc in ALL_MILESTONE_LOCATIONS:
            self.assertIn(ms_loc, loc_names, f"Missing milestone location: {ms_loc}")

    def test_total_location_count(self):
        self.assertEqual(len(ALL_SCIENCE_LOCATIONS), 125)
        self.assertEqual(len(ALL_MILESTONE_LOCATIONS), 16)
        total = len(location_name_to_id)
        self.assertEqual(total, 141, f"Expected 141 total locations, got {total}")

    def test_no_duplicate_item_ids(self):
        ids = list(item_name_to_id.values())
        self.assertEqual(len(ids), len(set(ids)), "Duplicate item IDs found")

    def test_no_duplicate_location_ids(self):
        ids = list(location_name_to_id.values())
        self.assertEqual(len(ids), len(set(ids)), "Duplicate location IDs found")

    def test_item_location_name_correspondence(self):
        """Every blueprint item 'Blueprint: X' should have a matching 'Science: X' location."""
        for bp_name in BLUEPRINT_ITEMS:
            building = bp_name.replace("Blueprint: ", "")
            sci_name = f"Science: {building}"
            self.assertIn(sci_name, location_name_to_id,
                          f"Blueprint '{bp_name}' has no matching science location")


class TestBranchingGeneration(TimberbornTestBase):
    """Branching shop should produce valid layout."""
    options = {"skip_count": 3}

    def test_shop_layout_exists(self):
        self.assertIsNotNone(self.world.shop_layout)
        self.assertEqual(len(self.world.shop_layout), 125)

    def test_shop_layout_in_slot_data(self):
        slot_data = self.world.fill_slot_data()
        self.assertIn("shop_layout", slot_data)
        self.assertEqual(len(slot_data["shop_layout"]), 125)

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

    def test_slot_data_no_location_names(self):
        """slot_data shop_layout should NOT contain location names (abstract paths only)."""
        slot_data = self.world.fill_slot_data()
        for entry in slot_data["shop_layout"]:
            self.assertNotIn("location_name", entry)
            self.assertIn("location_id", entry)
            self.assertIn("path", entry)
            self.assertIn("level", entry)
            self.assertIn("price", entry)
            self.assertIn("tier", entry)


class TestSkipCountZero(TimberbornTestBase):
    options = {"skip_count": 0}

    def test_no_skip_items(self):
        skip_items = [i for i in self.multiworld.itempool if i.name == "Skip"]
        self.assertEqual(len(skip_items), 0)
