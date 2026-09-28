"""Universal Tracker: a re-generation from slot_data alone rebuilds the seed's logic."""
import random
import unittest

from BaseClasses import CollectionState
from test.general import gen_steps, setup_multiworld
from worlds.AutoWorld import call_all

from .. import TimberbornWorld

CASES = [
    {"faction": 0},
    {"faction": 1, "progressive_items": 1, "goal_selection": ["Badtides", "Population"],
     "badtide_cycles_goal": 12, "population_goal": 150},
    {"faction": 0, "progressive_items": 1, "starting_blueprints": 0, "resource_milestone_set": 0,
     "goal_selection": ["Droughts", "Water Storage"], "drought_cycles_goal": 20,
     "include_population_milestones": 0, "max_science_cost": 9000},
    {"faction": 1, "progressive_items": 0, "randomization_style": 1, "goal_selection": ["Wonder"],
     "include_wellbeing_milestones": 0},
]


def _regenerate(slot_data: dict, seed: int):
    """What UT does: default options (no YAML) plus the slot_data as passthrough."""
    mw = setup_multiworld(TimberbornWorld, steps=(), seed=seed)
    mw.re_gen_passthrough = {"Timberborn": slot_data}
    for step in gen_steps:
        call_all(mw, step)
    return mw


def _state(mw, names):
    world = mw.worlds[1]
    state = CollectionState(mw)
    for name in names:
        state.collect(world.create_item(name), True)
    state.sweep_for_advancements()  # shop path events and goal events
    return state


class TestUniversalTrackerRegeneration(unittest.TestCase):
    def test_regeneration_matches_seed(self):
        for index, options in enumerate(CASES):
            with self.subTest(case=index):
                source = setup_multiworld(TimberbornWorld, seed=1000 + index, options=options)
                slot_data = source.worlds[1].fill_slot_data()
                # A different seed for the re-generation: nothing may depend on re-rolling.
                tracked = _regenerate(slot_data, seed=77 + index)
                a, b = source.worlds[1], tracked.worlds[1]
                self.assertEqual(a.faction, b.faction)
                self.assertEqual(a.shop_layout and [(e["location_name"], e["building_name"], e["tier"])
                                                    for e in a.shop_layout],
                                 [(e["location_name"], e["building_name"], e["tier"]) for e in b.shop_layout])
                self.assertEqual(a._progressive_chains, b._progressive_chains)
                self.assertEqual(a.resolved_goals, b.resolved_goals)
                self.assertEqual(a.starting_items, b.starting_items)
                locations_a = {loc.name for loc in source.get_locations(1)}
                locations_b = {loc.name for loc in tracked.get_locations(1)}
                self.assertEqual(locations_a, locations_b)
                self.assertEqual({r.name for r in source.get_regions(1)},
                                 {r.name for r in tracked.get_regions(1)})

                progression = sorted({item.name for item in source.itempool
                                      if item.player == 1 and item.advancement})
                rng = random.Random(index)
                samples = [[], progression] + [rng.sample(progression, rng.randrange(len(progression)))
                                               for _ in range(12)]
                for names in samples:
                    state_a, state_b = _state(source, names), _state(tracked, names)
                    for name in sorted(locations_a):
                        self.assertEqual(source.get_location(name, 1).can_reach(state_a),
                                         tracked.get_location(name, 1).can_reach(state_b),
                                         f"{name} with {len(names)} items")
                    self.assertEqual(source.can_beat_game(state_a), tracked.can_beat_game(state_b))

    def test_slot_data_from_before_logic_difficulty_removal(self):
        """Seeds generated before the removal carry logic_difficulty; UT ignores it."""
        source = setup_multiworld(TimberbornWorld, seed=2000, options={"faction": 1})
        slot_data = dict(source.worlds[1].fill_slot_data())
        self.assertNotIn("logic_difficulty", slot_data)
        for old_value in (0, 1):
            with self.subTest(logic_difficulty=old_value):
                tracked = _regenerate({**slot_data, "logic_difficulty": old_value}, seed=88)
                self.assertEqual({loc.name for loc in source.get_locations(1)},
                                 {loc.name for loc in tracked.get_locations(1)})
                self.assertEqual(tracked.worlds[1].faction, "IronTeeth")

    def test_interpret_slot_data_passes_slot_data_through(self):
        data = {"faction": "Folktails", "ut_version": 1}
        self.assertIs(TimberbornWorld.interpret_slot_data(data), data)
        self.assertTrue(TimberbornWorld.ut_can_gen_without_yaml)
