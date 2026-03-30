from . import TimberbornTestBase


# ============================================================================
# Branching shop mode tests
# ============================================================================

class TestBranchingLevel0Reachable(TimberbornTestBase):
    """Level 0 locations (tier 1) should be reachable with empty state."""

    def test_level0_reachable_empty_state(self):
        level0_locs = [e["location_name"] for e in self.world.shop_layout
                       if e["level"] == 0]
        self.assertEqual(len(level0_locs), 4, "Expected 4 level-0 locations (one per path)")
        for loc_name in level0_locs:
            self.assertTrue(
                self.can_reach_location(loc_name),
                f"Level 0 location '{loc_name}' should be reachable with empty state"
            )


class TestBranchingSequential(TimberbornTestBase):
    """Within a path, level N requires level N-1 to be reachable."""

    def test_level1_blocked_without_level0(self):
        level1_locs = [e["location_name"] for e in self.world.shop_layout
                       if e["level"] == 1]
        for loc_name in level1_locs:
            self.assertFalse(
                self.can_reach_location(loc_name),
                f"Level 1 location '{loc_name}' should NOT be reachable without level 0"
            )


class TestBranchingTierGates(TimberbornTestBase):
    """Tier gates should block locations at higher levels."""

    def test_tier2_level_blocked_without_gear_workshop(self):
        """A location at tier 2+ should not be reachable without Gear Workshop."""
        tier2_locs = [e for e in self.world.shop_layout if e["tier"] >= 2]
        if tier2_locs:
            loc_name = tier2_locs[0]["location_name"]
            self.assertFalse(
                self.can_reach_location(loc_name),
                f"Tier 2+ location '{loc_name}' should be blocked without Gear Workshop"
            )


class TestBranchingCompletionReachable(TimberbornTestBase):
    """With all progression items, the game should be beatable."""

    def test_beatable_with_all_items(self):
        self.collect_all_but([])
        self.assertBeatable(True)


# ============================================================================
# Tier prerequisite chain tests (FT) — remove key items and verify blocked
# ============================================================================

class TestTier2RequiresForester(TimberbornTestBase):
    """Forester is needed for sustainable wood → gear production → tier 2."""

    def test_not_beatable_without_forester(self):
        self.collect_all_but("Blueprint: Forester")
        self.assertBeatable(False)

    def test_tier2_blocked_without_forester(self):
        """With everything except Forester, tier 2 locations should be unreachable."""
        self.collect_all_but("Blueprint: Forester")
        tier2_locs = [e for e in self.world.shop_layout if e["tier"] >= 2]
        for entry in tier2_locs[:3]:  # spot-check a few
            self.assertFalse(
                self.can_reach_location(entry["location_name"]),
                f"Tier 2+ location '{entry['location_name']}' should be blocked without Forester"
            )

    def test_tier1_still_reachable_without_forester(self):
        """Tier 1 locations should still be reachable without Forester."""
        self.collect_all_but("Blueprint: Forester")
        level0_locs = [e for e in self.world.shop_layout if e["level"] == 0]
        for entry in level0_locs:
            self.assertTrue(
                self.can_reach_location(entry["location_name"]),
                f"Level 0 location '{entry['location_name']}' should still be reachable"
            )


class TestTier2RequiresGearWorkshop(TimberbornTestBase):
    """Gear Workshop is the other half of the tier 2 gate."""

    def test_not_beatable_without_gear_workshop(self):
        self.collect_all_but("Blueprint: Gear Workshop")
        self.assertBeatable(False)

    def test_tier2_blocked_without_gear_workshop(self):
        self.collect_all_but("Blueprint: Gear Workshop")
        tier2_locs = [e for e in self.world.shop_layout if e["tier"] >= 2]
        for entry in tier2_locs[:3]:
            self.assertFalse(
                self.can_reach_location(entry["location_name"]),
                f"Tier 2+ location '{entry['location_name']}' should be blocked without Gear Workshop"
            )


class TestTier3RequiresSmelter(TimberbornTestBase):
    """Tier 3 requires metal production (Smelter + scrap + gears)."""

    def test_not_beatable_without_smelter(self):
        self.collect_all_but("Blueprint: Smelter")
        self.assertBeatable(False)

    def test_tier3_blocked_without_smelter(self):
        self.collect_all_but("Blueprint: Smelter")
        tier3_locs = [e for e in self.world.shop_layout if e["tier"] >= 3]
        for entry in tier3_locs[:3]:
            self.assertFalse(
                self.can_reach_location(entry["location_name"]),
                f"Tier 3+ location '{entry['location_name']}' should be blocked without Smelter"
            )


class TestFTTier3RequiresScavengerFlag(TimberbornTestBase):
    """Folktails need Scavenger Flag for scrap gathering (tier 3 gate)."""

    def test_tier3_blocked_without_scavenger_flag(self):
        self.collect_all_but("Blueprint: Scavenger Flag")
        tier3_locs = [e for e in self.world.shop_layout if e["tier"] >= 3]
        for entry in tier3_locs[:3]:
            self.assertFalse(
                self.can_reach_location(entry["location_name"]),
                f"FT Tier 3+ location '{entry['location_name']}' should be blocked without Scavenger Flag"
            )


