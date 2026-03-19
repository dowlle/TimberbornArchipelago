"""
Generate Mermaid flowcharts of building unlock dependencies from blueprint JSONs.

Outputs two faction-specific flowcharts (Folktails and Iron Teeth) showing
which materials each building requires, grouped by material tier.

Usage:
    python extract_flowchart.py [--output PATH]

Default output: docs/Timberborn — Building Unlock Flowchart (by Materials).md
"""

from __future__ import annotations

import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ITEMS_PY = os.path.join(SCRIPT_DIR, "..", "Items.py")
BLUEPRINTS_DIR = os.path.normpath(os.path.join(
    SCRIPT_DIR, "..", "..", "..", "..",
    "timberborn-modding", "Assets", "Tools", "ImportedAssets",
    "Editor", "Resources", "Buildings"
))
DOCS_DIR = os.path.normpath(os.path.join(
    SCRIPT_DIR, "..", "..", "..", "..", "docs"
))

# ---------------------------------------------------------------------------
# Material -> tier mapping (same as extract_building_tiers.py)
# ---------------------------------------------------------------------------
MATERIAL_TIER: dict[str, int] = {
    "Log": 1, "Plank": 1,
    "Gear": 2, "Paper": 2, "PineResin": 2,
    "MetalBlock": 3, "ScrapMetal": 3,
    "TreatedPlank": 4, "Dirt": 4, "Extract": 4, "Explosives": 4,
    "MetalPart": 5, "Grease": 5,
}

TIER_LABELS = {
    1: "Tier 1 — Logs & Planks",
    2: "Tier 2 — Gears & Paper",
    3: "Tier 3 — Metal & Scrap",
    4: "Tier 4 — Treated Planks & Explosives",
    5: "Tier 5 — Metal Parts & Grease",
}

# Buildings that PRODUCE resources (shown in the resource chain)
PRODUCERS = {
    "Lumberjack Flag": "Log",
    "Lumber Mill": "Plank",
    "Forester": None,  # grows trees, not a direct output
    "Gear Workshop": "Gear",
    "Paper Mill": "Paper",
    "Tapper's Shack": "PineResin",
    "Wood Workshop": "TreatedPlank",
    "Smelter": "MetalBlock",
    "Scavenger Flag": "ScrapMetal",
    "Bot Part Factory": "MetalPart",
    "Explosives Factory": "Explosives",
    "Refinery": "Extract",
    "Grease Factory": "Grease",
    "Metalsmith": "MetalBlock",  # IT version
}


# ---------------------------------------------------------------------------
# Reused from extract_building_tiers.py
# ---------------------------------------------------------------------------

def parse_building_names_from_items() -> tuple[list[str], list[str], set[str]]:
    with open(ITEMS_PY, "r", encoding="utf-8") as f:
        source = f.read()

    name_pattern = re.compile(r'\("([^"]+)",\s+ItemClassification\.\w+\)')

    def extract_list_names(var_name: str) -> list[str]:
        pattern = rf'{var_name}\s*(?::.*?)?\s*=\s*\[(.*?)\]'
        match = re.search(pattern, source, re.DOTALL)
        if not match:
            return []
        return name_pattern.findall(match.group(1))

    ft_categories = [
        "WOOD_BLUEPRINTS", "FOOD_BLUEPRINTS", "HOUSING_BLUEPRINTS",
        "STORAGE_BLUEPRINTS", "WATER_BLUEPRINTS", "LANDSCAPING_BLUEPRINTS",
        "METAL_BLUEPRINTS", "POWER_BLUEPRINTS", "SCIENCE_BLUEPRINTS",
        "DISTRICT_BLUEPRINTS", "WELLBEING_BLUEPRINTS", "PATH_BLUEPRINTS",
        "AUTOMATION_BLUEPRINTS", "DECORATION_BLUEPRINTS", "FT_MONUMENT_BLUEPRINTS",
    ]
    all_ft_names = []
    for cat in ft_categories:
        all_ft_names.extend(extract_list_names(cat))

    it_categories = [
        "IT_WOOD_BLUEPRINTS", "IT_FOOD_BLUEPRINTS", "IT_HOUSING_BLUEPRINTS",
        "IT_STORAGE_BLUEPRINTS", "IT_WATER_BLUEPRINTS", "IT_LANDSCAPING_BLUEPRINTS",
        "IT_METAL_BLUEPRINTS", "IT_POWER_BLUEPRINTS", "IT_SCIENCE_BLUEPRINTS",
        "IT_WELLBEING_BLUEPRINTS", "IT_PATH_BLUEPRINTS", "IT_DECORATION_BLUEPRINTS",
        "IT_MONUMENT_BLUEPRINTS",
    ]
    it_only_names = []
    for cat in it_categories:
        it_only_names.extend(extract_list_names(cat))

    ft_only_match = re.search(r'_FT_ONLY_NAMES:\s*set\[str\]\s*=\s*\{(.*?)\}', source, re.DOTALL)
    ft_only_names: set[str] = set()
    if ft_only_match:
        ft_only_names = set(re.findall(r'"([^"]+)"', ft_only_match.group(1)))

    return all_ft_names, it_only_names, ft_only_names


