from BaseClasses import CollectionState
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import TimberbornWorld

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
    return has(state, player, "Gear Workshop")

def can_produce_paper(state: CollectionState, player: int) -> bool:
    return has(state, player, "Paper Mill") and can_produce_gears(state, player)

def has_power(state: CollectionState, player: int) -> bool:
    """Water Wheel and Power Wheel are FREE — basic power is always available."""
    return True

def has_advanced_power(state: CollectionState, player: int) -> bool:
    """Sustained or large-scale power for industrial buildings."""
    return has_any(state, player, "Geothermal Engine", "Wind Turbine",
                   "Gravity Battery", "Large Wind Turbine")

def can_gather_scrap(state: CollectionState, player: int) -> bool:
    return has(state, player, "Scavenger Flag")

def can_produce_metal(state: CollectionState, player: int) -> bool:
    """Smelter converts ScrapMetal → MetalBlock; requires scrap gathering first."""
    return can_gather_scrap(state, player) and has(state, player, "Smelter")

def can_produce_treated_planks(state: CollectionState, player: int) -> bool:
    """Tapper's Shack → PineResin; Wood Workshop → TreatedPlank."""
    return (has(state, player, "Tapper's Shack")
            and has(state, player, "Wood Workshop")
            and can_produce_gears(state, player))

def can_produce_explosives(state: CollectionState, player: int) -> bool:
    """Explosives Factory converts Badwater → Explosives."""
    return has(state, player, "Explosives Factory") and can_produce_metal(state, player)

def can_produce_extract(state: CollectionState, player: int) -> bool:
    """Refinery converts Badwater → Extract."""
    return has(state, player, "Refinery") and can_produce_metal(state, player)

def can_build_bots(state: CollectionState, player: int) -> bool:
    return (has(state, player, "Bot Part Factory")
            and has(state, player, "Bot Assembler")
            and can_produce_metal(state, player)
            and can_produce_gears(state, player))

def has_science_production(state: CollectionState, player: int) -> bool:
    """Inventor is FREE — science production is always available."""
    return True

# ---------------------------------------------------------------------------
# Tier helpers used to bulk-set rules
# ---------------------------------------------------------------------------

def _tier1(state: CollectionState, player: int) -> bool:
    """Basic colony — planks and power always available (both free)."""
    return True

def _tier2(state: CollectionState, player: int) -> bool:
    """Wood processing tier — requires Gear Workshop."""
    return can_produce_gears(state, player)

def _tier3(state: CollectionState, player: int) -> bool:
    """Metal tier — requires Scavenger Flag + Smelter + Gear Workshop."""
    return can_produce_metal(state, player) and can_produce_gears(state, player)

def _tier4(state: CollectionState, player: int) -> bool:
    """Advanced tier — treated planks, explosives, extract."""
    return _tier3(state, player) and can_produce_treated_planks(state, player)

def _tier5(state: CollectionState, player: int) -> bool:
    """Endgame — bots, late metal, high science production."""
    return _tier4(state, player) and can_build_bots(state, player)


def _tier_predicate(tier: int, state: CollectionState, player: int) -> bool:
    """Dispatch to the correct tier check by number."""
    if tier <= 1:
        return _tier1(state, player)
    if tier == 2:
        return _tier2(state, player)
    if tier == 3:
        return _tier3(state, player)
    if tier == 4:
        return _tier4(state, player)
    return _tier5(state, player)


# ---------------------------------------------------------------------------
# Rule setters
# ---------------------------------------------------------------------------

def set_rules(world: "TimberbornWorld") -> None:
    player = world.player
    mw = world.multiworld
    _set_branching_rules(world, player, mw)
    _set_completion_condition(world, player, mw)


def _set_branching_rules(world, player, mw) -> None:
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
                rule = lambda state, p=player, t=tier: (
                    _tier_predicate(t, state, p)
                )
            else:
                prev_loc_name = entries[idx - 1][1]
                prev_event = f"Event: {prev_loc_name} Checked"
                rule = lambda state, p=player, t=tier, ev=prev_event: (
                    _tier_predicate(t, state, p)
                    and state.has(ev, p)
                )

            loc.access_rule = rule

            # Event location (if it exists) gets the same access rule.
            # Last location in each path has no event.
            if idx < len(entries) - 1:
                event_name = f"Event: {loc_name} Checked"
                event_loc = mw.get_location(event_name, player)
                event_loc.access_rule = rule

    # Milestone locations have no access rules (unchanged)


def _set_completion_condition(world, player, mw) -> None:
    goal = world.options.goal.value
    if goal == 0:  # complete_wonder
        mw.completion_condition[player] = lambda state: (
            state.can_reach("Wonder: Complete Earth Recultivator", "Location", player)
        )
    else:
        # reach_population / survive_cycles: client sends a Victory item when done
        mw.completion_condition[player] = lambda state: (
            state.can_reach("Timberborn", "Region", player)
        )