class TestTier4RequiresTreatedPlankChain(TimberbornTestBase):
    """Tier 4 requires Tapper's Shack + Wood Workshop for treated planks."""

    def test_tier4_blocked_without_tappers_shack(self):
        self.collect_all_but("Blueprint: Tapper's Shack")
        tier4_locs = [e for e in self.world.shop_layout if e["tier"] >= 4]
        for entry in tier4_locs[:3]:
            self.assertFalse(
                self.can_reach_location(entry["location_name"]),
                f"Tier 4+ should be blocked without Tapper's Shack"
            )

    def test_tier4_blocked_without_wood_workshop(self):
        self.collect_all_but("Blueprint: Wood Workshop")
        tier4_locs = [e for e in self.world.shop_layout if e["tier"] >= 4]
        for entry in tier4_locs[:3]:
            self.assertFalse(
                self.can_reach_location(entry["location_name"]),
                f"Tier 4+ should be blocked without Wood Workshop"
            )


class TestTier5RequiresBotChain(TimberbornTestBase):
    """Tier 5 requires Bot Part Factory + Bot Assembler."""

    def test_tier5_blocked_without_bot_part_factory(self):
        self.collect_all_but("Blueprint: Bot Part Factory")
        tier5_locs = [e for e in self.world.shop_layout if e["tier"] >= 5]
        for entry in tier5_locs[:3]:
            self.assertFalse(
                self.can_reach_location(entry["location_name"]),
                f"Tier 5 should be blocked without Bot Part Factory"
            )

    def test_tier5_blocked_without_bot_assembler(self):
        self.collect_all_but("Blueprint: Bot Assembler")
        tier5_locs = [e for e in self.world.shop_layout if e["tier"] >= 5]
        for entry in tier5_locs[:3]:
            self.assertFalse(
                self.can_reach_location(entry["location_name"]),
                f"Tier 5 should be blocked without Bot Assembler"
            )


# ============================================================================
# Iron Teeth faction logic differences
# ============================================================================

class TestITTier3NoScavengerFlag(TimberbornTestBase):
    """Iron Teeth don't need Scavenger Flag for scrap gathering."""
    options = {"faction": 1}  # Iron Teeth

    def test_scavenger_flag_not_required(self):
        """IT should still be beatable without Scavenger Flag
        (it shouldn't even be in the IT item pool)."""
        self.collect_all_but("Blueprint: Scavenger Flag")
        self.assertBeatable(True)


class TestITBeatable(TimberbornTestBase):
    """Iron Teeth game should be beatable with all items."""
    options = {"faction": 1}

    def test_beatable(self):
        self.collect_all_but([])
        self.assertBeatable(True)


class TestITRequiresSmelterForTier3(TimberbornTestBase):
    """IT still needs Smelter for metal production (tier 3)."""
    options = {"faction": 1}

    def test_not_beatable_without_smelter(self):
        self.collect_all_but("Blueprint: Smelter")
        self.assertBeatable(False)


# ============================================================================
# Building prerequisite rules
# ============================================================================

class TestBuildingPrereqOverridesSlotTier(TimberbornTestBase):
    """A high-tier building placed in a low-tier slot should still require its tier."""

    def test_high_tier_building_in_low_slot_blocked(self):
        """Find a building whose tier exceeds its slot tier — it should be blocked
        even when the slot tier is satisfied."""
        from ..BuildingTiers import get_building_tier
        for entry in self.world.shop_layout:
            building_tier = get_building_tier(entry["building_name"], self.world.faction)
            slot_tier = entry["tier"]
            if building_tier > slot_tier and building_tier >= 3:
                # With everything except Smelter, T3+ buildings should be unreachable
                # even if their slot is T1/T2
                self.collect_all_but("Blueprint: Smelter")
                self.assertFalse(
                    self.can_reach_location(entry["location_name"]),
                    f"Building '{entry['building_name']}' (T{building_tier}) in slot "
                    f"'{entry['location_name']}' (T{slot_tier}) should be blocked "
                    f"without T{building_tier} tech"
                )
                return  # one example is enough


# ============================================================================
# Milestone tier gating
# ============================================================================

