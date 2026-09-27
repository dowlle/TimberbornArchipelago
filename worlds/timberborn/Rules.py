import re

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

def can_gather_badwater(state: CollectionState, player: int, faction: str = "Folktails") -> bool:
    """A badwater source: Badwater Pump (Folktails) or Deep Badwater Pump via Metalsmith (Iron Teeth)."""
    return resource_chain_met("Badwater", 1, state, player, faction)

def can_produce_explosives(state: CollectionState, player: int, faction: str = "Folktails") -> bool:
    """Explosives Factory converts Badwater → Explosives."""
    return resource_chain_met("Explosives", 1, state, player, faction)

def can_produce_extract(state: CollectionState, player: int, faction: str = "Folktails") -> bool:
    """Centrifuge converts Badwater → Extract (Refinery makes Biofuel and Catalyst)."""
    return resource_chain_met("Extract", 1, state, player, faction)

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


# Buildings that consume Explosives or Extract, from the 1.1 blueprints: as
# construction material (BuildingCost), as a recipe ingredient the building
# cannot work without, or as a consumed good or nutrient. Refinery (Catalyst)
# and Efficient Mine (efficient scrap recipe) also have recipes without
# Extract, so they stay usable without it and are not listed.
EXPLOSIVES_CONSUMERS: frozenset[str] = frozenset({
    "Dynamite", "Double Dynamite", "Triple Dynamite", "Tunnel", "Detonator",
})
EXTRACT_CONSUMERS: frozenset[str] = frozenset({
    "Double Dynamite", "Triple Dynamite", "Tunnel", "Detonator", "Memory",
    "Pole Banner", "Square Banner", "Agora", "Detailer",
    "Decontamination Pod", "Advanced Breeding Pod", "Grease Factory",
})


def building_prerequisite_blueprints(building: str, faction: str = "Folktails") -> tuple[str, ...]:
    """Blueprints a building needs beyond the shop's material-tier policy.

    Explosives and Extract consumers need the good's whole production chain,
    badwater source included. Iron Teeth Dance Pit costs Metal Parts.
    """
    required: list[str] = []
    if building in EXPLOSIVES_CONSUMERS:
        required += resource_chain_blueprints("Explosives", 1, faction)
    if building in EXTRACT_CONSUMERS:
        required += resource_chain_blueprints("Extract", 1, faction)
    if building == "Dance Pit" and faction == "IronTeeth":
        required.append("Metalsmith")
    return tuple(dict.fromkeys(required))


def has_building_prerequisites(building: str, state: CollectionState, player: int,
                               faction: str = "Folktails") -> bool:
    """Requirements beyond the shop's conservative material-tier policy."""
    return has_all(state, player, *building_prerequisite_blueprints(building, faction))

def set_rules(world: "TimberbornWorld") -> None:
    player = world.player
    mw = world.multiworld
    faction = world.faction
    _set_branching_rules(world, player, mw, faction)
    _set_building_prerequisite_rules(world, player, mw, faction)
    _set_completion_condition(world, player, mw, faction)
    _set_tier_placement_rules(world, player, mw)


# ---------------------------------------------------------------------------
# Tier-gated placement (#13)
#
# A Timberborn blueprint may only be placed in a Timberborn shop slot whose
# tier is at least the blueprint's own construction tier, so a Smelter (tier 3)
# never sits in a tier 1 slot that is reachable before metal. This is an item
# rule, not an access rule: it limits where fill puts items and never changes
# what a location needs. A progressive item counts as its first step. Items
# without a tier (packages, traps, boosts, scouts, skips), other games' items
# and Timberborn blueprints in other games' locations are unrestricted.
# Starting items are precollected, never placed, so the rule does not see them.
# ---------------------------------------------------------------------------

def placement_tiers(faction: str, progressive_chains: dict[str, tuple[str, ...]] | None) -> dict[str, int]:
    """Placement tier of every blueprint item of a faction, progressive items included."""
    from .Items import get_building_names
    tiers = {f"Blueprint: {name}": get_building_tier(name, faction)
             for name in get_building_names(faction)}
    for prog_name, chain in (progressive_chains or {}).items():
        tiers[prog_name] = get_building_tier(chain[0], faction)
    return tiers


def item_placement_tier(item, multiworld) -> int:
    """Tier an item needs from a Timberborn shop slot; 0 when unrestricted."""
    if item.game != "Timberborn":
        return 0
    tiers = getattr(multiworld.worlds[item.player], "placement_tiers", None) or {}
    return tiers.get(item.name, 0)


