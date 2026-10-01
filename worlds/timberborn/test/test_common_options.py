"""Common Archipelago options run through the real generator: excluded and priority
shop slots, and start_inventory_from_pool."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

import Generate
import Main
from BaseClasses import CollectionState, LocationProgressType

# Shop slots of tier 2 and higher on every path, last levels first. Names past a
# path's end are ignored by the generator.
LATE_SLOTS = [f"Shop: {path}-{level:02d}" for level in range(30, 14, -1) for path in "ABCD"]


def _yaml(name: str, game: str, options: dict) -> str:
    import yaml
    return yaml.safe_dump({"name": name, "game": game, game: options}, sort_keys=False)


class GeneratorTestBase(unittest.TestCase):
    """Runs Generate.main and Main.main without output on YAMLs written to a temp folder."""

    def generate(self, players: list[tuple[str, str, dict]], seed: int):
        with tempfile.TemporaryDirectory(prefix="tb_players_") as players_dir, \
                tempfile.TemporaryDirectory(prefix="tb_out_") as out_dir:
            for index, (name, game, options) in enumerate(players):
                Path(players_dir, f"{index}.yaml").write_text(_yaml(name, game, options))
            argv = sys.argv
            sys.argv = [argv[0], "--seed", str(seed), "--player_files_path", players_dir,
                        "--outputpath", out_dir, "--skip_output", "--spoiler", "0"]
            try:
                multiworld = Main.main(*Generate.main())
            finally:
                sys.argv = argv
        self.assertEqual([], [loc for loc in multiworld.get_locations() if loc.item is None])
        self.assertTrue(multiworld.fulfills_accessibility())
        return multiworld


class TestExcludedShopSlots(GeneratorTestBase):
    """Excluded tier 2+ shop slots used to refuse every filler item while useful
    blueprints were still unplaced, so generation failed with a FillError."""

    def test_one_excluded_slot_with_another_game(self):
        for seed in (1, 2, 3):
            with self.subTest(seed=seed):
                mw = self.generate([("TB", "Timberborn", {"exclude_locations": ["Shop: A-23"]}),
                                    ("HK", "Hollow Knight", {})], seed)
                location = mw.get_location("Shop: A-23", 1)
                self.assertEqual(location.progress_type, LocationProgressType.EXCLUDED)
                self.assertFalse(location.item.advancement or location.item.useful)

    def test_many_excluded_slots_both_factions(self):
        for faction in (0, 1):
            with self.subTest(faction=faction):
                self.generate([("TB", "Timberborn", {"faction": faction,
                                                     "exclude_locations": LATE_SLOTS[:12]}),
                               ("CF", "ChecksFinder", {})], 20261001)

    def test_excluded_slots_solo(self):
        self.generate([("TB", "Timberborn", {"exclude_locations": LATE_SLOTS[:8]})], 20261001)


class TestPriorityShopSlots(GeneratorTestBase):
    """Priority on late shop slots used to fail the priority fill in solo rooms."""

    def test_late_priority_solo(self):
        slots = [f"Shop: {path}-{level:02d}" for path in "ABCD" for level in range(20, 26)]
        mw = self.generate([("TB", "Timberborn", {"priority_locations": slots})], 20261001)
        for name in slots:
            self.assertTrue(mw.get_location(name, 1).item.advancement, name)


class TestStartInventoryFromPool(GeneratorTestBase):
    def test_progression_blueprint_moves_to_start(self):
        mw = self.generate([("TB", "Timberborn", {
            "start_inventory_from_pool": {"Blueprint: Smelter": 1, "Progressive Platforms": 1}})],
            20261001)
        start = [item.name for item in mw.precollected_items[1]]
        self.assertIn("Blueprint: Smelter", start)
        self.assertEqual(2, start.count("Progressive Platforms"))  # starting blueprint + pool copy
        placed = [loc.item.name for loc in mw.get_filled_locations(1) if loc.item.player == 1]
        self.assertNotIn("Blueprint: Smelter", placed)
        state = CollectionState(mw)  # starts with the precollected items
        self.assertTrue(state.has("Blueprint: Double Platform", 1))


NO_MILESTONES = {
    "include_population_milestones": False, "include_wellbeing_milestones": False,
    "include_survival_milestones": False, "include_wonder_milestone": False,
    "include_resource_milestones": False, "goal_selection": ["Population"],
}


class TestUsefulBlueprintsStillFit(GeneratorTestBase):
    """Without milestones nearly every item has to go in the shop, so useful
    blueprints depend on the reserved high-tier slots. A few late priority slots
    must still leave them room. (Such a seed has no filler, so it cannot exclude
    anything, and many late priority slots cannot be satisfied at all.)"""

    def test_no_milestones_with_late_priority_slots(self):
        for faction in (0, 1):
            for starting in (False, True):
                with self.subTest(faction=faction, starting_blueprints=starting):
                    self.generate([("TB", "Timberborn", {
                        **NO_MILESTONES, "faction": faction, "starting_blueprints": starting,
                        "priority_locations": LATE_SLOTS[:8]})], 20261001)
