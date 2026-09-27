from BaseClasses import Location

# ---------------------------------------------------------------------------
# Base IDs — ranges reserved per category
#   9_500_000 – 9_599_999 : Shop slot locations (one per building in the AP shop)
#   9_700_000 – 9_799_999 : Milestone locations (population, wellbeing, survival, wonder)
# ---------------------------------------------------------------------------
FT_SCIENCE_LOC_BASE = 9_500_000
MILESTONE_LOC_BASE  = 9_700_000


class TimberbornLocation(Location):
    game = "Timberborn"


# ---------------------------------------------------------------------------
# Shop slot locations
#
# Each slot is a fixed position in one of 4 shop paths (A–D).  At generation
# time, buildings are shuffled into these slots.  Slot names are stable across
# seeds so IDs never shift.  Pre-allocated with SLOTS_PER_PATH slots per path
# to allow future building additions without breaking existing IDs.
#
# Naming: "Shop: A-01" through "Shop: D-40"  (1-indexed)
# ---------------------------------------------------------------------------
NUM_PATHS = 4
SLOTS_PER_PATH = 40
PATH_LABELS = ["A", "B", "C", "D"]

ALL_SCIENCE_LOCATIONS: list[str] = [
    f"Shop: {label}-{slot:02d}"
    for label in PATH_LABELS
    for slot in range(1, SLOTS_PER_PATH + 1)
]

# ---------------------------------------------------------------------------
# Building pool — the building names used as a source list for ShopLayout
# to draw from.  These are NOT location names; they're just the reference pool.
#
# Faction-specific pools are built via Items.get_building_names(faction).
# Category lists below are legacy 1.0 snapshots, retained for compatibility.
# Use Items.get_building_names for current pools; ALL_BUILDING_NAMES delegates to it.
# ---------------------------------------------------------------------------

# --- WOOD ---
WOOD_BUILDINGS = [
    "Forester", "Gear Workshop", "Paper Mill", "Printing Press",
    "Tapper's Shack", "Wood Workshop",
]

# --- FOOD ---
FOOD_BUILDINGS = [
    "Aquatic Farmhouse", "Bakery", "Gristmill", "Beehive",
]

# --- HOUSING ---
HOUSING_BUILDINGS = [
    "Mini Lodge", "Double Lodge", "Triple Lodge",
]

# --- STORAGE ---
STORAGE_BUILDINGS = [
    "Medium Tank", "Large Warehouse", "Large Tank", "Underground Pile",
]

# --- WATER ---
WATER_BUILDINGS = [
    "Badwater Pump", "Fill Valve", "Fluid Dump", "Large Water Pump",
    "Aquifer Drill", "Centrifuge", "Badwater Dome", "Mechanical Fluid Pump",
    "Badwater Rig",
]

# --- LANDSCAPING ---
LANDSCAPING_BUILDINGS = [
    "Levee", "Floodgate", "Impermeable Floor", "Double Floodgate",
    "Contamination Barrier", "Explosives Factory", "Valve", "Triple Floodgate",
    "Dynamite", "Double Dynamite", "Terrain Block", "Triple Dynamite",
    "Dirt Excavator", "Tunnel",
]

# --- METAL ---
METAL_BUILDINGS = [
    "Scavenger Flag", "Smelter", "Mine",
]

# --- POWER ---
POWER_BUILDINGS = [
    "Vertical Power Shaft", "Wind Turbine", "Geothermal Engine",
    "Clutch", "Gravity Battery", "Large Wind Turbine",
]

# --- SCIENCE PRODUCTION ---
SCIENCE_PRODUCTION_BUILDINGS = [
    "Refinery", "Bot Part Factory", "Bot Assembler", "Observatory",
]

# --- DISTRICT MANAGEMENT ---
DISTRICT_BUILDINGS = [
    "Builders' Hut", "District Crossing",
]

# --- WELLBEING ---
WELLBEING_BUILDINGS = [
    "Shower", "Medical Bed", "Contemplation Spot", "Lido", "Herbalist",
    "Agora", "Carousel", "Detailer", "Dance Hall", "Mud Pit",
]

