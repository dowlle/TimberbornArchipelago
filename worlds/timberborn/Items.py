from BaseClasses import Item, ItemClassification
from .ItemIds import ITEM_IDS

# ---------------------------------------------------------------------------
# Base IDs — ranges reserved per category
#   9_000_000 – 9_099_999 : Folktails blueprint items (shared + FT-only)
#   9_100_000 – 9_199_999 : IronTeeth-exclusive blueprint items
#   9_200_000 – 9_209_999 : Boost items
#   9_210_000 – 9_219_999 : Filler items
#   9_220_000 – 9_229_999 : Trap items
#   9_230_000 – 9_239_999 : Skip items
#   9_240_000 – 9_249_999 : Progressive items
#   9_250_000 – 9_259_999 : Scout items
# ---------------------------------------------------------------------------
FT_BLUEPRINT_BASE  = 9_000_000
IT_BLUEPRINT_BASE  = 9_100_000
BOOST_BASE         = 9_200_000
FILLER_BASE        = 9_210_000
TRAP_BASE          = 9_220_000
SKIP_BASE          = 9_230_000
PROGRESSIVE_BASE   = 9_240_000
SCOUT_BASE         = 9_250_000


class TimberbornItem(Item):
    game = "Timberborn"


# ---------------------------------------------------------------------------
# Blueprint items, grouped by category and tagged S(hared) / F(olktails) / I(ronTeeth).
#
# Names are exact in-game display names (verified from blueprint JSONs + enUS.csv).
# Classification:
#   progression = logically required to reach certain locations
#   useful      = helpful but not in the logic graph
#   filler      = cosmetic / decorative, padding the item pool
#
# SC = science cost in-game (informational, not used at runtime)
# Faction: S = shared (both factions), F = Folktails-only, I = IronTeeth-only
# ---------------------------------------------------------------------------

# --- WOOD ---
WOOD_BLUEPRINTS = [
    # name,                         classification,                  SC    Faction
    ("Forester",                    ItemClassification.progression), # 30   S
    ("Gear Workshop",               ItemClassification.progression), # 100  S
    ("Paper Mill",                  ItemClassification.progression), # 250  F
    ("Printing Press",              ItemClassification.progression), # 400  F
    ("Tapper's Shack",              ItemClassification.progression), # 500  S
    ("Wood Workshop",               ItemClassification.progression), # 800  S
]

# --- FOOD ---
FOOD_BLUEPRINTS = [
    ("Aquatic Farmhouse",           ItemClassification.progression), # 150  F
    ("Bakery",                      ItemClassification.progression), # 160  F
    ("Gristmill",                   ItemClassification.progression), # 180  F
    ("Beehive",                     ItemClassification.useful),      # 400  F
]

# --- HOUSING ---
HOUSING_BLUEPRINTS = [
    ("Mini Lodge",                  ItemClassification.useful),      # 50   F
    ("Double Lodge",                ItemClassification.useful),      # 150  F
    ("Triple Lodge",                ItemClassification.useful),      # 250  F
]

# --- STORAGE ---
STORAGE_BLUEPRINTS = [
    ("Medium Tank",                 ItemClassification.progression),  # 120  S
    ("Large Warehouse",             ItemClassification.useful),      # 250  S
    ("Large Tank",                  ItemClassification.useful),      # 600  S
    ("Underground Pile",            ItemClassification.useful),      # 1000 F
]

# --- WATER ---
WATER_BLUEPRINTS = [
    ("Compact Mechanical Pump",     ItemClassification.useful),      # 4000 S
    ("Badwater Pump",               ItemClassification.progression), # 250  F
    ("Fill Valve",                  ItemClassification.useful),      # 300  S
    ("Fluid Dump",                  ItemClassification.useful),      # 250  S
    ("Large Water Pump",            ItemClassification.progression), # 400  F
    ("Aquifer Drill",               ItemClassification.useful),      # 400  S
    ("Centrifuge",                  ItemClassification.progression), # 600  S
    ("Badwater Dome",               ItemClassification.useful),      # 2000 F
    ("Mechanical Fluid Pump",       ItemClassification.useful),      # 2500 F
    ("Badwater Rig",                ItemClassification.useful),      # 4000 F
]