def _set_tier_placement_rules(world, player, mw) -> None:
    for entry in world.shop_layout:
        loc = mw.get_location(entry["location_name"], player)
        original = loc.item_rule
        loc.item_rule = lambda item, t=entry["tier"], orig=original, m=mw: (
            item_placement_tier(item, m) <= t and orig(item)
        )


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
        prerequisites = building_prerequisite_blueprints(building, faction)

        # T1 buildings without extra prerequisites need nothing more
        if building_tier <= 1 and not prerequisites:
            continue

        loc = mw.get_location(loc_name, player)
        original_rule = loc.access_rule

        # Combined rule: original (sequential + slot tier) AND building prereqs
        loc.access_rule = lambda state, p=player, bt=building_tier, f=faction, req=prerequisites, orig=original_rule: (
            orig(state) and _tier_predicate(bt, state, p, f)
            and has_all(state, p, *req)
        )

        # Also update the event location if it exists
        event_name = f"Event: {loc_name} Checked"
        if event_name in event_names:
            event_loc = mw.get_location(event_name, player)
            event_orig = event_loc.access_rule
            event_loc.access_rule = lambda state, p=player, bt=building_tier, f=faction, req=prerequisites, eo=event_orig: (
                eo(state) and _tier_predicate(bt, state, p, f)
                and has_all(state, p, *req)
            )


# Maps milestone location names to their logic tier (1-5).
MILESTONE_TIERS: dict[str, int] = {
    # Population
    "Population: First Beaver Born":    1,
    "Population: First Beaver Grown Up": 1,
    "Population: Reach 15 Beavers":     1,
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
    # Resource milestones use RESOURCE_CHAINS below, not a tier.
}


# ---------------------------------------------------------------------------
# Resource milestone production chains
#
# A resource milestone is in logic once the player owns every blueprint of the
# good's production chain and can make the materials those buildings cost
# ("gears", "metal", "treated"). Received resource packages never count.
# Material needs come from the chain buildings' BuildingCost in the 1.1
# blueprints; Metal Parts come from Metalsmith, whose scrap is free for Iron
# Teeth. This deliberately avoids the tier bundles: tier 5 would demand the
# whole bot chain for any building that costs Metal Parts.
# ---------------------------------------------------------------------------
_SHARED_CHAINS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    # good:           (blueprints, materials)
    "Logs":           ((), ()),
    "Planks":         ((), ()),
    "Berries":        ((), ()),
    "Water":          ((), ()),
    "Gears":          ((), ("gears",)),
    "Pine Resin":     (("Tapper's Shack",), ("gears",)),
    "Treated Planks": ((), ("treated",)),
    "Metal Blocks":   ((), ("metal",)),
}

# Where each faction gets Badwater as a good. Folktails pump it (Badwater Pump);
# the Badwater Rig is a 4000-science alternative left out of logic, and the
# Badwater Dome only caps a source. Iron Teeth need the Deep Badwater Pump,
# which costs Metal Parts from the Metalsmith (tier 5, accepted in #2).
BADWATER_SOURCES: dict[str, tuple[str, ...]] = {
    "Folktails": ("Badwater Pump",),
    "IronTeeth": ("Metalsmith", "Deep Badwater Pump"),
}

RESOURCE_CHAINS: dict[str, dict[str, tuple[tuple[str, ...], tuple[str, ...]]]] = {
    "Folktails": {
        **_SHARED_CHAINS,
        "Scrap Metal":      (("Scavenger Flag",), ()),
        "Badwater":         (BADWATER_SOURCES["Folktails"], ("metal",)),
        "Extract":          ((*BADWATER_SOURCES["Folktails"], "Centrifuge"), ("metal",)),
        "Explosives":       ((*BADWATER_SOURCES["Folktails"], "Explosives Factory"), ("metal",)),
        "Bread":            (("Gristmill", "Bakery"), ("gears",)),
        "Paper":            (("Paper Mill",), ("gears",)),
        "Grilled Potatoes": ((), ()),
        "Cattail Crackers": (("Aquatic Farmhouse", "Gristmill", "Bakery"), ("gears",)),
        "Maple Pastries":   (("Gristmill", "Bakery", "Tapper's Shack"), ("gears",)),
        "Books":            (("Paper Mill", "Printing Press"), ("metal",)),
        "Biofuel":          (("Refinery",), ("metal",)),
        "Antidote":         (("Herbalist", "Paper Mill"), ("gears",)),
    },
    "IronTeeth": {
        **_SHARED_CHAINS,
        "Scrap Metal":       ((), ()),
        "Badwater":          (BADWATER_SOURCES["IronTeeth"], ("metal",)),
        "Extract":           ((*BADWATER_SOURCES["IronTeeth"], "Centrifuge"), ("metal",)),
        "Explosives":        ((*BADWATER_SOURCES["IronTeeth"], "Explosives Factory"), ("metal",)),
        "Corn Rations":      (("Food Factory",), ("metal",)),
        "Fermented Cassava": ((), ()),
        "Kohlrabi":          ((), ()),
        "Mangrove Fruit":    (("Forester",), ()),
        "Metal Parts":       (("Metalsmith",), ()),
        "Eggplant Rations":  (("Food Factory", "Metalsmith", "Oil Press"), ("metal",)),
        "Fermented Soybean": (("Metalsmith", "Oil Press"), ()),
        "Coffee":            (("Coffee Brewery",), ("treated", "metal")),
        "Grease":            (("Grease Factory", "Centrifuge", "Metalsmith", "Oil Press",
                               "Deep Badwater Pump"), ("treated", "metal")),
    },
}