# --- PATHS ---
PATH_BUILDINGS = [
    "Stairs", "Platform", "Double Platform", "Suspension Bridge 1x1",
    "Gate", "Triple Platform", "Suspension Bridge 2x1", "Overhang 2x1",
    "Spiral Stairs", "Suspension Bridge 3x1", "Zipline Pylon", "Overhang 3x1",
    "Suspension Bridge 4x1", "Zipline Beam", "Zipline Station",
    "Metal Platform 3x3", "Overhang 4x1", "Suspension Bridge 5x1",
    "Overhang 5x1", "Suspension Bridge 6x1", "Metal Platform 5x5",
    "Overhang 6x1",
]

# --- AUTOMATION ---
AUTOMATION_BUILDINGS = [
    "Lever", "Relay", "Flow Sensor", "Chronometer", "Depth Sensor",
    "Population Counter", "Resource Counter", "Science Counter",
    "Weather Station", "Contamination Sensor", "Indicator", "Speaker",
    "Power Meter", "Timer", "Firework Launcher", "Memory", "Detonator",
    "HTTP Lever", "HTTP Adapter",
]

# --- DECORATION ---
DECORATION_BUILDINGS = [
    "Roof 1x1", "Bench", "Roof 1x2", "Lantern", "Hammock", "Roof 2x2",
    "Hedge", "Roof 2x3", "Roof 3x2", "Stream Gauge", "Wood Fence",
    "Scarecrow", "Weathervane", "Beaver Statue", "Bulletin Pole",
    "Pole Banner", "Square Banner",
]

# --- FOLKTAILS MONUMENTS ---
FT_MONUMENT_BUILDINGS = [
    "Farmer Monument", "Brazier of Bonding", "Fountain of Joy",
]

# --- IRON TEETH MONUMENTS ---
IT_MONUMENT_BUILDINGS = [
    "Laborer Monument", "Flame of Unity", "Tribute to Ingenuity",
]

from .Items import get_building_names

ALL_BUILDING_NAMES: list[str] = get_building_names("Folktails")

# ---------------------------------------------------------------------------
# Milestone locations — triggered by in-game events, not science spending
# ---------------------------------------------------------------------------
POPULATION_LOCATIONS: list[str] = [
    "Population: First Beaver Born",
    "Population: First Beaver Grown Up",
    "Population: Reach 15 Beavers",
    "Population: Reach 25 Beavers",
    "Population: Reach 50 Beavers",
    "Population: Reach 100 Beavers",
    "Population: Reach 200 Beavers",
]

WELLBEING_LOCATIONS: list[str] = [
    "Well-being: Reach Level 5",
    "Well-being: Reach Level 10",
    "Well-being: Reach Level 15",
    "Well-being: Reach Level 20",
]

SURVIVAL_LOCATIONS: list[str] = [
    "Survival: Survive 1st Drought",
    "Survival: Survive 5 Droughts",
    "Survival: Survive 10 Droughts",
    "Survival: Survive 1st Badtide",
    "Survival: Survive 5 Badtides",
    "Survival: Survive 10 Badtides",
]

FT_WONDER_LOCATIONS: list[str] = [
    "Wonder: Complete Earth Recultivator",
]

IT_WONDER_LOCATIONS: list[str] = [
    "Wonder: Complete Earth Repopulator",
]

# Backward compat alias
WONDER_LOCATIONS = FT_WONDER_LOCATIONS

# All milestones in stable order — append-only to preserve IDs
ALL_MILESTONE_LOCATIONS: list[str] = (
    POPULATION_LOCATIONS
    + WELLBEING_LOCATIONS
    + SURVIVAL_LOCATIONS
    + FT_WONDER_LOCATIONS
    + IT_WONDER_LOCATIONS  # appended at end to preserve existing FT milestone IDs
)

# ---------------------------------------------------------------------------
# Resource milestone locations — triggered by global resource count thresholds.
# IDs start at 9_710_000 (clear of the existing 9_700_000-9_700_018 block).
# This list only assigns permanent IDs. Which milestones a player gets depends
# on faction and the resource_milestone_set option (see the lists below).
# Order is append-only; never reorder or delete once IDs are assigned.
# ---------------------------------------------------------------------------
RESOURCE_MILESTONE_LOC_BASE = 9_710_000