# --- LANDSCAPING ---
LANDSCAPING_BLUEPRINTS = [
    ("Airlock",                     ItemClassification.useful),      # 300  S
    ("Levee",                       ItemClassification.progression),  # 120  S
    ("Floodgate",                   ItemClassification.progression), # 150  S
    ("Impermeable Floor",           ItemClassification.useful),      # 200  S
    ("Double Floodgate",            ItemClassification.useful),      # 250  S
    ("Contamination Barrier",       ItemClassification.useful),      # 400  F
    ("Explosives Factory",          ItemClassification.progression), # 400  S
    ("Valve",                       ItemClassification.useful),      # 500  S
    ("Triple Floodgate",            ItemClassification.useful),      # 500  S
    ("Dynamite",                    ItemClassification.useful),      # 600  S
    ("Double Dynamite",             ItemClassification.useful),      # 900  S
    ("Terrain Block",               ItemClassification.useful),      # 1000 S
    ("Triple Dynamite",             ItemClassification.useful),      # 1200 S
    ("Dirt Excavator",              ItemClassification.useful),      # 2000 S
    ("Tunnel",                      ItemClassification.useful),      # 2000 S
]

# --- METAL ---
METAL_BLUEPRINTS = [
    ("Scavenger Flag",              ItemClassification.progression), # 250  F (shared building but free for IT)
    ("Smelter",                     ItemClassification.progression), # 300  S
    ("Mine",                        ItemClassification.useful),      # 4000 F
]

# --- POWER ---
POWER_BLUEPRINTS = [
    ("Impermeable Power Shaft",      ItemClassification.useful),      # 300  S
    ("Vertical Power Shaft",        ItemClassification.useful),      # 40   S
    ("Wind Turbine",                ItemClassification.progression), # 120  F
    ("Geothermal Engine",           ItemClassification.progression), # 160  S
    ("Clutch",                      ItemClassification.useful),      # 400  S
    ("Gravity Battery",             ItemClassification.progression), # 400  S
    ("Large Wind Turbine",          ItemClassification.progression), # 1400 F
]

# --- SCIENCE PRODUCTION ---
SCIENCE_BLUEPRINTS = [
    ("Refinery",                    ItemClassification.progression), # 400  F (produces Extract)
    ("Bot Part Factory",            ItemClassification.progression), # 500  S
    ("Bot Assembler",               ItemClassification.progression), # 750  S
    ("Observatory",                 ItemClassification.useful),      # 1000 F
]

# --- DISTRICT MANAGEMENT ---
DISTRICT_BLUEPRINTS = [
    ("Builders' Hut",               ItemClassification.useful),      # 100  S
    ("District Crossing",           ItemClassification.useful),      # 600  S
]

# --- WELLBEING ---
WELLBEING_BLUEPRINTS = [
    ("Sauna",                       ItemClassification.useful),      # 300  F
    ("Domed Garden",                ItemClassification.useful),      # 800  F
    ("Shower",                      ItemClassification.progression),  # 50   F
    ("Medical Bed",                 ItemClassification.progression),  # 80   S
    ("Contemplation Spot",          ItemClassification.useful),      # 100  F
    ("Lido",                        ItemClassification.useful),      # 250  F
    ("Herbalist",                   ItemClassification.progression), # 300  F
    ("Agora",                       ItemClassification.useful),      # 400  F
    ("Carousel",                    ItemClassification.useful),      # 700  F
    ("Detailer",                    ItemClassification.useful),      # 1000 S
    ("Dance Hall",                  ItemClassification.useful),      # 1200 F
    ("Mud Pit",                     ItemClassification.useful),      # 1800 F
]

