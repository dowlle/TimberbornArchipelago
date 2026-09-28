"""Goals and badtide survival decisions (review 2026-09-27, decisions 2026-09-28)."""
from BaseClasses import CollectionState, ItemClassification

from . import TimberbornTestBase
from ..Items import item_table, get_building_names
from ..Rules import (survival_blueprints, survival_groups, drought_level, badtide_level,
                     SURVIVAL_EARLY, SURVIVAL_MID, SURVIVAL_LATE, tier_blueprints)


def _fresh_all_but(test, names):
    test.multiworld.state = CollectionState(test.multiworld)
    test.collect_all_but(names)


class TestSurvivalTables(TimberbornTestBase):
    options = {"faction": 0}

    def test_every_survival_blueprint_is_progression(self):
        for faction in ("Folktails", "IronTeeth"):
            buildings = set(get_building_names(faction))
            for name in survival_blueprints(faction):
                with self.subTest(faction=faction, building=name):
                    self.assertIn(name, buildings)
                    self.assertEqual(item_table[f"Blueprint: {name}"]["classification"],
                                     ItemClassification.progression)

    def test_levels(self):
        self.assertEqual([drought_level(n) for n in (1, 5, 6, 15, 16, 40)],
                         [SURVIVAL_EARLY, SURVIVAL_EARLY, SURVIVAL_MID, SURVIVAL_MID,
                          SURVIVAL_LATE, SURVIVAL_LATE])
        self.assertEqual([badtide_level(n) for n in (1, 3, 4, 10, 11, 20)],
                         [SURVIVAL_EARLY, SURVIVAL_EARLY, SURVIVAL_MID, SURVIVAL_MID,
                          SURVIVAL_LATE, SURVIVAL_LATE])

    def test_cure_is_mid_badtide(self):
        early = {b for g in survival_groups("badtide", SURVIVAL_EARLY, "Folktails") for b in g}
        mid = {b for g in survival_groups("badtide", SURVIVAL_MID, "Folktails") for b in g}
        self.assertNotIn("Herbalist", early)
        self.assertTrue({"Herbalist", "Paper Mill", "Floodgate"} <= mid)
        it_mid = {b for g in survival_groups("badtide", SURVIVAL_MID, "IronTeeth") for b in g}
        self.assertIn("Decontamination Pod", it_mid)

    def test_folktails_bots_need_refinery(self):
        self.assertIn("Refinery", tier_blueprints(5, "Folktails"))
        self.assertNotIn("Refinery", tier_blueprints(5, "IronTeeth"))


class TestSurvivalMilestones(TimberbornTestBase):
    """Survival predicates gate survival milestones; floodgates are essential for badtides."""
    options = {"faction": 0, "progressive_items": 0,
               "include_survival_milestones": 1}

    def test_first_badtide_needs_floodgate_and_medium_tank(self):
        for missing in ("Blueprint: Floodgate", "Blueprint: Medium Tank", "Blueprint: Levee"):
            _fresh_all_but(self, [missing])
            self.assertFalse(self.can_reach_location("Survival: Survive 1st Badtide"), missing)
        _fresh_all_but(self, [])
        self.assertTrue(self.can_reach_location("Survival: Survive 1st Badtide"))

    def test_five_badtides_need_the_cure(self):
        _fresh_all_but(self, ["Blueprint: Herbalist"])
        self.assertFalse(self.can_reach_location("Survival: Survive 5 Badtides"))
        self.assertTrue(self.can_reach_location("Survival: Survive 1st Badtide"))

    def test_ten_badtides_need_a_mechanical_pump(self):
        _fresh_all_but(self, ["Blueprint: Mechanical Fluid Pump", "Blueprint: Compact Mechanical Pump"])
        self.assertFalse(self.can_reach_location("Survival: Survive 10 Badtides"))
        _fresh_all_but(self, ["Blueprint: Mechanical Fluid Pump"])
        self.assertTrue(self.can_reach_location("Survival: Survive 10 Badtides"))

    def test_drought_milestones_step_up(self):
        _fresh_all_but(self, ["Blueprint: Double Floodgate"])
        self.assertFalse(self.can_reach_location("Survival: Survive 5 Droughts"))
        self.assertTrue(self.can_reach_location("Survival: Survive 1st Drought"))
        _fresh_all_but(self, ["Blueprint: Large Tank", "Blueprint: Triple Floodgate"])
        self.assertFalse(self.can_reach_location("Survival: Survive 10 Droughts"))
        self.assertTrue(self.can_reach_location("Survival: Survive 5 Droughts"))


