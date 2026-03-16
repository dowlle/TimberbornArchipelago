"""
Progressive item chain definitions for the Timberborn APWorld.

Progressive items merge related size-upgrade buildings into a single item
that grants the next tier each time it is received. For example,
"Progressive Platforms" gives Platform on first receipt, Double Platform
on second, Triple Platform on third.

The collect_item() override in __init__.py resolves progressive item
receipts to concrete building names, so Rules.py logic is transparent.
"""
from __future__ import annotations


# ---------------------------------------------------------------------------
# Chain definitions — each maps a progressive item name to its ordered
# sequence of building names (smallest → largest).
# ---------------------------------------------------------------------------

SHARED_PROGRESSIVE_CHAINS: dict[str, tuple[str, ...]] = {
    "Progressive Platforms": (
        "Platform", "Double Platform", "Triple Platform",
    ),
    "Progressive Flood Control": (
        "Floodgate", "Double Floodgate", "Triple Floodgate",
    ),
    "Progressive Bridges": (
        "Suspension Bridge 1x1", "Suspension Bridge 2x1",
        "Suspension Bridge 3x1", "Suspension Bridge 4x1",
        "Suspension Bridge 5x1", "Suspension Bridge 6x1",
    ),
    "Progressive Overhangs": (
        "Overhang 2x1", "Overhang 3x1", "Overhang 4x1",
        "Overhang 5x1", "Overhang 6x1",
    ),
    "Progressive Dynamite": (
        "Dynamite", "Double Dynamite", "Triple Dynamite",
    ),
}

FT_PROGRESSIVE_CHAINS: dict[str, tuple[str, ...]] = {
    "Progressive Housing": (
        "Mini Lodge", "Double Lodge", "Triple Lodge",
    ),
    "Progressive Wind Power": (
        "Wind Turbine", "Large Wind Turbine",
    ),
}

IT_PROGRESSIVE_CHAINS: dict[str, tuple[str, ...]] = {
    # Phase 2: IT housing, tubeways, etc.
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_progressive_chains(
    faction: str,
    enabled: bool,
) -> dict[str, tuple[str, ...]]:
    """Return the active progressive chains for the given faction.

    When *enabled* is False, returns an empty dict (classic mode).
    """
    if not enabled:
        return {}
    chains = dict(SHARED_PROGRESSIVE_CHAINS)
    if faction == "IronTeeth":
        chains.update(IT_PROGRESSIVE_CHAINS)
    else:
        chains.update(FT_PROGRESSIVE_CHAINS)
    return chains


def get_building_to_progressive(
    faction: str,
    enabled: bool,
) -> dict[str, str]:
    """Reverse lookup: building name → progressive item name.

    Only includes buildings that belong to an active progressive chain.
    """
    chains = get_progressive_chains(faction, enabled)
    result: dict[str, str] = {}
    for prog_name, buildings in chains.items():
        for building in buildings:
            result[building] = prog_name
    return result