RESOURCE_MILESTONE_LOCATIONS: list[str] = [
    # Original set (IDs 9_710_000 - 9_710_012)
    "Resource: Reach 500 Logs",
    "Resource: Reach 1000 Logs",
    "Resource: Reach 500 Planks",
    "Resource: Reach 1000 Planks",
    "Resource: Reach 100 Gears",
    "Resource: Reach 250 Gears",
    "Resource: Reach 500 Bread",  # Folktails only: Iron Teeth cannot make Bread
    "Resource: Reach 100 Metal Blocks",
    "Resource: Reach 250 Metal Blocks",
    "Resource: Reach 100 Treated Planks",
    "Resource: Reach 250 Treated Planks",
    "Resource: Reach 100 Scrap Metal",
    "Resource: Reach 250 Scrap Metal",
    # Iron Teeth replacement for 500 Bread
    "Resource: Reach 500 Corn Rations",
    # Shared, lite set
    "Resource: Reach 100 Logs",
    "Resource: Reach 250 Logs",
    "Resource: Reach 50 Planks",
    "Resource: Reach 100 Planks",
    "Resource: Reach 10 Gears",
    "Resource: Reach 25 Gears",
    "Resource: Reach 50 Gears",
    "Resource: Reach 10 Treated Planks",
    "Resource: Reach 25 Treated Planks",
    "Resource: Reach 50 Treated Planks",
    "Resource: Reach 10 Metal Blocks",
    "Resource: Reach 25 Metal Blocks",
    "Resource: Reach 50 Metal Blocks",
    "Resource: Reach 25 Scrap Metal",
    "Resource: Reach 50 Scrap Metal",
    # Shared, full set only
    "Resource: Reach 10 Pine Resin",
    "Resource: Reach 25 Pine Resin",
    "Resource: Reach 50 Pine Resin",
    "Resource: Reach 100 Water",
    "Resource: Reach 250 Water",
    "Resource: Reach 250 Berries",
    "Resource: Reach 10 Extract",
    "Resource: Reach 25 Extract",
    "Resource: Reach 50 Extract",
    "Resource: Reach 10 Explosives",
    "Resource: Reach 25 Explosives",
    # Folktails, lite set
    "Resource: Reach 10 Bread",
    "Resource: Reach 25 Bread",
    "Resource: Reach 50 Bread",
    # Folktails, full set only
    "Resource: Reach 25 Paper",
    "Resource: Reach 50 Paper",
    "Resource: Reach 100 Paper",
    "Resource: Reach 25 Grilled Potatoes",
    "Resource: Reach 50 Grilled Potatoes",
    "Resource: Reach 100 Grilled Potatoes",
    "Resource: Reach 25 Cattail Crackers",
    "Resource: Reach 50 Cattail Crackers",
    "Resource: Reach 100 Cattail Crackers",
    "Resource: Reach 10 Maple Pastries",
    "Resource: Reach 25 Maple Pastries",
    "Resource: Reach 50 Maple Pastries",
    "Resource: Reach 10 Books",
    "Resource: Reach 25 Books",
    "Resource: Reach 10 Biofuel",
    "Resource: Reach 25 Biofuel",
    "Resource: Reach 50 Biofuel",
    "Resource: Reach 10 Antidote",
    "Resource: Reach 25 Antidote",
    # Iron Teeth, lite set
    "Resource: Reach 25 Corn Rations",
    "Resource: Reach 50 Corn Rations",
    "Resource: Reach 100 Corn Rations",
    # Iron Teeth, full set only
    "Resource: Reach 25 Fermented Cassava",
    "Resource: Reach 50 Fermented Cassava",
    "Resource: Reach 100 Fermented Cassava",
    "Resource: Reach 10 Eggplant Rations",
    "Resource: Reach 25 Eggplant Rations",
    "Resource: Reach 50 Eggplant Rations",
    "Resource: Reach 50 Fermented Soybean",
    "Resource: Reach 50 Kohlrabi",
    "Resource: Reach 100 Kohlrabi",
    "Resource: Reach 50 Mangrove Fruit",
    "Resource: Reach 100 Mangrove Fruit",
    "Resource: Reach 10 Metal Parts",
    "Resource: Reach 25 Metal Parts",
    "Resource: Reach 50 Metal Parts",
    "Resource: Reach 10 Coffee",
    "Resource: Reach 25 Coffee",
    "Resource: Reach 50 Coffee",
    "Resource: Reach 10 Grease",
    "Resource: Reach 25 Grease",
]