# --- PATHS ---
PATH_BLUEPRINTS = [
    ("Stairs",                      ItemClassification.progression), # 70   S
    ("Platform",                    ItemClassification.progression), # 100  S
    ("Double Platform",             ItemClassification.useful),      # 150  S
    ("Suspension Bridge 1x1",       ItemClassification.useful),      # 150  S
    ("Gate",                        ItemClassification.useful),      # 200  S
    ("Triple Platform",             ItemClassification.useful),      # 200  S
    ("Suspension Bridge 2x1",       ItemClassification.useful),      # 250  S
    ("Overhang 2x1",                ItemClassification.useful),      # 350  S
    ("Spiral Stairs",               ItemClassification.useful),      # 350  S
    ("Suspension Bridge 3x1",       ItemClassification.useful),      # 400  S
    ("Zipline Pylon",               ItemClassification.useful),      # 500  F
    ("Overhang 3x1",                ItemClassification.useful),      # 550  S
    ("Suspension Bridge 4x1",       ItemClassification.useful),      # 600  S
    ("Zipline Beam",                ItemClassification.useful),      # 600  F
    ("Zipline Station",             ItemClassification.useful),      # 700  F
    ("Metal Platform 3x3",          ItemClassification.useful),      # 1000 S
    ("Overhang 4x1",                ItemClassification.useful),      # 1000 S
    ("Suspension Bridge 5x1",       ItemClassification.useful),      # 1000 S
    ("Overhang 5x1",                ItemClassification.useful),      # 1800 S
    ("Suspension Bridge 6x1",       ItemClassification.useful),      # 1800 S
    ("Metal Platform 5x5",          ItemClassification.useful),      # 2000 S
    ("Overhang 6x1",                ItemClassification.useful),      # 3000 S
]

# --- AUTOMATION ---
AUTOMATION_BLUEPRINTS = [
    ("Lever",                       ItemClassification.useful),      # 50   S
    ("Relay",                       ItemClassification.useful),      # 80   S
    ("Flow Sensor",                 ItemClassification.useful),      # 100  S
    ("Chronometer",                 ItemClassification.useful),      # 150  S
    ("Depth Sensor",                ItemClassification.useful),      # 200  S
    ("Population Counter",          ItemClassification.useful),      # 200  S
    ("Resource Counter",            ItemClassification.useful),      # 250  S
    ("Science Counter",             ItemClassification.useful),      # 300  S
    ("Weather Station",             ItemClassification.useful),      # 300  S
    ("Contamination Sensor",        ItemClassification.useful),      # 400  S
    ("Indicator",                   ItemClassification.useful),      # 400  S
    ("Speaker",                     ItemClassification.useful),      # 500  S
    ("Power Meter",                 ItemClassification.useful),      # 600  S
    ("Timer",                       ItemClassification.useful),      # 600  S
    ("Firework Launcher",           ItemClassification.useful),      # 700  S
    ("Memory",                      ItemClassification.useful),      # 1000 S
    ("Detonator",                   ItemClassification.useful),      # 1400 S
    ("HTTP Lever",                  ItemClassification.useful),      # 5000 S
    ("HTTP Adapter",                ItemClassification.useful),      # 7500 S
]

# --- DECORATION ---
DECORATION_BLUEPRINTS = [
    ("Roof 1x1",                    ItemClassification.useful),      # 60   S
    ("Bench",                       ItemClassification.useful),      # 80   S
    ("Roof 1x2",                    ItemClassification.useful),      # 80   S
    ("Lantern",                     ItemClassification.useful),      # 100  S
    ("Hammock",                     ItemClassification.useful),      # 120  F
    ("Roof 2x2",                    ItemClassification.useful),      # 120  S
    ("Hedge",                       ItemClassification.useful),      # 150  F
    ("Roof 2x3",                    ItemClassification.useful),      # 150  S
    ("Roof 3x2",                    ItemClassification.useful),      # 150  S
    ("Stream Gauge",                ItemClassification.useful),      # 150  S
    ("Wood Fence",                  ItemClassification.useful),      # 150  S
    ("Scarecrow",                   ItemClassification.useful),      # 200  F
    ("Weathervane",                 ItemClassification.useful),      # 250  F
    ("Beaver Statue",               ItemClassification.useful),      # 500  S
    ("Bulletin Pole",               ItemClassification.useful),      # 600  F
    ("Pole Banner",                 ItemClassification.useful),      # 700  S
    ("Square Banner",               ItemClassification.useful),      # 700  S
]

