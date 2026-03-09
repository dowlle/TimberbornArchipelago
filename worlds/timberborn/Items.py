from BaseClasses import Item, ItemClassification

# ---------------------------------------------------------------------------
# Base IDs — ranges reserved per category so IronTeeth can be added later
#   9_000_000 – 9_099_999 : Folktails blueprint items
#   9_100_000 – 9_199_999 : IronTeeth blueprint items (future)
#   9_200_000 – 9_209_999 : Boost items
#   9_210_000 – 9_219_999 : Filler items
#   9_220_000 – 9_229_999 : Trap items
#   9_230_000 – 9_239_999 : Skip items
# ---------------------------------------------------------------------------
FT_BLUEPRINT_BASE  = 9_000_000
BOOST_BASE         = 9_200_000
FILLER_BASE        = 9_210_000
TRAP_BASE          = 9_220_000
SKIP_BASE          = 9_230_000


class TimberbornItem(Item):
    game = "Timberborn"


# ---------------------------------------------------------------------------
# Folktails blueprint items, grouped by category.
# Names are exact in-game display names (verified from blueprint JSONs).
# Classification:
#   progression = logically required to reach certain locations
#   useful      = helpful but not in the logic graph
#   filler      = cosmetic / decorative, padding the item pool
#
# SC = science cost in-game (informational, not used at runtime)
# ---------------------------------------------------------------------------

# --- WOOD ---
WOOD_BLUEPRINTS = [
    # name,                         classification,                  SC
    ("Forester",                    ItemClassification.progression), # 30
    ("Gear Workshop",               ItemClassification.progression), # 100
    ("Paper Mill",                  ItemClassification.progression), # 250
    ("Printing Press",              ItemClassification.useful),       # 400
    ("Tapper's Shack",              ItemClassification.progression),  # 500
    ("Wood Workshop",               ItemClassification.progression),  # 800
]

# --- FOOD ---
FOOD_BLUEPRINTS = [
    ("Aquatic Farmhouse",           ItemClassification.useful),       # 150
    ("Bakery",                      ItemClassification.progression),  # 160
    ("Gristmill",                   ItemClassification.useful),       # 180
    ("Beehive",                     ItemClassification.useful),       # 400
]

# --- HOUSING ---
HOUSING_BLUEPRINTS = [
    ("Mini Lodge",                  ItemClassification.useful),       # 50
    ("Double Lodge",                ItemClassification.useful),       # 150
    ("Triple Lodge",                ItemClassification.useful),       # 250
]

# --- STORAGE ---
STORAGE_BLUEPRINTS = [
    ("Medium Tank",                 ItemClassification.useful),       # 120
    ("Large Warehouse",             ItemClassification.useful),       # 250
    ("Large Tank",                  ItemClassification.useful),       # 600
    ("Underground Pile",            ItemClassification.useful),       # 1000
]

# --- WATER ---
WATER_BLUEPRINTS = [
    ("Badwater Pump",               ItemClassification.useful),       # 250
    ("Fill Valve",                  ItemClassification.useful),       # 300
    ("Fluid Dump",                  ItemClassification.useful),       # 250
    ("Large Water Pump",            ItemClassification.progression),  # 400
    ("Aquifer Drill",               ItemClassification.useful),       # 400
    ("Centrifuge",                  ItemClassification.useful),       # 600
    ("Badwater Dome",               ItemClassification.useful),       # 2000
    ("Mechanical Fluid Pump",       ItemClassification.useful),       # 2500
    ("Badwater Rig",                ItemClassification.useful),       # 4000
]

