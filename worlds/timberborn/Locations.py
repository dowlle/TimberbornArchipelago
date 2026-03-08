from BaseClasses import Location

# ---------------------------------------------------------------------------
# Base IDs — ranges reserved per category
#   9_500_000 – 9_599_999 : Folktails science unlock locations (one per building)
#   9_600_000 – 9_699_999 : IronTeeth science locations (future)
#   9_700_000 – 9_799_999 : Milestone locations (population, wellbeing, survival, wonder)
# ---------------------------------------------------------------------------
FT_SCIENCE_LOC_BASE = 9_500_000
MILESTONE_LOC_BASE  = 9_700_000


class TimberbornLocation(Location):
    game = "Timberborn"


# ---------------------------------------------------------------------------
# Science unlock locations (Folktails)
#
# One location per science-costed Folktails building, in the same stable
# order as ALL_FT_BLUEPRINTS in Items.py (must not be reordered).
# The location is "checked" when the player spends science on that slot.
#
# Names match Items.py blueprint names exactly (replacing "Blueprint: " with
# "Science: ") so the client can map them trivially.
#
# SC = in-game science cost (informational).
# ---------------------------------------------------------------------------

# --- WOOD ---
WOOD_SCIENCE_LOCATIONS = [
    # name                          SC
    "Science: Forester",          # 30
    "Science: Gear Workshop",     # 100
    "Science: Paper Mill",        # 250
    "Science: Printing Press",    # 400
    "Science: Tapper's Shack",    # 500
    "Science: Wood Workshop",     # 800
]

# --- FOOD ---
FOOD_SCIENCE_LOCATIONS = [
    "Science: Aquatic Farmhouse", # 150
    "Science: Bakery",            # 160
    "Science: Gristmill",         # 180
    "Science: Beehive",           # 400
]

# --- HOUSING ---
HOUSING_SCIENCE_LOCATIONS = [
    "Science: Mini Lodge",        # 50
    "Science: Double Lodge",      # 150
    "Science: Triple Lodge",      # 250
]

# --- STORAGE ---
STORAGE_SCIENCE_LOCATIONS = [
    "Science: Medium Tank",       # 120
    "Science: Large Warehouse",   # 250
    "Science: Large Tank",        # 600
    "Science: Underground Pile",  # 1000
]

# --- WATER ---
WATER_SCIENCE_LOCATIONS = [
    "Science: Badwater Pump",         # 250
    "Science: Fluid Dump",            # 250
    "Science: Large Water Pump",      # 400
    "Science: Aquifer Drill",         # 400
    "Science: Centrifuge",            # 600
    "Science: Badwater Dome",         # 2000
    "Science: Mechanical Fluid Pump", # 2500
    "Science: Badwater Rig",          # 4000
]

# --- LANDSCAPING ---
LANDSCAPING_SCIENCE_LOCATIONS = [
    "Science: Levee",                 # 120
    "Science: Floodgate",             # 150
    "Science: Impermeable Floor",     # 200
    "Science: Double Floodgate",      # 250
    "Science: Contamination Barrier", # 400
    "Science: Explosives Factory",    # 400
    "Science: Valve",                 # 400
    "Science: Triple Floodgate",      # 500
    "Science: Dynamite",              # 600
    "Science: Double Dynamite",       # 900
    "Science: Terrain Block",         # 1000
    "Science: Triple Dynamite",       # 1200
    "Science: Dirt Excavator",        # 2000
    "Science: Tunnel",                # 2000
]

# --- METAL ---
METAL_SCIENCE_LOCATIONS = [
    "Science: Scavenger Flag",    # 250
    "Science: Smelter",           # 300
    "Science: Mine",              # 4000
]

# --- POWER ---
POWER_SCIENCE_LOCATIONS = [
    "Science: Vertical Power Shaft",  # 40
    "Science: Wind Turbine",          # 120
    "Science: Geothermal Engine",     # 160
    "Science: Clutch",                # 400
    "Science: Gravity Battery",       # 400
    "Science: Large Wind Turbine",    # 1400
]

# --- SCIENCE PRODUCTION ---
SCIENCE_PRODUCTION_LOCATIONS = [
    "Science: Refinery",          # 400
    "Science: Bot Part Factory",  # 500
    "Science: Bot Assembler",     # 750
    "Science: Observatory",       # 1000
]

# --- DISTRICT MANAGEMENT ---
DISTRICT_SCIENCE_LOCATIONS = [
    "Science: Builders' Hut",     # 100
    "Science: District Crossing", # 600
]

# --- WELLBEING ---
WELLBEING_SCIENCE_LOCATIONS = [
    "Science: Shower",            # 50
    "Science: Medical Bed",       # 80
    "Science: Contemplation Spot",# 100
    "Science: Lido",              # 250
    "Science: Herbalist",         # 300
    "Science: Agora",             # 400
    "Science: Carousel",          # 700
    "Science: Detailer",          # 1000
    "Science: Dance Hall",        # 1200
    "Science: Mud Pit",           # 1800
]

