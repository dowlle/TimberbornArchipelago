"""
Generates the branching-path shop layout at world creation time.

The shop has NUM_PATHS parallel abstract paths (A, B, C, D).  Buildings are
grouped by their actual construction-material tier, shuffled within each
tier group, then dealt level-by-level into paths.  This ensures buildings
never appear in shop slots earlier than their resource requirements allow.

Prices follow an exponential ramp from BASE_SCIENCE to the player's
configured max.  Tier boundaries are computed dynamically from the actual
building distribution per faction.

Location names use the fixed "Shop: X-NN" slot format (e.g. "Shop: A-01")
so IDs are stable across seeds.  Each entry also carries a ``building_name``
for the client to display.
"""
from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import TimberbornWorld

from .BuildingTiers import get_building_tier

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BASE_SCIENCE = 30
NUM_PATHS = 4
PATH_LABELS = ["A", "B", "C", "D"]


def generate_shop_layout(
    world: TimberbornWorld,
    building_names: list[str],
    max_science: int,
    cost_multiplier: int = 100,
) -> list[dict]:
    """
    Group buildings by resource tier, shuffle within each tier, then deal
    level-by-level into branching paths.

    Returns a list of dicts, one per location::

        {
            "path": "A",            # path label
            "level": 3,             # position within path (0-based internally)
            "slot": 4,              # 1-based slot number (for "Shop: A-04")
            "location_name": "Shop: A-04",
            "building_name": "Forester",
            "price": 142,           # science cost
            "tier": 1,              # tier gate (1-5)
            "global_pos": 12,       # interleaved ordering across all paths
        }
    """
    faction = getattr(world, "faction", "Folktails")

    # 1. Group buildings by their actual construction-material tier
    tier_groups: dict[int, list[str]] = {t: [] for t in range(1, 6)}
    for name in building_names:
        tier = get_building_tier(name, faction)
        tier_groups[tier].append(name)

    # 2. Shuffle each tier group independently
    for tier in tier_groups:
        world.random.shuffle(tier_groups[tier])

    # 3. Pin priority buildings to front of their tier group
    PRIORITY_BUILDINGS = ["Forester"]
    for bld in reversed(PRIORITY_BUILDINGS):
        tier = get_building_tier(bld, faction)
        if bld in tier_groups[tier]:
            tier_groups[tier].remove(bld)
            tier_groups[tier].insert(0, bld)

    # 4. Deal buildings into paths level-by-level, tier by tier.
    #    Only complete levels are used per tier (floor division) so all paths
    #    stay aligned.  Leftover buildings overflow to the next tier (safe:
    #    a lower-tier building in a higher-tier slot is always buildable).
    paths: list[list[str]] = [[] for _ in range(NUM_PATHS)]
    overflow: list[str] = []
    level_tier: dict[int, int] = {}
    current_level = 0

    for tier in range(1, 6):
        pool = tier_groups[tier] + overflow
        if tier < 5:
            # Only fill complete levels to keep paths aligned
            full_levels = len(pool) // NUM_PATHS
            to_deal = full_levels * NUM_PATHS
            overflow = pool[to_deal:]
            pool = pool[:to_deal]
        else:
            # Tier 5 absorbs all remaining (may have incomplete last level)
            overflow = []

        # Record tier for each level
        n_levels = math.ceil(len(pool) / NUM_PATHS) if pool else 0
        for lvl in range(current_level, current_level + n_levels):
            level_tier[lvl] = tier

        # Deal level-by-level
        idx = 0
        for level_offset in range(n_levels):
            for path_idx in range(NUM_PATHS):
                if idx < len(pool):
                    paths[path_idx].append(pool[idx])
                    idx += 1

        current_level += n_levels

    # 6. Build layout with interleaved global positions (level-by-level)
    layout: list[dict] = []
    max_level = max(len(p) for p in paths)
    n = len(building_names)
    global_pos = 0

    for level in range(max_level):
        for path_idx in range(NUM_PATHS):
            if level >= len(paths[path_idx]):
                continue
            building = paths[path_idx][level]
            t = global_pos / max(n - 1, 1)
            ratio = max_science / BASE_SCIENCE
            price = max(1, round(BASE_SCIENCE * (ratio ** t) * cost_multiplier / 100))
            tier = level_tier.get(level, 5)
            slot = level + 1  # 1-based slot number
            loc_name = f"Shop: {PATH_LABELS[path_idx]}-{slot:02d}"
            layout.append({
                "path": PATH_LABELS[path_idx],
                "level": level,
                "slot": slot,
                "location_name": loc_name,
                "building_name": building,
                "price": price,
                "tier": tier,
                "global_pos": global_pos,
            })
            global_pos += 1

    return layout


def get_tier_for_level(level: int) -> int:
    """Return tier for a level. Used by Rules.py for static tier lookup.

    NOTE: The actual tier boundaries are now dynamic per-seed (computed in
    generate_shop_layout).  This function is kept for backward compatibility
    with any code that needs a static estimate.  The layout's own ``tier``
    field is authoritative.
    """
    # Fallback static boundaries (conservative estimates)
    if level <= 11:
        return 1
    if level <= 16:
        return 2
    if level <= 25:
        return 3
    if level <= 31:
        return 4
    return 5