# --- FOLKTAILS MONUMENTS (pre-Wonder) ---
FT_MONUMENT_BLUEPRINTS = [
    ("Hall of Abundance",            ItemClassification.useful),      # 15000 F
    ("Farmer Monument",             ItemClassification.useful),      # 1000  F
    ("Brazier of Bonding",          ItemClassification.useful),      # 3000  F
    ("Fountain of Joy",             ItemClassification.useful),      # 12000 F
    # Earth Recultivator (20000) is the FT wonder — not a received item
]

# ---------------------------------------------------------------------------
# Folktails blueprint categories. Permanent IDs live in ItemIds.py and do not
# depend on category order.
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
    + FT_MONUMENT_BLUEPRINTS
)

# ---------------------------------------------------------------------------
# Iron Teeth exclusive blueprint items.
# These are buildings that only IT has (not in FT).
# Names verified from enUS.csv localization.
# ---------------------------------------------------------------------------

# --- IT WOOD ---
IT_WOOD_BLUEPRINTS: list[tuple[str, ItemClassification]] = [
    # IndustrialLumberMill is free (SC=0), not in pool
]

# --- IT FOOD ---
IT_FOOD_BLUEPRINTS = [
    # FarmHouse (SC=0) and Fermenter (SC=0) are free
    ("Oil Press",                   ItemClassification.progression), # 120
    ("Hydroponic Garden",           ItemClassification.useful),      # 200
    ("Food Factory",                ItemClassification.progression), # 300
    ("Coffee Brewery",              ItemClassification.progression), # 500
]

# --- IT HOUSING ---
IT_HOUSING_BLUEPRINTS = [
    # Barrack (SC=0) and BreedingPod (SC=0) are free
    ("Rowhouse",                    ItemClassification.useful),      # 180
    ("Large Barrack",               ItemClassification.useful),      # 400
    ("Large Rowhouse",              ItemClassification.useful),      # 600
    ("Advanced Breeding Pod",       ItemClassification.useful),      # 1000
]

# --- IT STORAGE ---
IT_STORAGE_BLUEPRINTS: list[tuple[str, ItemClassification]] = [
    # SmallIndustrialPile (SC=0) and LargeIndustrialPile (SC=0) are free
]

# --- IT WATER ---
IT_WATER_BLUEPRINTS = [
    # DeepWaterPump (SC=0) is free
    ("Deep Badwater Pump",          ItemClassification.progression), # 250
    ("Deep Mechanical Fluid Pump",  ItemClassification.useful),      # 2500
    ("Badwater Discharge",          ItemClassification.useful),      # 4000
]

# --- IT LANDSCAPING ---
IT_LANDSCAPING_BLUEPRINTS = [
    ("Irrigation Barrier",          ItemClassification.useful),      # 400
]

# --- IT METAL ---
IT_METAL_BLUEPRINTS = [
    ("Metalsmith",                  ItemClassification.progression), # 150; Dance Pit needs Metal Parts
    ("Efficient Mine",              ItemClassification.useful),      # 4000
]

# --- IT POWER ---
IT_POWER_BLUEPRINTS = [
    # CompactWaterWheel (SC=0) and LargePowerWheel (SC=0) are free
    ("Large Water Wheel",           ItemClassification.useful),      # 200
    ("Steam Engine",                ItemClassification.progression), # 400
]

# --- IT SCIENCE ---
IT_SCIENCE_BLUEPRINTS = [
    ("Charging Station",            ItemClassification.useful),      # 200
    ("Control Tower",               ItemClassification.useful),      # 1000
    ("Numbercruncher",              ItemClassification.useful),      # 1500
    ("Grease Factory",              ItemClassification.progression), # 2000
]