# --- PATHS ---
PATH_SCIENCE_LOCATIONS = [
    "Science: Stairs",                    # 70
    "Science: Platform",                  # 100
    "Science: Double Platform",           # 150
    "Science: Suspension Bridge 1x1",     # 150
    "Science: Gate",                      # 200
    "Science: Triple Platform",           # 200
    "Science: Suspension Bridge 2x1",     # 250
    "Science: Overhang 2x1",              # 350
    "Science: Spiral Stairs",             # 350
    "Science: Suspension Bridge 3x1",     # 400
    "Science: Zipline Pylon",             # 500
    "Science: Overhang 3x1",              # 550
    "Science: Suspension Bridge 4x1",     # 600
    "Science: Zipline Beam",              # 600
    "Science: Zipline Station",           # 700
    "Science: Metal Platform 3x3",        # 1000
    "Science: Overhang 4x1",              # 1000
    "Science: Suspension Bridge 5x1",     # 1000
    "Science: Overhang 5x1",              # 1800
    "Science: Suspension Bridge 6x1",     # 1800
    "Science: Metal Platform 5x5",        # 2000
    "Science: Overhang 6x1",              # 3000
]

# --- AUTOMATION ---
AUTOMATION_SCIENCE_LOCATIONS = [
    "Science: Lever",                 # 50
    "Science: Relay",                 # 80
    "Science: Flow Sensor",           # 100
    "Science: Chronometer",           # 150
    "Science: Depth Sensor",          # 200
    "Science: Population Counter",    # 200
    "Science: Resource Counter",      # 250
    "Science: Science Counter",       # 300
    "Science: Weather Station",       # 300
    "Science: Contamination Sensor",  # 400
    "Science: Indicator",             # 400
    "Science: Speaker",               # 500
    "Science: Power Meter",           # 600
    "Science: Timer",                 # 600
    "Science: Firework Launcher",     # 700
    "Science: Memory",                # 1000
    "Science: Detonator",             # 1400
    "Science: HTTP Lever",            # 5000
    "Science: HTTP Adapter",          # 7500
]

# --- DECORATION ---
DECORATION_SCIENCE_LOCATIONS = [
    "Science: Roof 1x1",          # 60
    "Science: Bench",             # 80
    "Science: Roof 1x2",          # 80
    "Science: Lantern",           # 100
    "Science: Hammock",           # 120
    "Science: Roof 2x2",          # 120
    "Science: Hedge",             # 150
    "Science: Roof 2x3",          # 150
    "Science: Roof 3x2",          # 150
    "Science: Stream Gauge",      # 150
    "Science: Wood Fence",        # 150
    "Science: Scarecrow",         # 200
    "Science: Weathervane",       # 250
    "Science: Beaver Statue",     # 500
    "Science: Bulletin Pole",     # 600
    "Science: Pole Banner",       # 700
    "Science: Square Banner",     # 700
]

# --- MONUMENTS ---
MONUMENT_SCIENCE_LOCATIONS = [
    "Science: Farmer Monument",   # 1000
    "Science: Brazier of Bonding",# 3000
    "Science: Fountain of Joy",   # 12000
]

# All science locations in stable order (mirrors Items.py ALL_FT_BLUEPRINTS order)
ALL_SCIENCE_LOCATIONS: list[str] = (
    WOOD_SCIENCE_LOCATIONS
    + FOOD_SCIENCE_LOCATIONS
    + HOUSING_SCIENCE_LOCATIONS
    + STORAGE_SCIENCE_LOCATIONS
    + WATER_SCIENCE_LOCATIONS
    + LANDSCAPING_SCIENCE_LOCATIONS
    + METAL_SCIENCE_LOCATIONS
    + POWER_SCIENCE_LOCATIONS
    + SCIENCE_PRODUCTION_LOCATIONS
    + DISTRICT_SCIENCE_LOCATIONS
    + WELLBEING_SCIENCE_LOCATIONS
    + PATH_SCIENCE_LOCATIONS
    + AUTOMATION_SCIENCE_LOCATIONS
    + DECORATION_SCIENCE_LOCATIONS
    + MONUMENT_SCIENCE_LOCATIONS
)

# ---------------------------------------------------------------------------
# Milestone locations — triggered by in-game events, not science spending
# ---------------------------------------------------------------------------
POPULATION_LOCATIONS: list[str] = [
    "Population: Reach 10 Beavers",
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

WONDER_LOCATIONS: list[str] = [
    "Wonder: Complete Earth Recultivator",
]

ALL_MILESTONE_LOCATIONS: list[str] = (
    POPULATION_LOCATIONS
    + WELLBEING_LOCATIONS
    + SURVIVAL_LOCATIONS
    + WONDER_LOCATIONS
)

# ---------------------------------------------------------------------------
# ID maps
# ---------------------------------------------------------------------------
science_location_name_to_id: dict[str, int] = {
    name: FT_SCIENCE_LOC_BASE + i for i, name in enumerate(ALL_SCIENCE_LOCATIONS)
}

milestone_location_name_to_id: dict[str, int] = {
    name: MILESTONE_LOC_BASE + i for i, name in enumerate(ALL_MILESTONE_LOCATIONS)
}

location_name_to_id: dict[str, int] = {
    **science_location_name_to_id,
    **milestone_location_name_to_id,
}

location_table: dict[str, dict] = {name: {} for name in location_name_to_id}
