import json
from pathlib import Path
import unittest

from . import TimberbornTestBase
from ..Items import get_building_names, item_name_to_id
from ..Locations import SLOTS_PER_PATH


class TestPermanentItemIds(unittest.TestCase):
    def test_every_existing_id_is_preserved(self):
        path = Path(__file__).parent / "fixtures/item_ids_before_1_1.json"
        for name, code in json.loads(path.read_text()).items():
            with self.subTest(item=name):
                self.assertEqual(item_name_to_id[name], code)

    def test_new_ids_are_unique_and_valve_is_not_duplicated(self):
        self.assertEqual(len(item_name_to_id), 236)  # 203 + 33 resource packages
        self.assertEqual(len(set(item_name_to_id.values())), 236)
        self.assertIn("Blueprint: Valve", item_name_to_id)
        self.assertNotIn("Blueprint: Throttling Valve", item_name_to_id)


class TestNewFolktailsBuildings(TimberbornTestBase):
    options = {"faction": 0, "progressive_items": 0}

    def test_new_content_in_pool_and_layout(self):
        expected = {"Airlock", "Impermeable Power Shaft", "Compact Mechanical Pump",
                    "Hall of Abundance", "Sauna", "Domed Garden"}
        self.assertTrue(expected <= set(get_building_names("Folktails")))
        pool = {item.name for item in self.multiworld.itempool}
        self.assertTrue({"Blueprint: " + name for name in expected} <= pool)
        layout = self.world.shop_layout
        self.assertEqual(len(layout), 132)
        self.assertTrue(expected <= {entry["building_name"] for entry in layout})
        self.assertLessEqual(max(entry["slot"] for entry in layout), SLOTS_PER_PATH)
        self.assertFalse({"Arch of Progress", "Massager", "Impermeable Tubeway", "Dance Pit"}
                         & set(get_building_names("Folktails")))


class TestNewFolktailsProgressive(TestNewFolktailsBuildings):
    options = {"faction": 0, "progressive_items": 2}


class TestNewIronTeethBuildings(TimberbornTestBase):
    options = {"faction": 1, "progressive_items": 0}

    def test_new_content_in_pool_and_layout(self):
        expected = {"Airlock", "Impermeable Power Shaft", "Compact Mechanical Pump",
                    "Arch of Progress", "Massager", "Impermeable Tubeway", "Dance Pit"}
        pool = {item.name for item in self.multiworld.itempool}
        self.assertTrue({"Blueprint: " + name for name in expected} <= pool)
        self.assertEqual(len(self.world.shop_layout), 131)
        self.assertTrue(expected <= {e["building_name"] for e in self.world.shop_layout})
        self.assertLessEqual(max(e["slot"] for e in self.world.shop_layout), SLOTS_PER_PATH)
        self.assertFalse({"Hall of Abundance", "Sauna", "Domed Garden"}
                         & set(get_building_names("IronTeeth")))

    def test_dance_pit_and_its_event_require_metalsmith(self):
        self.collect_all_but("Blueprint: Metalsmith")
        entry = next(e for e in self.world.shop_layout if e["building_name"] == "Dance Pit")
        location = self.multiworld.get_location(entry["location_name"], self.player)
        self.assertFalse(location.access_rule(self.multiworld.state))
        event = next((loc for loc in self.multiworld.get_locations(self.player)
                      if loc.name == "Event: " + entry["location_name"] + " Checked"), None)
        if event:
            self.assertFalse(event.access_rule(self.multiworld.state))
        item = self.world.create_item("Blueprint: Metalsmith")
        self.assertTrue(item.advancement, "Metalsmith must participate in logical reachability")
        self.collect(item)
        self.assertTrue(self.can_reach_location(entry["location_name"]))
        if event:
            self.assertTrue(event.access_rule(self.multiworld.state))


class TestNewIronTeethProgressive(TestNewIronTeethBuildings):
    options = {"faction": 1, "progressive_items": 2}