# Liquids live in tanks. Small Tanks hold 30, so 250 or more needs Medium Tank.
LIQUID_GOODS: set[str] = {"Water", "Extract", "Antidote", "Biofuel", "Coffee", "Grease"}
LARGE_LIQUID_THRESHOLD = 250


def parse_resource_milestone(name: str) -> tuple[str, int]:
    """Parse "Resource: Reach 25 Metal Blocks" into ("Metal Blocks", 25)."""
    match = re.fullmatch(r"Resource: Reach (\d+) (.+)", name)
    if not match:
        raise ValueError(f"Not a resource milestone: {name}")
    return match.group(2), int(match.group(1))


def resource_chain_blueprints(good: str, threshold: int, faction: str) -> tuple[str, ...]:
    """Every blueprint a milestone for *good* requires, materials included."""
    buildings, materials = RESOURCE_CHAINS[faction][good]
    required = list(buildings)
    if good in LIQUID_GOODS and threshold >= LARGE_LIQUID_THRESHOLD:
        required.append("Medium Tank")
        materials = materials + ("gears",)
    if "gears" in materials or "metal" in materials or "treated" in materials:
        required += ["Gear Workshop", "Forester"]
    if "metal" in materials:
        required += ["Smelter"] + (["Scavenger Flag"] if faction == "Folktails" else [])
    if "treated" in materials:
        required += ["Tapper's Shack", "Wood Workshop"]
    return tuple(dict.fromkeys(required))


def resource_chain_met(good: str, threshold: int, state: CollectionState, player: int,
                       faction: str = "Folktails") -> bool:
    return has_all(state, player, *resource_chain_blueprints(good, threshold, faction))


def _set_milestone_rules(world, player, mw, faction: str) -> None:
    """Gate milestones by tier so they appear in proper logic spheres.

    Resource milestones are gated by their production chain instead.

    In strict mode, survival milestones also require specific buildings
    (Levee, Floodgate, Stairs, Medium Tank) that are practically needed
    to survive droughts and badtides.
    """
    strict = world.options.logic_difficulty.value == 1

    for loc_name in world.active_milestones:
        loc = mw.get_location(loc_name, player)
        if loc_name.startswith("Resource:"):
            good, threshold = parse_resource_milestone(loc_name)
            required = resource_chain_blueprints(good, threshold, faction)
            loc.access_rule = lambda state, p=player, req=required: has_all(state, p, *req)
            continue

        if loc_name in WONDER_LOCATIONS:
            loc.access_rule = lambda state, p=player, f=faction: can_build_wonder(state, p, f)
            continue

        tier = MILESTONE_TIERS.get(loc_name, 1)

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


# Goods each faction's Wonder needs delivered (WonderInventorySpec in the 1.1
# blueprints). Earth Recultivator takes 500 Extract and 500 Paper, so it also
# needs a badwater source. Earth Repopulator takes Treated Planks and Berries,
# which tier 5 already covers.
WONDER_GOODS: dict[str, tuple[tuple[str, int], ...]] = {
    "Folktails": (("Extract", 500), ("Paper", 500)),
    "IronTeeth": (("Treated Planks", 500), ("Berries", 500)),
}
WONDER_LOCATIONS: frozenset[str] = frozenset({
    "Wonder: Complete Earth Recultivator", "Wonder: Complete Earth Repopulator",
})


def wonder_blueprints(faction: str) -> tuple[str, ...]:
    """Blueprints for the production chains of the Wonder's required goods."""
    required: list[str] = []
    for good, amount in WONDER_GOODS[faction]:
        required += resource_chain_blueprints(good, amount, faction)
    return tuple(dict.fromkeys(required))


def can_build_wonder(state: CollectionState, player: int, faction: str = "Folktails") -> bool:
    return _tier5(state, player, faction) and has_all(state, player, *wonder_blueprints(faction))


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
        if wb <= 20:
            return 3
        if wb <= 35:
            return 4
        return 5
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
            lambda state, p=player, f=faction: can_build_wonder(state, p, f)
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
