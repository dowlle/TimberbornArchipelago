from BaseClasses import CollectionState
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import TimberbornWorld

from .BuildingTiers import get_building_tier

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def has(state: CollectionState, player: int, item: str) -> bool:
    return state.has(f"Blueprint: {item}", player)

def has_any(state: CollectionState, player: int, *items: str) -> bool:
    return any(state.has(f"Blueprint: {i}", player) for i in items)

def has_all(state: CollectionState, player: int, *items: str) -> bool:
    return all(state.has(f"Blueprint: {i}", player) for i in items)

# ---------------------------------------------------------------------------
# Resource-chain predicates
# (names match exact in-game building names, without the "Blueprint: " prefix)
# ---------------------------------------------------------------------------

def can_produce_planks(state: CollectionState, player: int) -> bool:
    """Lumber Mill is FREE — planks are always producible from logs."""
    return True

def can_produce_gears(state: CollectionState, player: int) -> bool:
    """Gear Workshop needs sustainable wood supply (Forester)."""
    return has(state, player, "Gear Workshop") and can_replant_trees(state, player)

def can_replant_trees(state: CollectionState, player: int) -> bool:
    """Forester is required for sustainable wood — must arrive before T2."""
    return has(state, player, "Forester")

def can_produce_paper(state: CollectionState, player: int) -> bool:
    return has(state, player, "Paper Mill") and can_produce_gears(state, player)

def has_power(state: CollectionState, player: int) -> bool:
    """Water Wheel and Power Wheel are FREE — basic power is always available."""
    return True

def has_advanced_power(state: CollectionState, player: int) -> bool:
    """Sustained or large-scale power for industrial buildings."""
    return has_any(state, player, "Geothermal Engine", "Wind Turbine",
                   "Gravity Battery", "Large Wind Turbine", "Steam Engine")

def can_gather_scrap(state: CollectionState, player: int, faction: str = "Folktails") -> bool:
    """ScavengerFlag is free for IronTeeth (SC=0), requires unlock for Folktails."""
    if faction == "IronTeeth":
        return True
    return has(state, player, "Scavenger Flag")

def can_produce_metal(state: CollectionState, player: int, faction: str = "Folktails") -> bool:
    """Smelter converts ScrapMetal → MetalBlock; requires scrap gathering first."""
    return can_gather_scrap(state, player, faction) and has(state, player, "Smelter")

def can_produce_treated_planks(state: CollectionState, player: int) -> bool:
    """Tapper's Shack → PineResin; Wood Workshop → TreatedPlank."""
    return (has(state, player, "Tapper's Shack")
            and has(state, player, "Wood Workshop")
            and can_produce_gears(state, player))

def can_produce_explosives(state: CollectionState, player: int, faction: str = "Folktails") -> bool:
    """Explosives Factory converts Badwater → Explosives."""
    return has(state, player, "Explosives Factory") and can_produce_metal(state, player, faction)

def can_produce_extract(state: CollectionState, player: int, faction: str = "Folktails") -> bool:
    """Refinery converts Badwater → Extract."""
    return has(state, player, "Refinery") and can_produce_metal(state, player, faction)

def can_build_bots(state: CollectionState, player: int, faction: str = "Folktails") -> bool:
    return (has(state, player, "Bot Part Factory")
            and has(state, player, "Bot Assembler")
            and can_produce_metal(state, player, faction)
            and can_produce_gears(state, player))

def has_science_production(state: CollectionState, player: int) -> bool:
    """Inventor is FREE — science production is always available."""
    return True

# ---------------------------------------------------------------------------
# Tier helpers used to bulk-set rules
# ---------------------------------------------------------------------------

def _tier1(state: CollectionState, player: int, faction: str = "Folktails") -> bool:
    """Basic colony — planks and power always available (both free)."""
    return True

def _tier2(state: CollectionState, player: int, faction: str = "Folktails") -> bool:
    """Wood processing tier — requires Gear Workshop (which needs sustainable wood)."""
    return can_produce_gears(state, player)

def _tier3(state: CollectionState, player: int, faction: str = "Folktails") -> bool:
    """Metal tier — requires Smelter + Gear Workshop. FT also needs Scavenger Flag."""
    return can_produce_metal(state, player, faction) and can_produce_gears(state, player)

def _tier4(state: CollectionState, player: int, faction: str = "Folktails") -> bool:
    """Advanced tier — treated planks, explosives, extract."""
    return _tier3(state, player, faction) and can_produce_treated_planks(state, player)

def _tier5(state: CollectionState, player: int, faction: str = "Folktails") -> bool:
    """Endgame — bots, late metal, high science production."""
    return _tier4(state, player, faction) and can_build_bots(state, player, faction)


def _tier_predicate(tier: int, state: CollectionState, player: int,
                    faction: str = "Folktails") -> bool:
    """Dispatch to the correct tier check by number."""
    if tier <= 1:
        return _tier1(state, player, faction)
    if tier == 2:
        return _tier2(state, player, faction)
    if tier == 3:
        return _tier3(state, player, faction)
    if tier == 4:
        return _tier4(state, player, faction)
    return _tier5(state, player, faction)