class TestMilestoneTierGating(TimberbornTestBase):
    """Milestones should respect their tier assignments."""
    options = {
        "include_population_milestones": 1,
        "include_wellbeing_milestones": 1,
        "include_survival_milestones": 1,
    }

    def test_tier1_milestone_reachable_empty(self):
        """Population: First Beaver Born is T1 — always reachable."""
        if "Population: First Beaver Born" not in self.world.active_milestones:
            return
        self.assertTrue(
            self.can_reach_location("Population: First Beaver Born"),
            "First Beaver Born (T1) should be reachable with empty state"
        )

    def test_high_tier_milestone_blocked(self):
        """Population: Reach 200 Beavers is T4 — blocked without T4 tech."""
        if "Population: Reach 200 Beavers" not in self.world.active_milestones:
            return
        # Without Tapper's Shack, can't reach T4
        self.collect_all_but("Blueprint: Tapper's Shack")
        self.assertFalse(
            self.can_reach_location("Population: Reach 200 Beavers"),
            "Population 200 (T4) should be blocked without T4 tech"
        )

    def test_wonder_milestone_requires_tier5(self):
        """Wonder milestones require tier 5."""
        wonder_name = ("Wonder: Complete Earth Recultivator"
                       if self.world.faction == "Folktails"
                       else "Wonder: Complete Earth Repopulator")
        if wonder_name not in self.world.active_milestones:
            return
        self.collect_all_but("Blueprint: Bot Part Factory")
        self.assertFalse(
            self.can_reach_location(wonder_name),
            f"{wonder_name} should be blocked without T5 tech"
        )


# ============================================================================
# Strict mode logic
# ============================================================================

class TestStrictModeSurvivalRequirements(TimberbornTestBase):
    """Strict mode adds building requirements for survival milestones."""
    options = {
        "logic_difficulty": 1,  # strict
        "include_survival_milestones": 1,
    }

    def test_survive_5_droughts_requires_levee(self):
        if "Survival: Survive 5 Droughts" not in self.world.active_milestones:
            return
        self.collect_all_but("Blueprint: Levee")
        self.assertFalse(
            self.can_reach_location("Survival: Survive 5 Droughts"),
            "Strict mode: Survive 5 Droughts should require Levee"
        )

    def test_badtide_requires_floodgate(self):
        if "Survival: Survive 1st Badtide" not in self.world.active_milestones:
            return
        # Floodgate is part of Progressive Flood Control, so exclude both
        self.collect_all_but(["Blueprint: Floodgate", "Progressive Flood Control"])
        self.assertFalse(
            self.can_reach_location("Survival: Survive 1st Badtide"),
            "Strict mode: Survive 1st Badtide should require Floodgate"
        )

    def test_survive_5_badtides_requires_stairs(self):
        if "Survival: Survive 5 Badtides" not in self.world.active_milestones:
            return
        # Stairs is part of Progressive Platforms, so exclude both
        self.collect_all_but(["Blueprint: Stairs", "Progressive Platforms"])
        self.assertFalse(
            self.can_reach_location("Survival: Survive 5 Badtides"),
            "Strict mode: Survive 5 Badtides should require Stairs"
        )


# ============================================================================
# Goal completion conditions
# ============================================================================

class TestWonderGoalRequiresTier5(TimberbornTestBase):
    """Wonder goal needs full tier 5 tech chain."""
    options = {"goal_selection": {"Wonder"}}

    def test_not_beatable_without_bot_chain(self):
        self.collect_all_but(["Blueprint: Bot Part Factory", "Blueprint: Bot Assembler"])
        self.assertBeatable(False)

    def test_beatable_with_full_chain(self):
        self.collect_all_but([])
        self.assertBeatable(True)


class TestPopulationGoalBeatable(TimberbornTestBase):
    """Population goal should be beatable when Victory event is reachable."""
    options = {"goal_selection": {"Population"}, "population_goal": 25}

    def test_beatable_with_all_items(self):
        self.collect_all_but([])
        self.assertBeatable(True)


class TestMultiGoalAll(TimberbornTestBase):
    """With require_all, ALL goals must be satisfied."""
    options = {
        "goal_selection": {"Wonder", "Population"},
        "goal_requirement": 1,  # all
        "population_goal": 25,
    }

    def test_beatable_with_all_items(self):
        self.collect_all_but([])
        self.assertBeatable(True)

    def test_not_beatable_without_tier5(self):
        """Wonder requires T5 — missing bot chain should block completion."""
        self.collect_all_but(["Blueprint: Bot Part Factory", "Blueprint: Bot Assembler"])
        self.assertBeatable(False)


class TestMultiGoalAny(TimberbornTestBase):
    """With require_any, completing one goal suffices."""
    options = {
        "goal_selection": {"Wonder", "Population"},
        "goal_requirement": 0,  # any
        "population_goal": 10,
    }

    def test_beatable_with_all_items(self):
        self.collect_all_but([])
        self.assertBeatable(True)


class TestBotsGoalRequiresTier5(TimberbornTestBase):
    """Bots goal always requires tier 5."""
    options = {"goal_selection": {"Bots"}, "bots_goal": 5}

    def test_victory_location_blocked_without_bot_chain(self):
        """Victory: Bots location should be unreachable without T5 tech."""
        self.collect_all_but(["Blueprint: Bot Part Factory", "Blueprint: Bot Assembler"])
        self.assertFalse(
            self.can_reach_location("Victory: Bots"),
            "Victory: Bots should be unreachable without bot production chain"
        )

    def test_beatable_with_all_items(self):
        self.collect_all_but([])
        self.assertBeatable(True)
