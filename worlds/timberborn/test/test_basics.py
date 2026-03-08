from . import TimberbornTestBase
from ..Items import BLUEPRINT_ITEMS, item_name_to_id, ALL_FT_BLUEPRINTS
from ..Locations import (ALL_SCIENCE_LOCATIONS, ALL_MILESTONE_LOCATIONS,
                         location_name_to_id)


class TestDefaultGeneration(TimberbornTestBase):
    """Default options should produce a valid world."""

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
