"""
Extract building construction tiers from Timberborn blueprint JSON files.

Self-contained script — parses Items.py directly to get building names,
then reads blueprint JSONs for construction costs.

Material -> Tier mapping:
  T1: Log, Plank                    (free resources)
  T2: Gear, Paper, PineResin        (Gear Workshop chain)
  T3: MetalBlock, ScrapMetal        (Smelter chain)
  T4: TreatedPlank, Dirt, Extract, Explosives  (advanced processing)
  T5: MetalPart, Grease             (Bot Part Factory / late-game)

Building tier = max tier of all its construction materials.
Buildings with no cost or only T1 materials = T1.
"""

import json
import os
import re

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

# ---------------------------------------------------------------------------
# Material -> tier mapping
# ---------------------------------------------------------------------------
MATERIAL_TIER: dict[str, int] = {
    "Log": 1, "Plank": 1,
    "Gear": 2, "Paper": 2, "PineResin": 2,
    "MetalBlock": 3, "ScrapMetal": 3,
    "TreatedPlank": 4, "Dirt": 4, "Extract": 4, "Explosives": 4,
    "MetalPart": 5, "Grease": 5,
}


def parse_building_names_from_items() -> tuple[list[str], list[str], set[str]]:
    """Parse Items.py to extract building names.

    Returns (all_ft_names, it_only_names, ft_only_name_set).
    """
    with open(ITEMS_PY, "r", encoding="utf-8") as f:
        source = f.read()

    # Extract names from blueprint list definitions: ("Name", ItemClassification.xxx),
    name_pattern = re.compile(r'\("([^"]+)",\s+ItemClassification\.\w+\)')

    # Find the list variable boundaries
    def extract_list_names(var_name: str) -> list[str]:
        # Find the variable assignment and its list content
        pattern = rf'{var_name}\s*(?::.*?)?\s*=\s*\[(.*?)\]'
        match = re.search(pattern, source, re.DOTALL)
        if not match:
            return []
        block = match.group(1)
        return name_pattern.findall(block)

    # FT blueprint categories
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

    # IT-only categories
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

    # FT-only names set
    ft_only_match = re.search(r'_FT_ONLY_NAMES:\s*set\[str\]\s*=\s*\{(.*?)\}', source, re.DOTALL)
    ft_only_names: set[str] = set()
    if ft_only_match:
        ft_only_names = set(re.findall(r'"([^"]+)"', ft_only_match.group(1)))

    return all_ft_names, it_only_names, ft_only_names


def display_name_to_dirname(name: str) -> str:
    """Convert display name to blueprint directory name."""
    return re.sub(r"[\s']+", "", name)