# --- LANDSCAPING ---
LANDSCAPING_BLUEPRINTS = [
    ("Levee",                       ItemClassification.useful),       # 120
    ("Floodgate",                   ItemClassification.progression),  # 150
    ("Impermeable Floor",           ItemClassification.useful),       # 200
    ("Double Floodgate",            ItemClassification.useful),       # 250
    ("Contamination Barrier",       ItemClassification.useful),       # 400
    ("Explosives Factory",          ItemClassification.progression),  # 400
    ("Valve",                       ItemClassification.useful),       # 400
    ("Triple Floodgate",            ItemClassification.useful),       # 500
    ("Dynamite",                    ItemClassification.useful),       # 600
    ("Double Dynamite",             ItemClassification.useful),       # 900
    ("Terrain Block",               ItemClassification.filler),       # 1000
    ("Triple Dynamite",             ItemClassification.useful),       # 1200
    ("Dirt Excavator",              ItemClassification.useful),       # 2000
    ("Tunnel",                      ItemClassification.useful),       # 2000
]

# --- METAL ---
METAL_BLUEPRINTS = [
    ("Scavenger Flag",              ItemClassification.progression),  # 250
    ("Smelter",                     ItemClassification.progression),  # 300
    ("Mine",                        ItemClassification.useful),       # 4000
]

# --- POWER ---
POWER_BLUEPRINTS = [
    ("Vertical Power Shaft",        ItemClassification.filler),       # 40
    ("Wind Turbine",                ItemClassification.progression),  # 120
    ("Geothermal Engine",           ItemClassification.progression),  # 160
    ("Clutch",                      ItemClassification.useful),       # 400
    ("Gravity Battery",             ItemClassification.progression),  # 400
    ("Large Wind Turbine",          ItemClassification.progression),  # 1400
]

# --- SCIENCE PRODUCTION ---
SCIENCE_BLUEPRINTS = [
    ("Refinery",                    ItemClassification.progression),  # 400  (produces Extract)
    ("Bot Part Factory",            ItemClassification.progression),  # 500
    ("Bot Assembler",               ItemClassification.progression),  # 750
    ("Observatory",                 ItemClassification.useful),       # 1000
]

# --- DISTRICT MANAGEMENT ---
DISTRICT_BLUEPRINTS = [
    ("Builders' Hut",               ItemClassification.progression),  # 100
    ("District Crossing",           ItemClassification.useful),       # 600
]

# --- WELLBEING ---
WELLBEING_BLUEPRINTS = [
    ("Shower",                      ItemClassification.useful),       # 50
    ("Medical Bed",                 ItemClassification.useful),       # 80
    ("Contemplation Spot",          ItemClassification.filler),       # 100
    ("Lido",                        ItemClassification.useful),       # 250
    ("Herbalist",                   ItemClassification.useful),       # 300
    ("Agora",                       ItemClassification.useful),       # 400
    ("Carousel",                    ItemClassification.useful),       # 700
    ("Detailer",                    ItemClassification.useful),       # 1000
    ("Dance Hall",                  ItemClassification.useful),       # 1200
    ("Mud Pit",                     ItemClassification.useful),       # 1800
]

# --- PATHS ---
PATH_BLUEPRINTS = [
    ("Stairs",                      ItemClassification.progression),  # 70
    ("Platform",                    ItemClassification.useful),       # 100
    ("Double Platform",             ItemClassification.useful),       # 150
    ("Suspension Bridge 1x1",       ItemClassification.useful),       # 150
    ("Gate",                        ItemClassification.useful),       # 200
    ("Triple Platform",             ItemClassification.useful),       # 200
    ("Suspension Bridge 2x1",       ItemClassification.useful),       # 250
    ("Overhang 2x1",                ItemClassification.useful),       # 350
    ("Spiral Stairs",               ItemClassification.useful),       # 350
    ("Suspension Bridge 3x1",       ItemClassification.useful),       # 400
    ("Zipline Pylon",               ItemClassification.useful),       # 500
    ("Overhang 3x1",                ItemClassification.useful),       # 550
    ("Suspension Bridge 4x1",       ItemClassification.filler),       # 600
    ("Zipline Beam",                ItemClassification.useful),       # 600
    ("Zipline Station",             ItemClassification.useful),       # 700
    ("Metal Platform 3x3",          ItemClassification.filler),       # 1000
    ("Overhang 4x1",                ItemClassification.filler),       # 1000
    ("Suspension Bridge 5x1",       ItemClassification.filler),       # 1000
    ("Overhang 5x1",                ItemClassification.filler),       # 1800
    ("Suspension Bridge 6x1",       ItemClassification.filler),       # 1800
    ("Metal Platform 5x5",          ItemClassification.filler),       # 2000
    ("Overhang 6x1",                ItemClassification.filler),       # 3000
]

