from BaseClasses import CollectionState
from . import TimberbornTestBase
from ..Rules import (TIER1_SCIENCE_LOCS, TIER2_SCIENCE_LOCS,
                     TIER3_SCIENCE_LOCS, TIER4_SCIENCE_LOCS,
                     TIER5_SCIENCE_LOCS)


# ============================================================================
# Flat shop mode tests (existing 5-tier logic)
# ============================================================================

class TestTier1Reachable(TimberbornTestBase):
    """Tier 1 locations should be reachable with no items (planks/power are free)."""
    options = {"shop_style": 0}

    def test_tier1_locations_reachable_empty_state(self):
        state = CollectionState(self.multiworld)
        for loc_name in TIER1_SCIENCE_LOCS:
            self.assertTrue(
                state.can_reach(loc_name, "Location", self.player),
                f"Tier 1 location '{loc_name}' should be reachable with empty state"
            )


class TestTier2RequiresGearWorkshop(TimberbornTestBase):
    """Tier 2 locations require Gear Workshop."""
    options = {"shop_style": 0}

    def test_tier2_blocked_without_gear_workshop(self):
        state = CollectionState(self.multiworld)
        test_locs = [loc for loc in TIER2_SCIENCE_LOCS
                     if loc != "Science: Gear Workshop"]
        for loc_name in test_locs[:3]:
            self.assertFalse(
                state.can_reach(loc_name, "Location", self.player),
                f"Tier 2 location '{loc_name}' should NOT be reachable without items"
            )

    def test_tier2_reachable_with_gear_workshop(self):
        self.collect_by_name(["Blueprint: Gear Workshop"])
        for loc_name in TIER2_SCIENCE_LOCS:
            self.assertTrue(
                self.can_reach_location(loc_name),
                f"Tier 2 location '{loc_name}' should be reachable with Gear Workshop"
            )


class TestTier3RequiresMetal(TimberbornTestBase):
    """Tier 3 requires Scavenger Flag + Smelter + Gear Workshop."""
    options = {"shop_style": 0}

    def test_tier3_blocked_without_metal(self):
        state = CollectionState(self.multiworld)
        test_locs = [loc for loc in TIER3_SCIENCE_LOCS
                     if loc not in {"Science: Scavenger Flag", "Science: Smelter",
                                    "Science: Gear Workshop"}]
        for loc_name in test_locs[:3]:
            self.assertFalse(
                state.can_reach(loc_name, "Location", self.player),
                f"Tier 3 location '{loc_name}' should NOT be reachable without metal"
            )

    def test_tier3_reachable_with_metal(self):
        self.collect_by_name([
            "Blueprint: Gear Workshop",
            "Blueprint: Scavenger Flag",
            "Blueprint: Smelter",
        ])
        for loc_name in TIER3_SCIENCE_LOCS:
            self.assertTrue(
                self.can_reach_location(loc_name),
                f"Tier 3 location '{loc_name}' should be reachable with metal chain"
            )


class TestTier4RequiresTreatedPlanks(TimberbornTestBase):
    """Tier 4 requires Tapper's Shack + Wood Workshop + Gear Workshop + metal."""
    options = {"shop_style": 0}

    def test_tier4_reachable_with_treated_planks(self):
        self.collect_by_name([
            "Blueprint: Gear Workshop",
            "Blueprint: Scavenger Flag",
            "Blueprint: Smelter",
            "Blueprint: Tapper's Shack",
            "Blueprint: Wood Workshop",
        ])
        for loc_name in TIER4_SCIENCE_LOCS:
            self.assertTrue(
                self.can_reach_location(loc_name),
                f"Tier 4 location '{loc_name}' should be reachable with treated planks"
            )


class TestTier5RequiresBots(TimberbornTestBase):
    """Tier 5 requires everything from tier 4 + Bot Part Factory + Bot Assembler."""
    options = {"shop_style": 0}

    def test_tier5_blocked_without_bots(self):
        self.collect_by_name([
            "Blueprint: Gear Workshop",
            "Blueprint: Scavenger Flag",
            "Blueprint: Smelter",
            "Blueprint: Tapper's Shack",
            "Blueprint: Wood Workshop",
        ])
        for loc_name in TIER5_SCIENCE_LOCS:
            self.assertFalse(
                self.can_reach_location(loc_name),
                f"Tier 5 location '{loc_name}' should NOT be reachable without bots"
            )

    def test_tier5_reachable_with_bots(self):
        self.collect_by_name([
            "Blueprint: Gear Workshop",
            "Blueprint: Scavenger Flag",
            "Blueprint: Smelter",
            "Blueprint: Tapper's Shack",
            "Blueprint: Wood Workshop",
            "Blueprint: Bot Part Factory",
            "Blueprint: Bot Assembler",
        ])
        for loc_name in TIER5_SCIENCE_LOCS:
            self.assertTrue(
                self.can_reach_location(loc_name),
                f"Tier 5 location '{loc_name}' should be reachable with bots"
            )


class TestFlatCompletionReachable(TimberbornTestBase):
    """With all progression items in flat mode, the game should be beatable."""
    options = {"shop_style": 0}

    def test_beatable_with_all_items(self):
        self.collect_all_but([])
        self.assertBeatable(True)

    def test_not_beatable_empty(self):
        """With default options (complete_wonder), empty state should not beat the game."""
        state = CollectionState(self.multiworld)
        self.multiworld.state = state


# ============================================================================
# Branching shop mode tests
# ============================================================================

class TestBranchingLevel0Reachable(TimberbornTestBase):
    """Level 0 locations (tier 1) should be reachable with empty state."""
    options = {"shop_style": 1}

    def test_level0_reachable_empty_state(self):
        state = CollectionState(self.multiworld)
        level0_locs = [e["location_name"] for e in self.world.shop_layout
                       if e["level"] == 0]
        self.assertEqual(len(level0_locs), 4, "Expected 4 level-0 locations (one per path)")
        for loc_name in level0_locs:
            self.assertTrue(
                state.can_reach(loc_name, "Location", self.player),
                f"Level 0 location '{loc_name}' should be reachable with empty state"
            )


class TestBranchingSequential(TimberbornTestBase):
    """Within a path, level N requires level N-1 to be reachable."""
    options = {"shop_style": 1}

    def test_level1_blocked_without_level0(self):
        state = CollectionState(self.multiworld)
        level1_locs = [e["location_name"] for e in self.world.shop_layout
                       if e["level"] == 1]
        for loc_name in level1_locs:
            self.assertFalse(
                state.can_reach(loc_name, "Location", self.player),
                f"Level 1 location '{loc_name}' should NOT be reachable without level 0"
            )


class TestBranchingTierGates(TimberbornTestBase):
    """Tier gates should block locations at higher levels."""
    options = {"shop_style": 1}

    def test_tier2_level_blocked_without_gear_workshop(self):
        """A location at tier 2+ should not be reachable without Gear Workshop."""
        state = CollectionState(self.multiworld)
        tier2_locs = [e for e in self.world.shop_layout if e["tier"] >= 2]
        if tier2_locs:
            loc_name = tier2_locs[0]["location_name"]
            self.assertFalse(
                state.can_reach(loc_name, "Location", self.player),
                f"Tier 2+ location '{loc_name}' should be blocked without Gear Workshop"
            )


class TestBranchingCompletionReachable(TimberbornTestBase):
    """With all progression items in branching mode, the game should be beatable."""
    options = {"shop_style": 1}

    def test_beatable_with_all_items(self):
        self.collect_all_but([])
        self.assertBeatable(True)
