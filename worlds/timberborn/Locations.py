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
# The lists below are kept for reference and backward compatibility.
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

ALL_BUILDING_NAMES: list[str] = (
    WOOD_BUILDINGS + FOOD_BUILDINGS + HOUSING_BUILDINGS + STORAGE_BUILDINGS
    + WATER_BUILDINGS + LANDSCAPING_BUILDINGS + METAL_BUILDINGS
    + POWER_BUILDINGS + SCIENCE_PRODUCTION_BUILDINGS + DISTRICT_BUILDINGS
    + WELLBEING_BUILDINGS + PATH_BUILDINGS + AUTOMATION_BUILDINGS
    + DECORATION_BUILDINGS + FT_MONUMENT_BUILDINGS
)

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
# Goods and thresholds map to construction-material tiers for logic gating.
# Order is append-only; never reorder or delete once IDs are assigned.
# ---------------------------------------------------------------------------
RESOURCE_MILESTONE_LOC_BASE = 9_710_000

RESOURCE_MILESTONE_LOCATIONS: list[str] = [
    # T1 — always producible from day 1
    "Resource: Reach 500 Logs",
    "Resource: Reach 1000 Logs",
    # T2 — requires Gear Workshop + Forester
    "Resource: Reach 500 Planks",
    "Resource: Reach 1000 Planks",
    "Resource: Reach 100 Gears",
    "Resource: Reach 250 Gears",
    "Resource: Reach 500 Bread",
    # T3 — requires Smelter + scrap source
    "Resource: Reach 100 Metal Blocks",
    "Resource: Reach 250 Metal Blocks",
    # T4 — requires Wood Workshop (Treated Planks) or Scavenger Flag/Metalsmith (Scrap Metal)
    "Resource: Reach 100 Treated Planks",
    "Resource: Reach 250 Treated Planks",
    "Resource: Reach 100 Scrap Metal",
    "Resource: Reach 250 Scrap Metal",
]


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
