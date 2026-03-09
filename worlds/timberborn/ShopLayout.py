"""
Generates the branching-path shop layout at world creation time.

The shop has NUM_PATHS parallel abstract paths (A, B, C, D).  Locations are
shuffled and dealt round-robin into paths, then priced on an exponential ramp
from BASE_SCIENCE to the player's configured max.  The exponential curve keeps
early items cheap (matching vanilla T1 science costs) while ramping steeply
toward endgame.  Tier gates are applied by mapping level ranges to the
existing 5-tier system from Rules.py.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import TimberbornWorld

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BASE_SCIENCE = 30
NUM_PATHS = 4
PATH_LABELS = ["A", "B", "C", "D"]

# Inclusive (start_level, end_level, tier).  Tier 5 has no upper bound.
TIER_LEVEL_BOUNDARIES: list[tuple[int, int, int]] = [
    (0,  7,  1),   # Tier 1 — always open
    (8,  16, 2),   # Tier 2 — Gear Workshop
    (17, 23, 3),   # Tier 3 — + Scavenger Flag + Smelter
    (24, 28, 4),   # Tier 4 — + Tapper's Shack + Wood Workshop
    (29, 999, 5),  # Tier 5 — + Bot Part Factory + Bot Assembler
]


def get_tier_for_level(level: int) -> int:
    """Return the tier number (1-5) for the given shop level."""
    for start, end, tier in TIER_LEVEL_BOUNDARIES:
        if start <= level <= end:
            return tier
    return 5


def generate_shop_layout(
    world: TimberbornWorld,
    science_locations: list[str],
    max_science: int,
) -> list[dict]:
    """
    Shuffle *science_locations* into branching paths and assign prices.

    Returns a list of dicts, one per location::

        {
            "path": "A",            # path label
            "level": 3,             # position within path (0-based)
            "location_name": "Science: Forester",
            "price": 142,           # science cost
            "tier": 1,              # tier gate (1-5)
            "global_pos": 12,       # interleaved ordering across all paths
        }
    """
    shuffled = list(science_locations)
    world.random.shuffle(shuffled)

    # Pin critical survival buildings to the front so they always land in T1
    PRIORITY_LOCATIONS = ["Science: Forester"]
    for loc in reversed(PRIORITY_LOCATIONS):
        if loc in shuffled:
            shuffled.remove(loc)
            shuffled.insert(0, loc)

    # Deal round-robin into paths
    paths: list[list[str]] = [[] for _ in range(NUM_PATHS)]
    for i, loc_name in enumerate(shuffled):
        paths[i % NUM_PATHS].append(loc_name)

    # Build layout with interleaved global positions (level-by-level)
    layout: list[dict] = []
    max_level = max(len(p) for p in paths)
    n = len(science_locations)
    global_pos = 0

    for level in range(max_level):
        for path_idx in range(NUM_PATHS):
            if level >= len(paths[path_idx]):
                continue
            loc_name = paths[path_idx][level]
            t = global_pos / max(n - 1, 1)
            ratio = max_science / BASE_SCIENCE
            price = round(BASE_SCIENCE * (ratio ** t))
            tier = get_tier_for_level(level)
            layout.append({
                "path": PATH_LABELS[path_idx],
                "level": level,
                "location_name": loc_name,
                "price": price,
                "tier": tier,
                "global_pos": global_pos,
            })
            global_pos += 1

    return layout