# ---------------------------------------------------------------------------
# Rule setters
# ---------------------------------------------------------------------------

def set_rules(world: "TimberbornWorld") -> None:
    player = world.player
    mw = world.multiworld
    faction = world.faction
    _set_branching_rules(world, player, mw, faction)
    _set_building_prerequisite_rules(world, player, mw, faction)
    _set_completion_condition(world, player, mw, faction)


def _set_branching_rules(world, player, mw, faction: str) -> None:
    """Branching-path shop rules: sequential within each path + tier gates.

    Sequential ordering uses event items placed at each location in
    create_regions.  Location N in a path requires the event item from
    location N-1 (``state.has("Event: <prev> Checked")``).
    """
    # Build lookup: path -> sorted list of (level, location_name)
    path_levels: dict[str, list[tuple[int, str]]] = {}
    for entry in world.shop_layout:
        path = entry["path"]
        if path not in path_levels:
            path_levels[path] = []
        path_levels[path].append((entry["level"], entry["location_name"]))

    for path in path_levels:
        path_levels[path].sort()

    # Build a quick tier lookup: location_name -> tier
    tier_lookup = {e["location_name"]: e["tier"] for e in world.shop_layout}

    # Set access rules for each shop location and its event twin
    for path, entries in path_levels.items():
        for idx, (level, loc_name) in enumerate(entries):
            loc = mw.get_location(loc_name, player)
            tier = tier_lookup[loc_name]

            if idx == 0:
                rule = lambda state, p=player, t=tier, f=faction: (
                    _tier_predicate(t, state, p, f)
                )
            else:
                prev_loc_name = entries[idx - 1][1]
                prev_event = f"Event: {prev_loc_name} Checked"
                rule = lambda state, p=player, t=tier, ev=prev_event, f=faction: (
                    _tier_predicate(t, state, p, f)
                    and state.has(ev, p)
                    and can_replant_trees(state, p)
                )

            loc.access_rule = rule

            # Event location (if it exists) gets the same access rule.
            # Last location in each path has no event.
            if idx < len(entries) - 1:
                event_name = f"Event: {loc_name} Checked"
                event_loc = mw.get_location(event_name, player)
                event_loc.access_rule = rule

    # Milestone access rules — only for active milestones
    _set_milestone_rules(world, player, mw, faction)


def _set_building_prerequisite_rules(world, player, mw, faction: str) -> None:
    """Gate each shop location by the construction prerequisites of its building.

    The existing tier gate is based on the SLOT's position in the shop layout.
    This adds an additional constraint based on what BUILDING is displayed at
    that slot — e.g. if the slot shows Smelter (T3), the player must be able
    to produce metal before checking it, regardless of the slot's position.

    The two constraints are combined: the original rule (sequential + slot tier)
    must ALSO pass alongside the building's resource prerequisites.
    """
    # Build set of event location names (non-last entries in each path)
    path_levels: dict[str, list[tuple[int, str]]] = {}
    for entry in world.shop_layout:
        path = entry["path"]
        if path not in path_levels:
            path_levels[path] = []
        path_levels[path].append((entry["level"], entry["location_name"]))
    for path in path_levels:
        path_levels[path].sort()

    event_names: set[str] = set()
    for path, entries in path_levels.items():
        for idx, (level, loc_name) in enumerate(entries):
            if idx < len(entries) - 1:
                event_names.add(f"Event: {loc_name} Checked")

    for entry in world.shop_layout:
        loc_name = entry["location_name"]
        building = entry["building_name"]
        building_tier = get_building_tier(building, faction)

        # T1 buildings have no extra prerequisites
        if building_tier <= 1:
            continue

        loc = mw.get_location(loc_name, player)
        original_rule = loc.access_rule

        # Combined rule: original (sequential + slot tier) AND building prereqs
        loc.access_rule = lambda state, p=player, bt=building_tier, f=faction, orig=original_rule: (
            orig(state) and _tier_predicate(bt, state, p, f)
        )

        # Also update the event location if it exists
        event_name = f"Event: {loc_name} Checked"
        if event_name in event_names:
            event_loc = mw.get_location(event_name, player)
            event_orig = event_loc.access_rule
            event_loc.access_rule = lambda state, p=player, bt=building_tier, f=faction, eo=event_orig: (
                eo(state) and _tier_predicate(bt, state, p, f)
            )


# Maps milestone location names to their logic tier (1-5).
MILESTONE_TIERS: dict[str, int] = {
    # Population
    "Population: First Beaver Born":    1,
    "Population: First Beaver Grown Up": 1,
    "Population: Reach 10 Beavers":     1,
    "Population: Reach 25 Beavers":     2,
    "Population: Reach 50 Beavers":     2,
    "Population: Reach 100 Beavers":    3,
    "Population: Reach 200 Beavers":    4,
    # Well-being
    "Well-being: Reach Level 5":        1,
    "Well-being: Reach Level 10":       2,
    "Well-being: Reach Level 15":       3,
    "Well-being: Reach Level 20":       4,
    # Survival
    "Survival: Survive 1st Drought":    1,
    "Survival: Survive 5 Droughts":     2,
    "Survival: Survive 10 Droughts":    3,
    "Survival: Survive 1st Badtide":    2,
    "Survival: Survive 5 Badtides":     3,
    "Survival: Survive 10 Badtides":    4,
    # Wonder (both factions)
    "Wonder: Complete Earth Recultivator": 5,
    "Wonder: Complete Earth Repopulator":  5,
}