# --- IT WELLBEING ---
IT_WELLBEING_BLUEPRINTS = [
    ("Massager",                    ItemClassification.useful),      # 150
    ("Dance Pit",                   ItemClassification.useful),      # 1800
    ("Double Shower",               ItemClassification.useful),      # 50
    ("Scratcher",                   ItemClassification.useful),      # 100
    ("Swimming Pool",               ItemClassification.useful),      # 250
    ("Decontamination Pod",         ItemClassification.useful),      # 400
    ("Exercise Plaza",              ItemClassification.useful),      # 400
    ("Wind Tunnel",                 ItemClassification.useful),      # 700
    ("Motivatorium",                ItemClassification.useful),      # 1200
    ("Mud Bath",                    ItemClassification.useful),      # 1800
]

# --- IT PATHS ---
IT_PATH_BLUEPRINTS = [
    ("Impermeable Tubeway",          ItemClassification.useful),      # 800
    ("Tubeway",                     ItemClassification.useful),      # 500
    ("Vertical Tubeway",            ItemClassification.useful),      # 600
    ("Tubeway Station",             ItemClassification.useful),      # 700
]

# --- IT DECORATION ---
IT_DECORATION_BLUEPRINTS = [
    ("Brazier",                     ItemClassification.useful),      # 150
    ("Metal Fence",                 ItemClassification.useful),      # 150
    ("Beaver Bust",                 ItemClassification.useful),      # 200
    ("Bell",                        ItemClassification.useful),      # 500
    ("Decorative Clock",            ItemClassification.useful),      # 600
]

# --- IT MONUMENTS (pre-Wonder) ---
IT_MONUMENT_BLUEPRINTS = [
    ("Arch of Progress",            ItemClassification.useful),      # 15000
    ("Laborer Monument",            ItemClassification.useful),      # 1000
    ("Flame of Unity",              ItemClassification.useful),      # 3000
    ("Tribute to Ingenuity",        ItemClassification.useful),      # 12000
    # Earth Repopulator (20000) is the IT wonder — not a received item
]

# ---------------------------------------------------------------------------
# IronTeeth-exclusive blueprint categories. IDs are explicit in ItemIds.py.
# ---------------------------------------------------------------------------
ALL_IT_ONLY_BLUEPRINTS: list[tuple[str, ItemClassification]] = (
    IT_WOOD_BLUEPRINTS
    + IT_FOOD_BLUEPRINTS
    + IT_HOUSING_BLUEPRINTS
    + IT_STORAGE_BLUEPRINTS
    + IT_WATER_BLUEPRINTS
    + IT_LANDSCAPING_BLUEPRINTS
    + IT_METAL_BLUEPRINTS
    + IT_POWER_BLUEPRINTS
    + IT_SCIENCE_BLUEPRINTS
    + IT_WELLBEING_BLUEPRINTS
    + IT_PATH_BLUEPRINTS
    + IT_DECORATION_BLUEPRINTS
    + IT_MONUMENT_BLUEPRINTS
)

# ---------------------------------------------------------------------------
# Faction membership sets — used to build per-faction pools.
# Items tagged "F" above are FT-only; all others in ALL_FT_BLUEPRINTS are shared.
# ScavengerFlag is a shared building but free (SC=0) for IT, so it's FT-only in AP.
# ---------------------------------------------------------------------------
_FT_ONLY_NAMES: set[str] = {
    "Hall of Abundance", "Sauna", "Domed Garden",
    # Wood
    "Paper Mill", "Printing Press",
    # Food
    "Aquatic Farmhouse", "Bakery", "Gristmill", "Beehive",
    # Housing
    "Mini Lodge", "Double Lodge", "Triple Lodge",
    # Storage
    "Underground Pile",
    # Water
    "Badwater Pump", "Large Water Pump", "Badwater Dome",
    "Mechanical Fluid Pump", "Badwater Rig",
    # Landscaping
    "Contamination Barrier",
    # Metal
    "Scavenger Flag", "Mine",
    # Power
    "Wind Turbine", "Large Wind Turbine",
    # Science
    "Refinery", "Observatory",
    # Wellbeing
    "Shower", "Contemplation Spot", "Lido", "Herbalist",
    "Agora", "Carousel", "Dance Hall", "Mud Pit",
    # Paths
    "Zipline Pylon", "Zipline Beam", "Zipline Station",
    # Decoration
    "Hammock", "Hedge", "Scarecrow", "Weathervane", "Bulletin Pole",
    # Monuments
    "Farmer Monument", "Brazier of Bonding", "Fountain of Joy",
}