# --- AUTOMATION ---
AUTOMATION_BLUEPRINTS = [
    ("Lever",                       ItemClassification.useful),       # 50
    ("Relay",                       ItemClassification.useful),       # 80
    ("Flow Sensor",                 ItemClassification.useful),       # 100
    ("Chronometer",                 ItemClassification.useful),       # 150
    ("Depth Sensor",                ItemClassification.useful),       # 200
    ("Population Counter",          ItemClassification.filler),       # 200
    ("Resource Counter",            ItemClassification.filler),       # 250
    ("Science Counter",             ItemClassification.filler),       # 300
    ("Weather Station",             ItemClassification.useful),       # 300
    ("Contamination Sensor",        ItemClassification.useful),       # 400
    ("Indicator",                   ItemClassification.filler),       # 400
    ("Speaker",                     ItemClassification.filler),       # 500
    ("Power Meter",                 ItemClassification.useful),       # 600
    ("Timer",                       ItemClassification.useful),       # 600
    ("Firework Launcher",           ItemClassification.filler),       # 700
    ("Memory",                      ItemClassification.useful),       # 1000
    ("Detonator",                   ItemClassification.useful),       # 1400
    ("HTTP Lever",                  ItemClassification.filler),       # 5000
    ("HTTP Adapter",                ItemClassification.filler),       # 7500
]

# --- DECORATION ---
DECORATION_BLUEPRINTS = [
    ("Roof 1x1",                    ItemClassification.filler),       # 60
    ("Bench",                       ItemClassification.filler),       # 80
    ("Roof 1x2",                    ItemClassification.filler),       # 80
    ("Lantern",                     ItemClassification.filler),       # 100
    ("Hammock",                     ItemClassification.filler),       # 120
    ("Roof 2x2",                    ItemClassification.filler),       # 120
    ("Hedge",                       ItemClassification.filler),       # 150
    ("Roof 2x3",                    ItemClassification.filler),       # 150
    ("Roof 3x2",                    ItemClassification.filler),       # 150
    ("Stream Gauge",                ItemClassification.filler),       # 150
    ("Wood Fence",                  ItemClassification.filler),       # 150
    ("Scarecrow",                   ItemClassification.filler),       # 200
    ("Weathervane",                 ItemClassification.filler),       # 250
    ("Beaver Statue",               ItemClassification.filler),       # 500
    ("Bulletin Pole",               ItemClassification.filler),       # 600
    ("Pole Banner",                 ItemClassification.filler),       # 700
    ("Square Banner",               ItemClassification.filler),       # 700
]

# --- MONUMENTS (pre-Wonder) ---
MONUMENT_BLUEPRINTS = [
    ("Farmer Monument",             ItemClassification.useful),       # 1000
    ("Brazier of Bonding",          ItemClassification.useful),       # 3000
    ("Fountain of Joy",             ItemClassification.useful),       # 12000
    # Earth Recultivator (20000) is the goal/wonder — not a received item
]

# ---------------------------------------------------------------------------
# All Folktails blueprint items in a stable order (order must never change
# once assigned IDs, to avoid shifting existing IDs).
# ---------------------------------------------------------------------------
ALL_FT_BLUEPRINTS: list[tuple[str, ItemClassification]] = (
    WOOD_BLUEPRINTS
    + FOOD_BLUEPRINTS
    + HOUSING_BLUEPRINTS
    + STORAGE_BLUEPRINTS
    + WATER_BLUEPRINTS
    + LANDSCAPING_BLUEPRINTS
    + METAL_BLUEPRINTS
    + POWER_BLUEPRINTS
    + SCIENCE_BLUEPRINTS
    + DISTRICT_BLUEPRINTS
    + WELLBEING_BLUEPRINTS
    + PATH_BLUEPRINTS
    + AUTOMATION_BLUEPRINTS
    + DECORATION_BLUEPRINTS
    + MONUMENT_BLUEPRINTS
)

