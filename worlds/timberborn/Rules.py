import re

from BaseClasses import CollectionState, LocationProgressType
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

# Folktails Bot Chassis costs Biofuel, which only the Refinery makes.
BOT_BLUEPRINTS: dict[str, tuple[str, ...]] = {
    "Folktails": ("Bot Part Factory", "Bot Assembler", "Refinery"),
    "IronTeeth": ("Bot Part Factory", "Bot Assembler"),
}


def can_build_bots(state: CollectionState, player: int, faction: str = "Folktails") -> bool:
    return (has_all(state, player, *BOT_BLUEPRINTS[faction])
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
    world.placement_tiers = placement_tiers(
        faction, world._progressive_chains, world.shop_layout,
        set(mw.early_items[player]) | set(mw.local_early_items[player]))
    _set_tier_placement_rules(world, player, mw)


# ---------------------------------------------------------------------------
# Tier-gated placement (#13)
#
# A Timberborn blueprint may only be placed in a Timberborn shop slot whose
# tier is at least the blueprint's own tier, so a Smelter never sits in a
# tier 1 slot that is reachable long before metal. This is an item rule, not
# an access rule: it limits where fill puts items and never changes what a
# location needs. A progressive item counts as its first step. Items without a
# tier (packages, traps, boosts, scouts, skips), other games' items and
# Timberborn blueprints in other games' locations or in milestones are
# unrestricted. Starting items are precollected, never placed.
#
# The allowed slot tier comes from what the item is needed for, not only from
# its construction materials. Two cases lower it:
# - A blueprint that a shop slot of tier N requires (the tier keys such as the
#   Smelter for tier 3, and the prerequisites of the building shown in that
#   slot) may sit one tier lower, in N - 1. Otherwise it could never be in its
#   own shop, and a seed with few milestones has nowhere to put it.
# - A blueprint forced into sphere 1 (Force Early Items) may sit in tier 1,
#   because the tier 1 slots are sphere 1.
# ---------------------------------------------------------------------------

def tier_blueprints(tier: int, faction: str = "Folktails") -> tuple[str, ...]:
    """Blueprints that _tier_predicate(tier) requires."""
    required: list[str] = []
    if tier >= 2:
        required += ["Gear Workshop", "Forester"]
    if tier >= 3:
        required += ["Smelter"] + (["Scavenger Flag"] if faction == "Folktails" else [])
    if tier >= 4:
        required += ["Tapper's Shack", "Wood Workshop"]
    if tier >= 5:
        required += list(BOT_BLUEPRINTS[faction])
    return tuple(dict.fromkeys(required))


def slot_required_blueprints(entry: dict, faction: str) -> tuple[str, ...]:
    """Blueprints a shop slot's access rule requires (slot tier and its building)."""
    building = entry["building_name"]
    required = (list(tier_blueprints(entry["tier"], faction))
                + list(tier_blueprints(get_building_tier(building, faction), faction))
                + list(building_prerequisite_blueprints(building, faction)))
    return tuple(dict.fromkeys(required))


def placement_tiers(faction: str, progressive_chains: dict[str, tuple[str, ...]] | None,
                    shop_layout: list[dict] | None = None,
                    early_items: set[str] | frozenset[str] = frozenset()) -> dict[str, int]:
    """Placement tier of every blueprint item of a faction, progressive items included."""
    from .Items import get_building_names
    item_of = {name: f"Blueprint: {name}" for name in get_building_names(faction)}
    for prog_name, chain in (progressive_chains or {}).items():
        for building in chain:
            item_of[building] = prog_name
    tiers = {f"Blueprint: {name}": get_building_tier(name, faction)
             for name in get_building_names(faction)}
    for prog_name, chain in (progressive_chains or {}).items():
        tiers[prog_name] = get_building_tier(chain[0], faction)
        for building in chain:
            tiers.pop(f"Blueprint: {building}", None)
    # Needed to open a slot of tier N: allowed from tier N - 1.
    for entry in shop_layout or ():
        for building in slot_required_blueprints(entry, faction):
            name = item_of.get(building)
            if name in tiers:
                tiers[name] = max(1, min(tiers[name], entry["tier"] - 1))
    # Forced into sphere 1: allowed in tier 1.
    for name in early_items:
        if name in tiers:
            tiers[name] = 1
    return tiers


def item_placement_tier(item, multiworld) -> int:
    """Tier an item needs from a Timberborn shop slot; 0 when unrestricted."""
    if item.game != "Timberborn":
        return 0
    tiers = getattr(multiworld.worlds[item.player], "placement_tiers", None) or {}
    return tiers.get(item.name, 0)


class ShopCapacity:
    """Keeps enough high-tier shop slots free for the blueprints that need them.

    Slot tiers are nested: a blueprint of tier t fits every slot of tier t or
    higher. Fill may put a lower-tier or untiered item into a high slot only
    while, for every tier t the slot covers above the item's own tier, the
    free slots of tier t or higher (after this placement) still number at
    least the unplaced blueprints that need tier t or higher. That is Hall's
    condition for nested sets, so the remaining blueprints can always be
    placed. It counts every unplaced blueprint as needing this shop, which is
    safe: a blueprint placed elsewhere only frees room.

    Two kinds of slot are special, because Archipelago fills them in its own
    order:
    - Excluded slots never hold a blueprint: Archipelago fills them only with
      filler, before the useful items are placed. They are not counted as
      free room, and they take any item their tier allows. Counting them made
      every excluded tier 2+ slot refuse all filler while useful blueprints
      were still waiting, and generation failed.
    - Priority slots are filled with progression first, while the useful
      blueprints are still waiting. A progression item there only keeps room
      for the progression blueprints. Useful blueprints still fit any
      milestone, any other game's location or any shop slot of their tier. A
      seed with no milestones and many late priority slots runs out of room
      either way; it failed before this rule too, in the priority fill.
    """

    def __init__(self, world, slots_by_tier: dict[int, list]):
        self.world = world
        self.slots_by_tier = slots_by_tier
        self._restricted: list[tuple[object, int]] | None = None

    def restricted_items(self) -> list[tuple[object, int]]:
        if self._restricted is None:
            tiers = self.world.placement_tiers or {}
            self._restricted = [
                (item, tiers[item.name]) for item in self.world.multiworld.itempool
                if item.player == self.world.player and item.game == "Timberborn"
                and tiers.get(item.name, 0) > 1
            ]
        return self._restricted

    def allows(self, item, slot_tier: int, location=None) -> bool:
        item_tier = item_placement_tier(item, self.world.multiworld)
        if item_tier > slot_tier:
            return False
        progress_type = getattr(location, "progress_type", LocationProgressType.DEFAULT)
        if progress_type == LocationProgressType.EXCLUDED:
            return True
        if item_tier == slot_tier or slot_tier <= 1:
            return True
        free = [0] * 7
        for tier, slots in self.slots_by_tier.items():
            free[tier] = sum(1 for slot in slots if slot.item is None
                             and slot.progress_type != LocationProgressType.EXCLUDED)
        progression_only = item.advancement and progress_type == LocationProgressType.PRIORITY
        need = [0] * 7
        for placed, tier in self.restricted_items():
            if placed.location is None and (placed.advancement or not progression_only):
                need[tier] += 1
        free_at_least = need_at_least = 0
        for tier in range(5, max(item_tier, 1), -1):
            free_at_least += free[tier]
            need_at_least += need[tier]
            if tier <= slot_tier and free_at_least - 1 < need_at_least:
                return False
        return True


def _set_tier_placement_rules(world, player, mw) -> None:
    slots_by_tier: dict[int, list] = {tier: [] for tier in range(1, 6)}
    for entry in world.shop_layout:
        slots_by_tier[entry["tier"]].append(mw.get_location(entry["location_name"], player))
    world.shop_capacity = capacity = ShopCapacity(world, slots_by_tier)
    for entry in world.shop_layout:
        loc = mw.get_location(entry["location_name"], player)
        original = loc.item_rule
        loc.item_rule = lambda item, t=entry["tier"], orig=original, c=capacity, l=loc: (
            c.allows(item, t, l) and orig(item)
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

    Resource milestones are gated by their production chain instead, the
    Wonder by its goods chains, and survival milestones also need the survival
    predicates for their hazard level.
    """
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
        survival = SURVIVAL_MILESTONE_LEVELS.get(loc_name)

        loc.access_rule = lambda state, p=player, t=tier, f=faction, sv=survival: (
            _tier_predicate(t, state, p, f)
            and (sv is None or can_survive(sv[0], sv[1], state, p, f))
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
    """Construction needs Gears, Treated Planks and Metal Blocks (tier 4), then the
    wonder's goods chains. No bots. A long goal, so it also needs survival."""
    return (_tier4(state, player, faction) and has_all(state, player, *wonder_blueprints(faction))
            and can_survive_long_game(state, player, faction))


# ---------------------------------------------------------------------------
# Survival predicates (Goals and badtide survival review, 2026-09-27)
#
# A hazard is survived with water control and stored water early, then
# automation, cures and bigger storage, then a clean side channel with
# mechanical pumps and backup power. Each tier is a list of requirement
# groups; a group is met when any one of its buildings can be built: the
# blueprint, its material tier and its prerequisites (the Iron Teeth cure,
# the Decontamination Pod, consumes Extract). Tiers are cumulative.
# ---------------------------------------------------------------------------
SURVIVAL_EARLY, SURVIVAL_MID, SURVIVAL_LATE = 1, 2, 3

_DROUGHT_TIERS: dict[str, dict[int, tuple[tuple[str, ...], ...]]] = {
    "Folktails": {
        SURVIVAL_EARLY: (("Levee",), ("Floodgate",), ("Stairs",)),
        SURVIVAL_MID:   (("Medium Tank",), ("Double Floodgate",), ("Platform",)),
        SURVIVAL_LATE:  (("Large Tank", "Triple Floodgate"),
                         ("Gravity Battery", "Geothermal Engine", "Wind Turbine")),
    },
    "IronTeeth": {
        SURVIVAL_EARLY: (("Levee",), ("Floodgate",), ("Stairs",)),
        SURVIVAL_MID:   (("Medium Tank",), ("Double Floodgate",), ("Platform",)),
        SURVIVAL_LATE:  (("Large Tank", "Triple Floodgate"),
                         ("Gravity Battery", "Geothermal Engine", "Steam Engine")),
    },
}

_BADTIDE_TIERS: dict[str, dict[int, tuple[tuple[str, ...], ...]]] = {
    "Folktails": {
        SURVIVAL_EARLY: (("Floodgate",), ("Levee",), ("Medium Tank",)),
        SURVIVAL_MID:   (("Double Floodgate",), ("Contamination Sensor",),
                         ("Herbalist",), ("Paper Mill",)),
        SURVIVAL_LATE:  (("Large Tank",), ("Mechanical Fluid Pump", "Compact Mechanical Pump")),
    },
    "IronTeeth": {
        SURVIVAL_EARLY: (("Floodgate",), ("Levee",), ("Medium Tank",)),
        SURVIVAL_MID:   (("Double Floodgate",), ("Contamination Sensor",),
                         ("Decontamination Pod",)),
        SURVIVAL_LATE:  (("Large Tank",), ("Large Water Wheel",),
                         ("Deep Mechanical Fluid Pump", "Compact Mechanical Pump")),
    },
}


def survival_groups(kind: str, level: int, faction: str) -> tuple[tuple[str, ...], ...]:
    """Requirement groups for surviving droughts or badtides at a level (cumulative)."""
    table = (_DROUGHT_TIERS if kind == "drought" else _BADTIDE_TIERS)[faction]
    groups: list[tuple[str, ...]] = []
    for lvl in range(SURVIVAL_EARLY, level + 1):
        groups += table[lvl]
    return tuple(groups)


def survival_blueprints(faction: str) -> set[str]:
    """Every blueprint any survival predicate names (all must be progression)."""
    names: set[str] = set()
    for table in (_DROUGHT_TIERS, _BADTIDE_TIERS):
        for groups in table[faction].values():
            for group in groups:
                for building in group:
                    names.add(building)
                    names.update(building_prerequisite_blueprints(building, faction))
    return names


def drought_level(count: int) -> int:
    """Survival level needed for *count* droughts: early 1-5, mid 6-15, late 16+."""
    return SURVIVAL_EARLY if count <= 5 else SURVIVAL_MID if count <= 15 else SURVIVAL_LATE


def badtide_level(count: int) -> int:
    """Survival level needed for *count* badtides: early 1-3, mid 4-10, late 11+."""
    return SURVIVAL_EARLY if count <= 3 else SURVIVAL_MID if count <= 10 else SURVIVAL_LATE


def can_build(building: str, state: CollectionState, player: int, faction: str = "Folktails") -> bool:
    return (has(state, player, building)
            and _tier_predicate(get_building_tier(building, faction), state, player, faction)
            and has_building_prerequisites(building, state, player, faction))


def can_survive(kind: str, level: int, state: CollectionState, player: int,
                faction: str = "Folktails") -> bool:
    return all(any(can_build(b, state, player, faction) for b in group)
               for group in survival_groups(kind, level, faction))


def can_survive_long_game(state: CollectionState, player: int, faction: str = "Folktails") -> bool:
    """Long goals take many cycles: mid drought and early badtide survival."""
    return (can_survive("drought", SURVIVAL_MID, state, player, faction)
            and can_survive("badtide", SURVIVAL_EARLY, state, player, faction))


# Survival milestones: kind and level. Per the review, the three milestones of
# each family map to the three levels (1st early, 5 mid, 10 late); the goals
# pick the level from their threshold with drought_level / badtide_level.
SURVIVAL_MILESTONE_LEVELS: dict[str, tuple[str, int]] = {
    "Survival: Survive 1st Drought":  ("drought", SURVIVAL_EARLY),
    "Survival: Survive 5 Droughts":   ("drought", SURVIVAL_MID),
    "Survival: Survive 10 Droughts":  ("drought", SURVIVAL_LATE),
    "Survival: Survive 1st Badtide":  ("badtide", SURVIVAL_EARLY),
    "Survival: Survive 5 Badtides":   ("badtide", SURVIVAL_MID),
    "Survival: Survive 10 Badtides":  ("badtide", SURVIVAL_LATE),
}

# Long-goal thresholds from which a goal needs can_survive_long_game.
LONG_POPULATION_GOAL = 100
LONG_WELLBEING_GOAL = 20
LONG_WATER_STORAGE_GOAL = 5000


def goal_survival(goal_name: str, world) -> tuple[tuple[str, int], ...]:
    """Survival (kind, level) pairs a client-tracked goal needs besides its tier."""
    options = world.options
    if goal_name == "Droughts":
        return (("drought", drought_level(options.drought_cycles_goal.value)),)
    if goal_name == "Badtides":
        return (("badtide", badtide_level(options.badtide_cycles_goal.value)),)
    long_goal = (
        (goal_name == "Population" and options.population_goal.value >= LONG_POPULATION_GOAL)
        or (goal_name == "Well-being" and options.wellbeing_goal.value >= LONG_WELLBEING_GOAL)
        or (goal_name == "Water Storage" and options.water_storage_goal.value >= LONG_WATER_STORAGE_GOAL)
    )
    if long_goal:
        return (("drought", SURVIVAL_MID), ("badtide", SURVIVAL_EARLY))
    return ()


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
        survival = goal_survival(goal_name, world)
        event_loc = mw.get_location(event, player)
        event_loc.access_rule = lambda state, p=player, t=tier, f=faction, sv=survival: (
            _tier_predicate(t, state, p, f)
            and all(can_survive(kind, level, state, p, f) for kind, level in sv)
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