# Shared items = everything in ALL_FT_BLUEPRINTS that is NOT FT-only
_SHARED_NAMES: set[str] = {name for name, _ in ALL_FT_BLUEPRINTS} - _FT_ONLY_NAMES

# ---------------------------------------------------------------------------
# Passive boosts (received from the multiworld, applied globally)
# ---------------------------------------------------------------------------
BOOSTS: list[tuple[str, ItemClassification]] = [
    ("Boost: Faster Movement Speed",        ItemClassification.useful),
    ("Boost: Increased Carrying Capacity",  ItemClassification.useful),
    ("Boost: Faster Working Speed",         ItemClassification.useful),
    ("Boost: Faster Beaver Growth",         ItemClassification.useful),
    ("Boost: Longer Life Expectancy",       ItemClassification.useful),
    ("Boost: Better Woodcutting Chance",    ItemClassification.useful),
]

# ---------------------------------------------------------------------------
# Scout items — reveal building names on a shop path
# ---------------------------------------------------------------------------
SCOUT_ITEMS: list[tuple[str, ItemClassification]] = [
    ("Scout: Path A",                       ItemClassification.useful),
    ("Scout: Path B",                       ItemClassification.useful),
    ("Scout: Path C",                       ItemClassification.useful),
    ("Scout: Path D",                       ItemClassification.useful),
]

# ---------------------------------------------------------------------------
# Legacy filler — fixed-amount resource items from seeds generated before the
# resource packages below. Kept so existing seeds and IDs keep working.
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
# Resource packages — goods delivered to storage, drawn into the pool by
# faction weight. Names carry no amount: the delivered amount is the base
# amount scaled by the resource_package_size option, and slot_data tells the
# client the final amount. The legacy "Filler: N Good" items above keep their
# names and IDs for existing seeds but are no longer placed.
# ---------------------------------------------------------------------------
RESOURCE_PACKAGES: list[tuple[str, str, int, int, int]] = [
    # name,                            good id,             base, FT, IT weight
    ("Package: Logs",                 "Log",                100,  4, 4),
    ("Package: Planks",               "Plank",              50,   5, 5),
    ("Package: Gears",                "Gear",               25,   5, 5),
    ("Package: Treated Planks",       "TreatedPlank",       20,   4, 4),
    ("Package: Metal Blocks",         "MetalBlock",         15,   5, 4),
    ("Package: Scrap Metal",          "ScrapMetal",         30,   3, 2),
    ("Package: Pine Resin",           "PineResin",          20,   2, 3),
    ("Package: Extract",              "Extract",            15,   2, 2),
    ("Package: Explosives",           "Explosives",         10,   1, 1),
    ("Package: Water",                "Water",              60,   3, 3),
    ("Package: Berries",              "Berries",            60,   2, 2),
    ("Package: Dirt",                 "Dirt",               40,   0, 1),
    ("Package: Paper",                "Paper",              40,   2, 0),
    ("Package: Books",                "Book",               10,   1, 0),
    ("Package: Antidote",             "Antidote",           10,   1, 0),
    ("Package: Biofuel",              "Biofuel",            25,   1, 0),
    ("Package: Bread",                "Bread",              60,   4, 0),
    ("Package: Grilled Potatoes",     "GrilledPotato",      60,   3, 0),
    ("Package: Cattail Crackers",     "CattailCracker",     60,   2, 0),
    ("Package: Maple Pastries",       "MaplePastry",        30,   2, 0),
    ("Package: Grilled Chestnuts",    "GrilledChestnut",    40,   1, 0),
    ("Package: Grilled Spadderdock",  "GrilledSpadderdock", 45,   1, 0),
    ("Package: Carrots",              "Carrot",             40,   1, 0),
    ("Package: Sunflower Seeds",      "SunflowerSeeds",     30,   1, 0),
    ("Package: Metal Parts",          "MetalPart",          10,   0, 2),
    ("Package: Coffee",               "Coffee",             30,   0, 2),
    ("Package: Grease",               "Grease",             10,   0, 1),
    ("Package: Corn Rations",         "CornRation",         60,   0, 4),
    ("Package: Fermented Cassava",    "FermentedCassava",   60,   0, 3),
    ("Package: Eggplant Rations",     "EggplantRation",     60,   0, 2),
    ("Package: Fermented Soybean",    "FermentedSoybean",   60,   0, 2),
    ("Package: Kohlrabi",             "Kohlrabi",           40,   0, 2),
    ("Package: Mangrove Fruit",       "MangroveFruit",      40,   0, 2),
]