# Milestone sets, split by faction like the Wonder locations.
# Values match the resource_milestone_set option: 0 classic, 1 lite, 2 full.
RESOURCE_MILESTONE_SET_CLASSIC = 0
RESOURCE_MILESTONE_SET_LITE = 1
RESOURCE_MILESTONE_SET_FULL = 2

_CLASSIC_SHARED: list[str] = [
    name for name in RESOURCE_MILESTONE_LOCATIONS[:13] if not name.endswith(" Bread")
]
_LITE_SHARED: list[str] = RESOURCE_MILESTONE_LOCATIONS[14:29]
_FULL_SHARED: list[str] = RESOURCE_MILESTONE_LOCATIONS[29:40]
_LITE_FT: list[str] = RESOURCE_MILESTONE_LOCATIONS[40:43]
_FULL_FT: list[str] = RESOURCE_MILESTONE_LOCATIONS[43:62]
_LITE_IT: list[str] = RESOURCE_MILESTONE_LOCATIONS[62:65]
_FULL_IT: list[str] = RESOURCE_MILESTONE_LOCATIONS[65:84]

_RESOURCE_SETS: dict[str, tuple[list[str], list[str], list[str]]] = {
    # faction: (classic, lite additions, full additions)
    "Folktails": (
        _CLASSIC_SHARED + ["Resource: Reach 500 Bread"],
        _LITE_SHARED + _LITE_FT,
        _FULL_SHARED + _FULL_FT,
    ),
    "IronTeeth": (
        _CLASSIC_SHARED + ["Resource: Reach 500 Corn Rations"],
        _LITE_SHARED + _LITE_IT,
        _FULL_SHARED + _FULL_IT,
    ),
}


def get_resource_milestones(faction: str,
                            milestone_set: int = RESOURCE_MILESTONE_SET_FULL) -> list[str]:
    """Resource milestone locations for a faction and milestone set, in ID order."""
    classic, lite, full = _RESOURCE_SETS[faction]
    names = list(classic)
    if milestone_set >= RESOURCE_MILESTONE_SET_LITE:
        names += lite
    if milestone_set >= RESOURCE_MILESTONE_SET_FULL:
        names += full
    return sorted(names, key=RESOURCE_MILESTONE_LOCATIONS.index)


FT_RESOURCE_MILESTONE_LOCATIONS: list[str] = get_resource_milestones("Folktails")
IT_RESOURCE_MILESTONE_LOCATIONS: list[str] = get_resource_milestones("IronTeeth")


# ---------------------------------------------------------------------------
# ID maps
# ---------------------------------------------------------------------------
science_location_name_to_id: dict[str, int] = {
    name: FT_SCIENCE_LOC_BASE + i for i, name in enumerate(ALL_SCIENCE_LOCATIONS)
}

milestone_location_name_to_id: dict[str, int] = {
    name: MILESTONE_LOC_BASE + i for i, name in enumerate(ALL_MILESTONE_LOCATIONS)
}

resource_milestone_location_name_to_id: dict[str, int] = {
    name: RESOURCE_MILESTONE_LOC_BASE + i
    for i, name in enumerate(RESOURCE_MILESTONE_LOCATIONS)
}

location_name_to_id: dict[str, int] = {
    **science_location_name_to_id,
    **milestone_location_name_to_id,
    **resource_milestone_location_name_to_id,
}

location_table: dict[str, dict] = {name: {} for name in location_name_to_id}