# ---------------------------------------------------------------------------
# Passive boosts (received from the multiworld, applied globally)
# ---------------------------------------------------------------------------
BOOSTS: list[tuple[str, ItemClassification]] = [
    ("Boost: Faster Movement Speed",        ItemClassification.useful),
    ("Boost: Increased Carrying Capacity",  ItemClassification.useful),
    ("Boost: Faster Working Speed",         ItemClassification.useful),
    ("Boost: Faster Tree Growth",           ItemClassification.useful),
    ("Boost: Longer Life Expectancy",       ItemClassification.useful),
    ("Boost: Better Woodcutting Chance",    ItemClassification.useful),
]

# ---------------------------------------------------------------------------
# Filler — resource care packages delivered to nearest District Center
# ---------------------------------------------------------------------------
FILLER_ITEMS: list[tuple[str, ItemClassification, int]] = [
    # name,                              classification,              count
    ("Filler: 50 Logs",                 ItemClassification.filler,   6),
    ("Filler: 20 Planks",               ItemClassification.filler,   4),
    ("Filler: 10 Gears",                ItemClassification.filler,   4),
    ("Filler: 20 Bread",                ItemClassification.filler,   4),
    ("Filler: 5 Metal Blocks",          ItemClassification.filler,   3),
    ("Filler: 10 Treated Planks",       ItemClassification.filler,   3),
    ("Filler: 5 Scrap Metal",           ItemClassification.filler,   3),
]

# ---------------------------------------------------------------------------
# Traps — negative effects sent from/to other players
# ---------------------------------------------------------------------------
TRAP_ITEMS: list[tuple[str, ItemClassification, int]] = [
    ("Trap: Early Drought",             ItemClassification.trap,     3),
    ("Trap: Hungry Beavers",            ItemClassification.trap,     3),
    ("Trap: Badwater Leak",             ItemClassification.trap,     2),
]

# ---------------------------------------------------------------------------
# Build the master item_table and ID maps
# ---------------------------------------------------------------------------
item_table: dict[str, dict] = {}

# Folktails blueprints
for i, (name, classification) in enumerate(ALL_FT_BLUEPRINTS):
    item_table[f"Blueprint: {name}"] = {
        "classification": classification,
        "count": 1,
        "id": FT_BLUEPRINT_BASE + i,
    }

# Boosts
for i, (name, classification) in enumerate(BOOSTS):
    item_table[name] = {
        "classification": classification,
        "count": 1,
        "id": BOOST_BASE + i,
    }

# Filler
for i, (name, classification, count) in enumerate(FILLER_ITEMS):
    item_table[name] = {
        "classification": classification,
        "count": count,
        "id": FILLER_BASE + i,
    }

# Traps
for i, (name, classification, count) in enumerate(TRAP_ITEMS):
    item_table[name] = {
        "classification": classification,
        "count": count,
        "id": TRAP_BASE + i,
    }

# Skip — count determined at runtime by SkipCount option
item_table["Skip"] = {
    "classification": ItemClassification.useful,
    "count": 0,
    "id": SKIP_BASE,
}

item_name_to_id: dict[str, int] = {name: data["id"] for name, data in item_table.items()}


# Convenience sets for use in Rules.py / __init__.py
BLUEPRINT_ITEMS: set[str] = {f"Blueprint: {name}" for name, _ in ALL_FT_BLUEPRINTS}
PROGRESSION_BLUEPRINTS: set[str] = {
    name for name, data in item_table.items()
    if data["classification"] == ItemClassification.progression
}
