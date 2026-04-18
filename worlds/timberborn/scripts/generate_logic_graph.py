#!/usr/bin/env python3
"""Generate a progression logic graph from the APWorld data files.

Reads Items.py, BuildingTiers.py, and Rules.py to produce an accurate
DOT/SVG visualization of the tier dependency tree.

Usage:
    python generate_logic_graph.py [--faction folktails|ironteeth] [--output PATH]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add the Archipelago root so we can import the world modules
_SCRIPT_DIR = Path(__file__).resolve().parent
_WORLD_DIR = _SCRIPT_DIR.parent          # worlds/timberborn/
_AP_ROOT = _WORLD_DIR.parent.parent       # ArchipelagoWorld/
sys.path.insert(0, str(_AP_ROOT))

from BaseClasses import ItemClassification
from worlds.timberborn.Items import (
    ALL_FT_BLUEPRINTS, ALL_IT_ONLY_BLUEPRINTS,
    _FT_ONLY_NAMES, _SHARED_NAMES,
)
from worlds.timberborn.BuildingTiers import (
    BUILDING_TIERS, IT_BUILDING_TIERS, IT_SHARED_OVERRIDES, get_building_tier,
)

import graphviz  # type: ignore[import-untyped]

# ── Tier colors ──────────────────────────────────────────────────────────────
TIER_COLORS = {
    1: {"bg": "#e3f2fd", "border": "#1976d2", "font": "#0d47a1"},
    2: {"bg": "#fff3e0", "border": "#f57c00", "font": "#e65100"},
    3: {"bg": "#fce4ec", "border": "#c62828", "font": "#b71c1c"},
    4: {"bg": "#f3e5f5", "border": "#7b1fa2", "font": "#4a148c"},
    5: {"bg": "#fff9c4", "border": "#f9a825", "font": "#f57f17"},
}

TIER_LABELS = {
    1: "Tier 1 — Log & Plank",
    2: "Tier 2 — Gear & Paper",
    3: "Tier 3 — Metal",
    4: "Tier 4 — Treated Plank",
    5: "Tier 5 — Bots & Wonder",
}

# ── Resource chain definitions ───────────────────────────────────────────────
# Each chain: (chain_name, inputs, description)
# inputs are either building names or other chain names (prefixed with "chain:")
RESOURCE_CHAINS = {
    "can_replant_trees": {
        "inputs": ["Forester"],
        "label": "can_replant_trees\n(sustainable wood)",
    },
    "can_produce_gears": {
        "inputs": ["chain:can_replant_trees", "Gear Workshop"],
        "label": "can_produce_gears\n(Gear Workshop + trees)",
    },
    "can_gather_scrap_ft": {
        "inputs": ["Scavenger Flag"],
        "label": "can_gather_scrap\n(Scavenger Flag)",
    },
    "can_gather_scrap_it": {
        "inputs": [],
        "label": "can_gather_scrap\n(free for IT)",
    },
    "can_produce_metal_ft": {
        "inputs": ["chain:can_gather_scrap_ft", "Smelter", "chain:can_produce_gears"],
        "label": "can_produce_metal\n(Smelter + scrap + gears)",
    },
    "can_produce_metal_it": {
        "inputs": ["chain:can_gather_scrap_it", "Smelter", "chain:can_produce_gears"],
        "label": "can_produce_metal\n(Smelter + gears)",
    },
    "can_produce_treated_planks": {
        "inputs": ["Tapper's Shack", "Wood Workshop", "chain:can_produce_gears"],
        "label": "can_produce_treated_planks\n(Tapper + Wood Workshop + gears)",
    },
    "can_build_bots_ft": {
        "inputs": [
            "Bot Part Factory", "Bot Assembler",
            "chain:can_produce_metal_ft", "chain:can_produce_gears",
        ],
        "label": "can_build_bots\n(BPF + Assembler + metal + gears)",
    },
    "can_build_bots_it": {
        "inputs": [
            "Bot Part Factory", "Bot Assembler",
            "chain:can_produce_metal_it", "chain:can_produce_gears",
        ],
        "label": "can_build_bots\n(BPF + Assembler + metal + gears)",
    },
}

# Which chains to use per faction
FACTION_CHAINS = {
    "Folktails": [
        "can_replant_trees", "can_produce_gears", "can_gather_scrap_ft",
        "can_produce_metal_ft", "can_produce_treated_planks", "can_build_bots_ft",
    ],
    "IronTeeth": [
        "can_replant_trees", "can_produce_gears", "can_gather_scrap_it",
        "can_produce_metal_it", "can_produce_treated_planks", "can_build_bots_it",
    ],
}

# Tier gate edges: tier -> list of chains that gate it
TIER_GATES = {
    "Folktails": {
        2: ["can_produce_gears"],
        3: ["can_produce_metal_ft", "can_produce_gears"],
        4: ["can_produce_metal_ft", "can_produce_treated_planks"],
        5: ["can_build_bots_ft", "can_produce_treated_planks"],
    },
    "IronTeeth": {
        2: ["can_produce_gears"],
        3: ["can_produce_metal_it", "can_produce_gears"],
        4: ["can_produce_metal_it", "can_produce_treated_planks"],
        5: ["can_build_bots_it", "can_produce_treated_planks"],
    },
}

# Free buildings (always available, not in the item pool)
FREE_BUILDINGS = [
    "Lumberjack Flag", "Water Pump", "Farm", "Small Tank",
    "Stockpile", "Path", "Inventor", "Water Wheel",
    "Power Wheel", "Lumber Mill",
]

IT_FREE_BUILDINGS = [
    "Lumberjack Flag", "Deep Water Pump", "Farmhouse", "Fermenter",
    "Small Industrial Pile", "Large Industrial Pile", "Path",
    "Inventor", "Compact Water Wheel", "Large Power Wheel",
    "Industrial Lumber Mill", "Barrack", "Breeding Pod",
    "Scavenger Flag",
]

# Milestones per tier
MILESTONE_TIERS: dict[int, list[str]] = {
    1: [
        "First Beaver Born", "First Beaver Grown Up",
        "Reach 15 Beavers", "Well-being Lv5", "Survive 1st Drought",
    ],
    2: [
        "Reach 25 Beavers", "Reach 50 Beavers",
        "Well-being Lv10", "Survive 5 Droughts", "Survive 1st Badtide",
    ],
    3: [
        "Reach 100 Beavers", "Well-being Lv15",
        "Survive 10 Droughts", "Survive 5 Badtides",
    ],
    4: [
        "Reach 200 Beavers", "Well-being Lv20", "Survive 10 Badtides",
    ],
    5: ["Complete Wonder"],
}


def _get_faction_buildings(
    faction: str,
) -> list[tuple[str, ItemClassification, int]]:
    """Return (name, classification, tier) for all buildings in the faction."""
    results: list[tuple[str, ItemClassification, int]] = []
    if faction == "IronTeeth":
        for name, cls in ALL_FT_BLUEPRINTS:
            if name in _SHARED_NAMES:
                tier = get_building_tier(name, "IronTeeth")
                results.append((name, cls, tier))
        for name, cls in ALL_IT_ONLY_BLUEPRINTS:
            tier = get_building_tier(name, "IronTeeth")
            results.append((name, cls, tier))
    else:
        for name, cls in ALL_FT_BLUEPRINTS:
            tier = get_building_tier(name, "Folktails")
            results.append((name, cls, tier))
    return results


def _sanitize_id(name: str) -> str:
    """Make a graphviz-safe node ID from a building name."""
    return name.replace(" ", "_").replace("'", "").replace(":", "_").replace("-", "_")


def build_graph(faction: str) -> graphviz.Digraph:
    """Build the full progression logic graph for the given faction."""
    dot = graphviz.Digraph(
        name=f"Timberborn Progression ({faction})",
        format="svg",
        engine="dot",
    )
    dot.attr(rankdir="TB", fontname="Helvetica", fontsize="11", bgcolor="white")
    dot.attr("node", fontname="Helvetica", fontsize="10")
    dot.attr("edge", color="#666666", arrowsize="0.7")

    # ── Free buildings subgraph ──────────────────────────────────────────
    free_list = IT_FREE_BUILDINGS if faction == "IronTeeth" else FREE_BUILDINGS
    with dot.subgraph(name="cluster_free") as s:
        s.attr(
            label="Free Buildings (always available)",
            style="filled", fillcolor="#e8f5e9", color="#4caf50",
            fontcolor="#1b5e20", fontsize="12",
        )
        for b in free_list:
            s.node(
                _sanitize_id(b), b,
                shape="box", style="filled,rounded",
                fillcolor="#c8e6c9", color="#4caf50", fontcolor="#1b5e20",
            )

    # ── Building nodes grouped by tier ───────────────────────────────────
    buildings = _get_faction_buildings(faction)
    tiers: dict[int, list[tuple[str, ItemClassification]]] = {}
    for name, cls, tier in buildings:
        tiers.setdefault(tier, []).append((name, cls))

    for tier_num in sorted(tiers.keys()):
        colors = TIER_COLORS[tier_num]
        label = TIER_LABELS[tier_num]
        with dot.subgraph(name=f"cluster_t{tier_num}") as s:
            s.attr(
                label=label, style="filled",
                fillcolor=colors["bg"], color=colors["border"],
                fontcolor=colors["font"], fontsize="12",
            )
            # Add milestone sidebar
            milestones = MILESTONE_TIERS.get(tier_num, [])
            if milestones:
                ms_label = "\\l".join(milestones) + "\\l"
                s.node(
                    f"milestones_t{tier_num}",
                    f"Milestones:\\l{ms_label}",
                    shape="note", style="filled",
                    fillcolor="#fafafa", color="#bdbdbd",
                    fontsize="8", fontcolor="#616161",
                )

            for name, cls in tiers[tier_num]:
                nid = _sanitize_id(name)
                if cls == ItemClassification.progression:
                    s.node(
                        nid, name,
                        shape="box", style="filled,bold",
                        fillcolor=colors["bg"], color=colors["border"],
                        fontcolor=colors["font"], penwidth="2.5",
                    )
                elif cls == ItemClassification.useful:
                    s.node(
                        nid, name,
                        shape="box", style="filled,rounded",
                        fillcolor=colors["bg"], color=colors["border"],
                        fontcolor=colors["font"], penwidth="1",
                    )
                else:  # filler
                    s.node(
                        nid, name,
                        shape="box", style="filled,dashed,rounded",
                        fillcolor="#fafafa", color="#bdbdbd",
                        fontcolor="#9e9e9e", penwidth="1",
                    )

    # ── Resource chain diamond nodes ─────────────────────────────────────
    active_chains = FACTION_CHAINS[faction]
    for chain_name in active_chains:
        chain = RESOURCE_CHAINS[chain_name]
        dot.node(
            chain_name, chain["label"],
            shape="diamond", style="filled",
            fillcolor="#fffde7", color="#fbc02d", fontcolor="#827717",
            fontsize="9",
        )

    # ── Edges: building → chain ──────────────────────────────────────────
    for chain_name in active_chains:
        chain = RESOURCE_CHAINS[chain_name]
        for inp in chain["inputs"]:
            if inp.startswith("chain:"):
                src = inp[len("chain:"):]
                dot.edge(src, chain_name, style="dashed", color="#fbc02d")
            else:
                dot.edge(_sanitize_id(inp), chain_name, color="#333333")

    # ── Edges: chain → tier subgraph (via invisible anchor) ──────────────
    gates = TIER_GATES[faction]
    for tier_num, chain_list in gates.items():
        # Pick a representative node in the tier to point to
        if tier_num in tiers and tiers[tier_num]:
            first_prog = None
            for name, cls in tiers[tier_num]:
                if cls == ItemClassification.progression:
                    first_prog = name
                    break
            target = first_prog or tiers[tier_num][0][0]
            for chain_name in chain_list:
                dot.edge(
                    chain_name, _sanitize_id(target),
                    style="bold", color="#333333",
                    lhead=f"cluster_t{tier_num}",
                )

    # ── Wonder node ──────────────────────────────────────────────────────
    if faction == "IronTeeth":
        wonder_name = "Earth Repopulator"
    else:
        wonder_name = "Earth Recultivator"
    dot.node(
        "wonder", f"🏆 {wonder_name}\n(Wonder)",
        shape="doubleoctagon", style="filled",
        fillcolor="#fff9c4", color="#f9a825", fontcolor="#f57f17",
        fontsize="12", penwidth="3",
    )
    # Connect T5 chain to wonder
    bot_chain = "can_build_bots_ft" if faction == "Folktails" else "can_build_bots_it"
    dot.edge(bot_chain, "wonder", style="bold", color="#f9a825", penwidth="2")

    return dot


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Timberborn progression logic graph")
    parser.add_argument(
        "--faction", choices=["folktails", "ironteeth"], default="folktails",
        help="Which faction to generate the graph for (default: folktails)",
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Output path (without extension). Default: docs/logic_graph",
    )
    args = parser.parse_args()

    faction = "IronTeeth" if args.faction == "ironteeth" else "Folktails"

    # Default output to docs/ in the repo root
    if args.output:
        out_path = Path(args.output)
    else:
        repo_root = _AP_ROOT.parent  # TimberbornAP/
        out_path = repo_root / "docs" / "logic_graph"

    dot = build_graph(faction)

    # Save .dot source
    dot_path = out_path.with_suffix(".dot")
    dot_path.parent.mkdir(parents=True, exist_ok=True)
    dot_path.write_text(dot.source, encoding="utf-8")
    print(f"DOT source: {dot_path}")

    # Render SVG
    try:
        rendered = dot.render(
            filename=str(out_path),
            cleanup=False,  # keep the .dot file
        )
        print(f"SVG output: {rendered}")
    except graphviz.backend.execute.ExecutableNotFound:
        print(
            "WARNING: Graphviz system binary (dot) not found.\n"
            "Install it with: winget install --id Graphviz.Graphviz\n"
            f"DOT file saved to {dot_path} — render manually with:\n"
            f"  dot -Tsvg {dot_path} -o {out_path.with_suffix('.svg')}",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