class TestIronTeethCureNeedsExtract(TimberbornTestBase):
    """The Decontamination Pod consumes Extract, so mid badtides need its chain."""
    options = {"faction": 1, "progressive_items": 0, "include_survival_milestones": 1}

    def test_five_badtides_need_deep_badwater_pump(self):
        _fresh_all_but(self, ["Blueprint: Deep Badwater Pump"])
        self.assertFalse(self.can_reach_location("Survival: Survive 5 Badtides"))
        self.assertTrue(self.can_reach_location("Survival: Survive 1st Badtide"))


class TestBadtidesGoalLate(TimberbornTestBase):
    options = {"faction": 0, "progressive_items": 0, "goal_selection": ["Badtides"],
               "badtide_cycles_goal": 15}

    def test_goal_needs_late_badtide_survival(self):
        _fresh_all_but(self, ["Blueprint: Large Tank"])
        self.assertFalse(self.can_reach_location("Victory: Badtides"))
        _fresh_all_but(self, [])
        self.assertTrue(self.can_reach_location("Victory: Badtides"))


class TestDroughtsGoalEarlyNeedsFloodgate(TimberbornTestBase):
    options = {"faction": 1, "progressive_items": 0, "goal_selection": ["Droughts"],
               "drought_cycles_goal": 5}

    def test_goal_needs_floodgate(self):
        _fresh_all_but(self, ["Blueprint: Floodgate"])
        self.assertFalse(self.can_reach_location("Victory: Droughts"))
        _fresh_all_but(self, [])
        self.assertTrue(self.can_reach_location("Victory: Droughts"))


class TestLongGoalNeedsSurvival(TimberbornTestBase):
    options = {"faction": 0, "progressive_items": 0, "goal_selection": ["Population"],
               "population_goal": 150}

    def test_population_goal_needs_mid_drought_survival(self):
        _fresh_all_but(self, ["Blueprint: Double Floodgate"])
        self.assertFalse(self.can_reach_location("Victory: Population"))
        _fresh_all_but(self, ["Blueprint: Contamination Sensor"])  # mid badtide only
        self.assertTrue(self.can_reach_location("Victory: Population"))


class TestShortGoalNeedsNoSurvival(TimberbornTestBase):
    options = {"faction": 0, "progressive_items": 0, "goal_selection": ["Population"],
               "population_goal": 50}

    def test_small_population_goal_has_no_survival_rule(self):
        _fresh_all_but(self, ["Blueprint: Double Floodgate", "Blueprint: Floodgate"])
        self.assertTrue(self.can_reach_location("Victory: Population"))


class TestFloodgateAndMediumTankForcedEarly(TimberbornTestBase):
    options = {"faction": 0, "progressive_items": 0, "force_early_items": 1}

    def test_early_items(self):
        early = self.multiworld.early_items[self.player]
        self.assertEqual(early.get("Blueprint: Floodgate"), 1)
        self.assertEqual(early.get("Blueprint: Medium Tank"), 1)
        # Forced into sphere 1, so tier 1 shop slots may hold them (#13).
        self.assertEqual(self.world.placement_tiers["Blueprint: Medium Tank"], 1)


class TestProgressiveFloodControlForcedEarly(TimberbornTestBase):
    options = {"faction": 1, "progressive_items": 2, "force_early_items": 1}

    def test_first_progressive_flood_control_is_early(self):
        early = self.multiworld.early_items[self.player]
        self.assertEqual(early.get("Progressive Flood Control"), 1)
        self.assertNotIn("Blueprint: Floodgate", early)


class TestRemovedDroughtDifficultyStillGenerates(TimberbornTestBase):
    """Old YAMLs set drought_difficulty and goal counts above the new maximums."""
    options = {"drought_difficulty": 5, "drought_cycles_goal": 100, "badtide_cycles_goal": 50,
               "goal_selection": ["Droughts", "Badtides"]}

    def test_old_values_generate(self):
        data = self.world.fill_slot_data()
        self.assertNotIn("drought_difficulty", data)
        self.assertEqual(data["drought_cycles_goal"], 40)
        self.assertEqual(data["badtide_cycles_goal"], 20)


class TestRemovedLogicDifficultyStandardStillGenerates(TimberbornTestBase):
    """Old YAMLs set logic_difficulty: standard."""
    options = {"logic_difficulty": "standard"}

    def test_old_value_generates(self):
        self.assertNotIn("logic_difficulty", self.world.fill_slot_data())


class TestRemovedLogicDifficultyStrictStillGenerates(TimberbornTestBase):
    """Old YAMLs set logic_difficulty: strict."""
    options = {"logic_difficulty": "strict"}

    def test_old_value_generates(self):
        self.assertNotIn("logic_difficulty", self.world.fill_slot_data())