def extract_building_cost(json_path: str) -> list[dict]:
    with open(json_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    return data.get("BuildingSpec", {}).get("BuildingCost", [])


def get_tier_from_costs(costs: list[dict]) -> tuple[int, list[str]]:
    if not costs:
        return 1, []
    max_tier = 1
    unknown = []
    for cost in costs:
        material = cost.get("Id", "")
        tier = MATERIAL_TIER.get(material, 0)
        if tier == 0:
            unknown.append(material)
        max_tier = max(max_tier, tier)
    return max_tier, unknown


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


def process_buildings(names: list[str], faction: str, label: str) -> dict[str, int]:
    print(f"\n{'=' * 70}")
    print(f"{label} ({faction} blueprints)")
    print(f"{'=' * 70}")

    tiers: dict[str, int] = {}
    missing = []

    for name in names:
        dirname = display_name_to_dirname(name)
        json_path = find_blueprint(dirname, faction)
        if json_path is None:
            missing.append((name, dirname))
            tiers[name] = 1
            continue
        costs = extract_building_cost(json_path)
        tier, unknown = get_tier_from_costs(costs)
        tiers[name] = tier
        materials = ", ".join(f"{c['Id']}:{c['Amount']}" for c in costs)
        warn = f"  !! UNKNOWN: {unknown}" if unknown else ""
        print(f"  T{tier}  {name:35s}  [{materials}]{warn}")

    if missing:
        print(f"\n  MISSING BLUEPRINTS ({len(missing)}):")
        for name, dirname in missing:
            print(f"    {name} -> tried {dirname}.{faction}.blueprint.json")

    return tiers


def print_tier_distribution(label: str, tiers: dict[str, int]):
    counts = {t: 0 for t in range(1, 6)}
    for t in tiers.values():
        counts[t] += 1
    total = sum(counts.values())
    print(f"\n  {label} ({total} buildings):")
    for t in range(1, 6):
        names = sorted(n for n, tier in tiers.items() if tier == t)
        print(f"    Tier {t}: {counts[t]:3d}  {names[:5]}{'...' if len(names) > 5 else ''}")


def print_python_dict(var_name: str, tiers: dict[str, int]):
    print(f"\n{var_name}: dict[str, int] = {{")
    for tier in range(1, 6):
        names_in_tier = [n for n, t in tiers.items() if t == tier]
        if names_in_tier:
            print(f"    # --- Tier {tier} ---")
            for name in names_in_tier:
                print(f'    "{name}": {tier},')
    print("}")


def main():
    print(f"Blueprint directory: {BLUEPRINTS_DIR}")
    print(f"Exists: {os.path.isdir(BLUEPRINTS_DIR)}")

    all_ft_names, it_only_names, ft_only_names = parse_building_names_from_items()
    shared_names = [n for n in all_ft_names if n not in ft_only_names]

    print(f"\nParsed from Items.py:")
    print(f"  All FT blueprints: {len(all_ft_names)}")
    print(f"  FT-only: {len(ft_only_names)}")
    print(f"  Shared: {len(shared_names)}")
    print(f"  IT-exclusive: {len(it_only_names)}")

    # Process all FT buildings (shared + FT-only)
    ft_tiers = process_buildings(all_ft_names, "Folktails", "BUILDING_TIERS (Shared + Folktails)")

    # Process IT-exclusive buildings
    it_tiers = process_buildings(it_only_names, "IronTeeth", "IT_BUILDING_TIERS (IronTeeth-exclusive)")

    # Check shared buildings for IT cost differences
    print(f"\n{'=' * 70}")
    print("IT overrides for shared buildings (different tier than FT)")
    print(f"{'=' * 70}")
    it_overrides: dict[str, int] = {}
    for name in shared_names:
        dirname = display_name_to_dirname(name)
        json_path = find_blueprint(dirname, "IronTeeth")
        if json_path is None:
            continue
        costs = extract_building_cost(json_path)
        it_tier, _ = get_tier_from_costs(costs)
        ft_tier = ft_tiers.get(name, 1)
        if it_tier != ft_tier:
            it_overrides[name] = it_tier
            materials = ", ".join(f"{c['Id']}:{c['Amount']}" for c in costs)
            print(f"  T{ft_tier}->T{it_tier}  {name:35s}  [{materials}]")
    if not it_overrides:
        print("  (none)")

    # Summary
    print(f"\n{'=' * 70}")
    print("TIER DISTRIBUTION")
    print(f"{'=' * 70}")
    print_tier_distribution("Folktails (all)", ft_tiers)
    print_tier_distribution("IT-exclusive", it_tiers)
    if it_overrides:
        print_tier_distribution("IT shared overrides", it_overrides)

    # Python output
    print(f"\n{'=' * 70}")
    print("PYTHON OUTPUT (paste into BuildingTiers.py)")
    print(f"{'=' * 70}")
    print_python_dict("BUILDING_TIERS", ft_tiers)
    print_python_dict("IT_BUILDING_TIERS", it_tiers)
    if it_overrides:
        print_python_dict("IT_SHARED_OVERRIDES", it_overrides)


if __name__ == "__main__":
    main()
