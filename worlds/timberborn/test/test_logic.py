from BaseClasses import CollectionState
from . import TimberbornTestBase


# ============================================================================
# Branching shop mode tests
# ============================================================================

class TestBranchingLevel0Reachable(TimberbornTestBase):
    """Level 0 locations (tier 1) should be reachable with empty state."""

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
    """With all progression items, the game should be beatable."""

    def test_beatable_with_all_items(self):
        self.collect_all_but([])
        self.assertBeatable(True)