def _set_milestone_rules(world, player, mw, faction: str) -> None:
    """Gate milestones by tier so they appear in proper logic spheres.

    In strict mode, survival milestones also require specific buildings
    (Levee, Floodgate, Stairs, Medium Tank) that are practically needed
    to survive droughts and badtides.
    """
    strict = world.options.logic_difficulty.value == 1

    for loc_name in world.active_milestones:
        tier = MILESTONE_TIERS.get(loc_name, 1)
        loc = mw.get_location(loc_name, player)

        if strict and loc_name in STRICT_MILESTONE_REQUIREMENTS:
            required = STRICT_MILESTONE_REQUIREMENTS[loc_name]
            loc.access_rule = lambda state, p=player, t=tier, f=faction, req=required: (
                _tier_predicate(t, state, p, f)
                and all(has(state, p, bld) for bld in req)
            )
        else:
            loc.access_rule = lambda state, p=player, t=tier, f=faction: (
                _tier_predicate(t, state, p, f)
            )


# Strict-mode building requirements for survival milestones.
# These buildings are practically necessary to survive the event in-game.
STRICT_MILESTONE_REQUIREMENTS: dict[str, list[str]] = {
    # Droughts — need water storage infrastructure
    "Survival: Survive 5 Droughts":     ["Levee"],
    "Survival: Survive 10 Droughts":    ["Levee", "Medium Tank"],
    # Badtides — need flood control to contain contaminated water
    "Survival: Survive 1st Badtide":    ["Levee", "Floodgate"],
    "Survival: Survive 5 Badtides":     ["Levee", "Floodgate", "Stairs"],
    "Survival: Survive 10 Badtides":    ["Levee", "Floodgate", "Stairs"],
}


def _resolve_goals(world) -> set[str]:
    """Return the resolved set of active goals, falling back to Wonder if empty."""
    goals = set(world.options.goal_selection.value)
    if not goals:
        goals = {"Wonder"}
    return goals


def _goal_tier(goal_name: str, world) -> int:
    """Return the logic tier required to achieve a client-tracked goal.

    This gates Victory event locations so the solver knows what tech is
    needed before the goal can be completed in-game.
    """
    if goal_name == "Population":
        pop = world.options.population_goal.value
        if pop <= 10:
            return 1
        if pop <= 50:
            return 2
        if pop <= 100:
            return 3
        if pop <= 200:
            return 4
        return 5
    if goal_name == "Well-being":
        wb = world.options.wellbeing_goal.value
        if wb <= 5:
            return 1
        if wb <= 10:
            return 2
        if wb <= 15:
            return 3
        return 4
    if goal_name == "Droughts":
        d = world.options.drought_cycles_goal.value
        if d <= 1:
            return 1
        if d <= 5:
            return 2
        if d <= 10:
            return 3
        return 4
    if goal_name == "Badtides":
        b = world.options.badtide_cycles_goal.value
        if b <= 1:
            return 2
        if b <= 5:
            return 3
        return 4
    if goal_name == "Bots":
        return 5  # always requires bot production chain
    if goal_name == "Water Storage":
        ws = world.options.water_storage_goal.value
        if ws <= 1000:
            return 2
        if ws <= 5000:
            return 3
        return 4
    return 2  # safe default


def _set_completion_condition(world, player, mw, faction: str) -> None:
    goals = _resolve_goals(world)
    world.resolved_goals = goals  # store for slot_data
    require_all = world.options.goal_requirement.value == 1

    # Wonder is the only goal with a pure logic check (requires T5 tech).
    # All other goals are tracked client-side: the client sends an event item
    # "Victory: <GoalName>" when the in-game condition is met.
    # The completion condition checks for these event items.

    goal_checks: list = []

    if "Wonder" in goals:
        goal_checks.append(
            lambda state, p=player, f=faction: _tier5(state, p, f)
        )

    client_goals = goals - {"Wonder"}
    for goal_name in sorted(client_goals):
        event = f"Victory: {goal_name}"
        goal_checks.append(
            lambda state, p=player, ev=event: state.has(ev, p)
        )

        # Gate the Victory event location so the solver knows what tech is
        # required before the goal can be achieved in-game.
        tier = _goal_tier(goal_name, world)
        event_loc = mw.get_location(event, player)
        event_loc.access_rule = lambda state, p=player, t=tier, f=faction: (
            _tier_predicate(t, state, p, f)
        )

    if not goal_checks:
        # Safety fallback — should not happen due to _resolve_goals
        mw.completion_condition[player] = lambda state, f=faction: _tier5(state, player, f)
        return

    if require_all:
        mw.completion_condition[player] = lambda state: all(
            check(state) for check in goal_checks
        )
    else:
        mw.completion_condition[player] = lambda state: any(
            check(state) for check in goal_checks
        )