def display_name_to_dirname(name: str) -> str:
    return re.sub(r"[\s']+", "", name)


def find_blueprint(dirname: str, faction: str) -> str | None:
    for category in os.listdir(BLUEPRINTS_DIR):
        cat_path = os.path.join(BLUEPRINTS_DIR, category)
        if not os.path.isdir(cat_path):
            continue
        building_dir = os.path.join(cat_path, dirname)
        if os.path.isdir(building_dir):
            json_name = f"{dirname}.{faction}.blueprint.json"
            json_path = os.path.join(building_dir, json_name)
            if os.path.isfile(json_path):
                return json_path
    return None


def extract_building_cost(json_path: str) -> list[dict]:
    with open(json_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    return data.get("BuildingSpec", {}).get("BuildingCost", [])


def get_tier_from_costs(costs: list[dict]) -> int:
    if not costs:
        return 1
    max_tier = 1
    for cost in costs:
        tier = MATERIAL_TIER.get(cost.get("Id", ""), 0)
        max_tier = max(max_tier, tier)
    return max_tier


# ---------------------------------------------------------------------------
# Building data collection
# ---------------------------------------------------------------------------

def collect_building_data(names: list[str], faction: str) -> list[dict]:
    """Collect building name, costs, and tier for a list of buildings."""
    buildings = []
    for name in names:
        dirname = display_name_to_dirname(name)
        json_path = find_blueprint(dirname, faction)
        if json_path is None:
            buildings.append({"name": name, "costs": [], "tier": 1})
            continue
        costs = extract_building_cost(json_path)
        tier = get_tier_from_costs(costs)
        buildings.append({"name": name, "costs": costs, "tier": tier})
    return buildings


def sanitize_id(name: str) -> str:
    """Convert building name to a valid Mermaid node ID."""
    return re.sub(r"[^a-zA-Z0-9]", "", name)


def format_cost(costs: list[dict]) -> str:
    """Format building cost as a compact string."""
    if not costs:
        return "Free"
    parts = []
    for c in costs:
        mat = c["Id"]
        amt = c["Amount"]
        parts.append(f"{mat}:{amt}")
    return ", ".join(parts)


# ---------------------------------------------------------------------------
# Progression / notable building classification
# ---------------------------------------------------------------------------

# Buildings shown individually (progression-relevant or notable)
PROGRESSION_BUILDINGS = {
    # Resource producers (always shown)
    *PRODUCERS.keys(),
    # Key infrastructure
    "Forester", "Gear Workshop", "Paper Mill", "Tapper's Shack", "Wood Workshop",
    "Smelter", "Scavenger Flag", "Bot Part Factory", "Bot Assembler",
    "Explosives Factory", "Refinery", "Metalsmith", "Grease Factory",
    # Power
    "Wind Turbine", "Large Wind Turbine", "Geothermal Engine", "Gravity Battery",
    "Large Water Wheel", "Steam Engine",
    # Water
    "Levee", "Floodgate", "Large Tank", "Medium Tank", "Aquifer Drill",
    "Badwater Dome", "Centrifuge", "Large Water Pump", "Mechanical Fluid Pump",
    "Deep Badwater Pump", "Deep Mechanical Fluid Pump",
    # Food chain
    "Bakery", "Gristmill", "Beehive", "Aquatic Farmhouse",
    "Food Factory", "Oil Press", "Hydroponic Garden", "Coffee Brewery",
    # Housing
    "Mini Lodge", "Double Lodge", "Triple Lodge",
    "Rowhouse", "Large Barrack", "Large Rowhouse",
    # Science
    "Observatory", "Printing Press", "Charging Station", "Numbercruncher",
    "Control Tower",
    # Mining / terraforming
    "Mine", "Efficient Mine", "Dynamite",
    # Essential paths
    "Stairs", "Platform", "Spiral Stairs",
    # Wellbeing key
    "Shower", "Double Shower",
    # Monuments
    "Farmer Monument", "Brazier of Bonding", "Fountain of Joy",
    "Laborer Monument", "Flame of Unity", "Tribute to Ingenuity",
}

# Category labels for collapsed "other" buildings
CATEGORY_LABELS = {
    1: "Decoration, roofs, bridges, fences, etc.",
    2: "Automation sensors, scarecrow, etc.",
    3: "Ziplines, metal platforms, overhangs, automation, etc.",
    4: "Banners, advanced automation, tunnels, etc.",
    5: "Fences, decorations, etc.",
}


# ---------------------------------------------------------------------------
# Mermaid generation
# ---------------------------------------------------------------------------

def generate_mermaid(buildings: list[dict], faction: str, faction_label: str) -> str:
    """Generate a Mermaid flowchart for one faction.

    Progression buildings are shown individually. Minor buildings (decorations,
    roofs, etc.) are collapsed into a single summary node per tier.
    Tiers are stacked vertically with explicit connections between them.
    """
    lines = ["flowchart TD"]

    # Group by tier
    tiers: dict[int, list[dict]] = {t: [] for t in range(1, 6)}
    for b in buildings:
        tiers[b["tier"]].append(b)

    # --- Tier subgraphs with progression buildings + collapsed others ---
    for tier in range(1, 6):
        tier_buildings = tiers[tier]
        if not tier_buildings:
            continue

        label = TIER_LABELS[tier]
        lines.append("")
        lines.append(f'    subgraph t{tier}["{label}"]')

        progression = []
        other = []
        for b in sorted(tier_buildings, key=lambda x: x["name"]):
            if b["name"] in PROGRESSION_BUILDINGS:
                progression.append(b)
            else:
                other.append(b)

        # Show progression buildings individually
        for b in progression:
            nid = sanitize_id(b["name"])
            display = b["name"].replace('"', "'")
            cost_str = format_cost(b["costs"])
            product = PRODUCERS.get(b["name"])
            if product:
                lines.append(f'        {nid}["{display}<br>➜ {product}<br>({cost_str})"]')
            elif b["name"] == "Forester":
                lines.append(f'        {nid}["{display}<br>🌱 sustains trees<br>({cost_str})"]')
            else:
                lines.append(f'        {nid}["{display}<br>({cost_str})"]')

        # Collapse non-progression buildings into one summary node
        if other:
            cat_label = CATEGORY_LABELS.get(tier, "Other buildings")
            other_names = [b["name"] for b in other]
            # Show up to 4 names as examples, then "..."
            if len(other_names) <= 4:
                examples = ", ".join(other_names)
            else:
                examples = ", ".join(other_names[:4]) + f", ... +{len(other_names) - 4} more"
            lines.append(f'        t{tier}_other["{len(other)} other buildings<br>{cat_label}<br>({examples})"]')

        lines.append("    end")

    # --- Resource chain connections (between tiers) ---
    lines.append("")
    lines.append("    %% Resource production chain")

    # T1 internal: Forester sustains trees for Lumberjack
    # T1 → T2: Gear Workshop is the gate
    if any(b["name"] == "Gear Workshop" for b in buildings):
        lines.append(f'    {sanitize_id("Forester")} -.->|"sustains wood"| {sanitize_id("Gear Workshop")}')

    # T2 → T3: Smelter needs Gears + ScrapMetal
    if any(b["name"] == "Smelter" for b in buildings):
        lines.append(f'    {sanitize_id("Gear Workshop")} -->|"Gears"| {sanitize_id("Smelter")}')
    if any(b["name"] == "Scavenger Flag" for b in buildings):
        lines.append(f'    {sanitize_id("Scavenger Flag")} -->|"Scrap Metal"| {sanitize_id("Smelter")}')

    # T2 → T2: Gear consumers
    gear_consumers_t2 = ["Paper Mill", "Tapper's Shack", "Wood Workshop", "Observatory"]
    for name in gear_consumers_t2:
        if any(b["name"] == name for b in buildings):
            lines.append(f'    {sanitize_id("Gear Workshop")} -->|"Gears"| {sanitize_id(name)}')

    # Metalsmith (IT) also from ScrapMetal
    if any(b["name"] == "Metalsmith" for b in buildings):
        lines.append(f'    {sanitize_id("Scavenger Flag")} -->|"Scrap Metal"| {sanitize_id("Metalsmith")}')

    # T2 → T4: Tapper's Shack → Wood Workshop
    if any(b["name"] == "Tapper's Shack" for b in buildings):
        lines.append(f'    {sanitize_id("TappersShack")} -->|"Pine Resin"| {sanitize_id("Wood Workshop")}')

    # T3 → T3: Smelter outputs
    metal_consumers = ["Bot Part Factory", "Bot Assembler", "Explosives Factory", "Refinery"]
    for name in metal_consumers:
        if any(b["name"] == name for b in buildings):
            lines.append(f'    {sanitize_id("Smelter")} -->|"Metal Blocks"| {sanitize_id(name)}')

    # T3 → T5: Bot Part Factory → MetalPart consumers
    if any(b["name"] == "Bot Part Factory" for b in buildings):
        lines.append(f'    {sanitize_id("Bot Part Factory")} -->|"Metal Parts"| {sanitize_id("Bot Assembler")}')

    # Grease Factory (IT)
    if any(b["name"] == "Grease Factory" for b in buildings):
        lines.append(f'    {sanitize_id("Gear Workshop")} -->|"Gears"| {sanitize_id("Grease Factory")}')

    # Explosives Factory → Explosives consumers
    if any(b["name"] == "Explosives Factory" for b in buildings):
        if any(b["name"] == "Dynamite" for b in buildings):
            lines.append(f'    {sanitize_id("Explosives Factory")} -->|"Explosives"| {sanitize_id("Dynamite")}')

    # Refinery → Extract consumers
    if any(b["name"] == "Refinery" for b in buildings):
        lines.append(f'    {sanitize_id("Refinery")} -->|"Extract"| t4')

    # Force vertical flow: invisible links between tier subgraphs
    lines.append("")
    lines.append("    %% Force vertical tier layout")
    active_tiers = [t for t in range(1, 6) if tiers[t]]
    for i in range(len(active_tiers) - 1):
        lines.append(f'    t{active_tiers[i]} ~~~ t{active_tiers[i + 1]}')

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def write_faction_doc(path: str, faction_label: str, buildings: list[dict], chart: str):
    counts = {}
    for b in buildings:
        counts[b["tier"]] = counts.get(b["tier"], 0) + 1
    summary = ", ".join(f"T{t}: {c}" for t, c in sorted(counts.items()))

    doc = f"""# {faction_label} — Building Unlock Flowchart (by Materials)

> Auto-generated from blueprint JSON files. Do not edit manually.
> Regenerate with: `python scripts/extract_flowchart.py`
>
> Arrows show the **resource production chain** — which buildings produce materials
> needed by other buildings. Buildings are grouped by their **construction material tier**
> (tier = highest-tier material required to build it).
>
> {len(buildings)} buildings: {summary}

```mermaid
{chart}
```
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"  Written: {path}")


def main():
    if not os.path.isdir(BLUEPRINTS_DIR):
        print(f"ERROR: Blueprint directory not found: {BLUEPRINTS_DIR}")
        sys.exit(1)

    all_ft_names, it_only_names, ft_only_names = parse_building_names_from_items()
    shared_names = [n for n in all_ft_names if n not in ft_only_names]

    print(f"Parsed: {len(all_ft_names)} FT, {len(it_only_names)} IT-exclusive, {len(shared_names)} shared")

    # Folktails: all FT names
    ft_buildings = collect_building_data(all_ft_names, "Folktails")
    # Iron Teeth: shared + IT-exclusive
    it_names = shared_names + it_only_names
    it_buildings = collect_building_data(it_names, "IronTeeth")

    ft_chart = generate_mermaid(ft_buildings, "Folktails", "Folktails")
    it_chart = generate_mermaid(it_buildings, "IronTeeth", "Iron Teeth")

    ft_path = os.path.join(DOCS_DIR, "Folktails — Building Flowchart.md")
    it_path = os.path.join(DOCS_DIR, "Iron Teeth — Building Flowchart.md")

    write_faction_doc(ft_path, "Folktails", ft_buildings, ft_chart)
    write_faction_doc(it_path, "Iron Teeth", it_buildings, it_chart)

    print(f"  Folktails: {len(ft_buildings)} buildings")
    print(f"  Iron Teeth: {len(it_buildings)} buildings")


if __name__ == "__main__":
    main()