RESOURCE_PACKAGE_GOODS: dict[str, str] = {name: good for name, good, _, _, _ in RESOURCE_PACKAGES}
RESOURCE_PACKAGE_BASE_AMOUNTS: dict[str, int] = {
    name: amount for name, _, amount, _, _ in RESOURCE_PACKAGES
}


def get_resource_package_weights(faction: str) -> dict[str, int]:
    """Pool weight of every resource package the faction can store (weight > 0)."""
    column = 4 if faction == "IronTeeth" else 3
    return {row[0]: row[column] for row in RESOURCE_PACKAGES if row[column] > 0}


def scale_package_amount(base_amount: int, percent: int) -> int:
    """Base amount scaled by a percentage, rounded half up, at least 1.

    Integer arithmetic so the client (ResourcePackages.ScaleAmount) gets
    exactly the same result.
    """
    return max(1, (base_amount * percent + 50) // 100)


# ---------------------------------------------------------------------------
# Traps — negative effects sent from/to other players
# ---------------------------------------------------------------------------
TRAP_ITEMS: list[tuple[str, ItemClassification, int]] = [
    # Consolidated weather trap: the game's own HazardousWeatherRandomizer
    # picks drought or badtide based on map conditions. Replaces the previous
    # separate "Trap: Early Drought" and "Trap: Badwater Leak" entries.
    ("Trap: Hazardous Weather",         ItemClassification.trap,     5),
    ("Trap: Hungry Beavers",            ItemClassification.trap,     3),
    ("Trap: Thirsty Beavers",           ItemClassification.trap,     2),
]

# ---------------------------------------------------------------------------
# Build the master item_table and ID maps
# ---------------------------------------------------------------------------
item_table: dict[str, dict] = {}

# Folktails blueprints (shared + FT-only) — IDs frozen from FT_BLUEPRINT_BASE
for name, classification in ALL_FT_BLUEPRINTS:
    item_table[f"Blueprint: {name}"] = {
        "classification": classification,
        "count": 1,
        "id": ITEM_IDS[f"Blueprint: {name}"],
    }

# IronTeeth-exclusive blueprints — IDs from IT_BLUEPRINT_BASE
for name, classification in ALL_IT_ONLY_BLUEPRINTS:
    item_table[f"Blueprint: {name}"] = {
        "classification": classification,
        "count": 1,
        "id": ITEM_IDS[f"Blueprint: {name}"],
    }

# Boosts
for name, classification in BOOSTS:
    item_table[name] = {
        "classification": classification,
        "count": 1,
        "id": ITEM_IDS[name],
    }

# Scouts
for name, classification in SCOUT_ITEMS:
    item_table[name] = {
        "classification": classification,
        "count": 1,
        "id": ITEM_IDS[name],
    }

# Filler
for name, classification, count in FILLER_ITEMS:
    item_table[name] = {
        "classification": classification,
        "count": count,
        "id": ITEM_IDS[name],
    }

# Resource packages — count is decided at generation time by faction weight
for name, _, _, _, _ in RESOURCE_PACKAGES:
    item_table[name] = {
        "classification": ItemClassification.filler,
        "count": 0,
        "id": ITEM_IDS[name],
    }

# Traps
for name, classification, count in TRAP_ITEMS:
    item_table[name] = {
        "classification": classification,
        "count": count,
        "id": ITEM_IDS[name],
    }

# Skip — count determined at runtime by SkipCount option
item_table["Skip"] = {
    "classification": ItemClassification.useful,
    "count": 0,
    "id": ITEM_IDS["Skip"],
}

# Progressive items use explicit IDs from ItemIds.py, independent of chain order.
from .ProgressiveItems import SHARED_PROGRESSIVE_CHAINS, FT_PROGRESSIVE_CHAINS, IT_PROGRESSIVE_CHAINS

_ALL_PROGRESSIVE_CHAINS: list[tuple[str, tuple[str, ...]]] = (
    list(SHARED_PROGRESSIVE_CHAINS.items())
    + list(FT_PROGRESSIVE_CHAINS.items())
    + list(IT_PROGRESSIVE_CHAINS.items())
)

for prog_name, chain in _ALL_PROGRESSIVE_CHAINS:
    item_table[prog_name] = {
        "classification": ItemClassification.progression,
        "count": len(chain),
        "id": ITEM_IDS[prog_name],
    }

item_name_to_id: dict[str, int] = {name: data["id"] for name, data in item_table.items()}


# ---------------------------------------------------------------------------
# Convenience helpers for faction-aware item pools
# ---------------------------------------------------------------------------
BLUEPRINT_ITEMS: set[str] = {f"Blueprint: {name}" for name, _ in ALL_FT_BLUEPRINTS}


def get_blueprint_items(
    faction: str,
    progressive_chains: dict[str, tuple[str, ...]] | None = None,
) -> list[str]:
    """Return the item names for the given faction's blueprint pool.

    When *progressive_chains* is provided, individual buildings that belong
    to a chain are replaced by N copies of the progressive item (one per
    chain member).  Returns a list (not a set) so duplicate progressive
    entries are preserved for correct item counts.
    """
    if faction == "IronTeeth":
        shared = {f"Blueprint: {n}" for n, _ in ALL_FT_BLUEPRINTS if n in _SHARED_NAMES}
        it_only = {f"Blueprint: {n}" for n, _ in ALL_IT_ONLY_BLUEPRINTS}
        base = shared | it_only
    else:
        base = set(BLUEPRINT_ITEMS)

    if not progressive_chains:
        return sorted(base)

    # Build reverse lookup: building name → progressive item name
    building_to_prog: dict[str, str] = {}
    for prog_name, chain in progressive_chains.items():
        for building in chain:
            building_to_prog[building] = prog_name

    result: list[str] = []
    prog_added: dict[str, int] = {}
    for bp_name in sorted(base):
        # Strip "Blueprint: " prefix to check against chain members
        building = bp_name.removeprefix("Blueprint: ")
        if building in building_to_prog:
            prog_name = building_to_prog[building]
            prog_added.setdefault(prog_name, 0)
            prog_added[prog_name] += 1
            # Add one copy of the progressive item per chain member
            result.append(prog_name)
        else:
            result.append(bp_name)

    return result


def get_building_names(faction: str) -> list[str]:
    """Return the list of building names for the given faction (for ShopLayout)."""
    if faction == "IronTeeth":
        shared = [n for n, _ in ALL_FT_BLUEPRINTS if n in _SHARED_NAMES]
        it_only = [n for n, _ in ALL_IT_ONLY_BLUEPRINTS]
        return shared + it_only
    return [name for name, _ in ALL_FT_BLUEPRINTS]


PROGRESSION_BLUEPRINTS: set[str] = {
    name for name, data in item_table.items()
    if data["classification"] == ItemClassification.progression
}
