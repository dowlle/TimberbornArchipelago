"""
Maps each building to its required resource tier based on construction materials.

Tier 1: Log, Plank (free resources)
Tier 2: Gear, Paper, PineResin (Gear Workshop chain)
Tier 3: MetalBlock, ScrapMetal (Smelter chain)
Tier 4: TreatedPlank, Dirt, Extract, Explosives (advanced processing)
Tier 5: MetalPart, Grease (Bot Part Factory / late-game)

Building tier = max tier of all its construction materials.
Generated from blueprint JSONs via scripts/extract_building_tiers.py.
"""
from __future__ import annotations

# Shared + Folktails buildings (extracted from Folktails blueprint JSONs)
BUILDING_TIERS: dict[str, int] = {
    # --- Tier 1 ---
    "Forester": 1,
    "Gear Workshop": 1,
    "Aquatic Farmhouse": 1,
    "Mini Lodge": 1,
    "Double Lodge": 1,
    "Triple Lodge": 1,
    "Large Warehouse": 1,
    "Fluid Dump": 1,
    "Levee": 1,
    "Floodgate": 1,
    "Double Floodgate": 1,
    "Triple Floodgate": 1,
    "Scavenger Flag": 1,
    "Wind Turbine": 1,
    "Geothermal Engine": 1,
    "Builders' Hut": 1,
    "District Crossing": 1,
    "Shower": 1,
    "Medical Bed": 1,
    "Contemplation Spot": 1,
    "Lido": 1,
    "Agora": 1,
    "Stairs": 1,
    "Platform": 1,
    "Double Platform": 1,
    "Suspension Bridge 1x1": 1,
    "Triple Platform": 1,
    "Suspension Bridge 2x1": 1,
    "Suspension Bridge 3x1": 1,
    "Suspension Bridge 4x1": 1,
    "Suspension Bridge 5x1": 1,
    "Suspension Bridge 6x1": 1,
    "Roof 1x1": 1,
    "Bench": 1,
    "Roof 1x2": 1,
    "Lantern": 1,
    "Hammock": 1,
    "Roof 2x2": 1,
    "Hedge": 1,
    "Roof 2x3": 1,
    "Roof 3x2": 1,
    "Stream Gauge": 1,
    "Wood Fence": 1,
    "Weathervane": 1,
    "Beaver Statue": 1,
    "Farmer Monument": 1,
    "Brazier of Bonding": 1,
    # --- Tier 2 ---
    "Paper Mill": 2,
    "Tapper's Shack": 2,
    "Wood Workshop": 2,
    "Bakery": 2,
    "Gristmill": 2,
    "Beehive": 2,
    "Medium Tank": 2,
    "Underground Pile": 2,
    "Vertical Power Shaft": 2,
    "Large Wind Turbine": 2,
    "Observatory": 2,
    "Herbalist": 2,
    "Lever": 2,
    "Relay": 2,
    "Flow Sensor": 2,
    "Chronometer": 2,
    "Population Counter": 2,
    "Resource Counter": 2,
    "Scarecrow": 2,
    # --- Tier 3 ---
    "Printing Press": 3,
    "Large Tank": 3,
    "Badwater Pump": 3,
    "Fill Valve": 3,
    "Aquifer Drill": 3,
    "Centrifuge": 3,
    "Badwater Dome": 3,
    "Impermeable Floor": 3,
    "Contamination Barrier": 3,
    "Explosives Factory": 3,
    "Smelter": 3,
    "Clutch": 3,
    "Gravity Battery": 3,
    "Refinery": 3,
    "Bot Part Factory": 3,
    "Bot Assembler": 3,
    "Carousel": 3,
    "Gate": 3,
    "Overhang 2x1": 3,
    "Zipline Pylon": 3,
    "Overhang 3x1": 3,
    "Zipline Beam": 3,
    "Zipline Station": 3,
    "Metal Platform 3x3": 3,
    "Overhang 4x1": 3,
    "Overhang 5x1": 3,
    "Metal Platform 5x5": 3,
    "Overhang 6x1": 3,
    "Depth Sensor": 3,
    "Science Counter": 3,
    "Contamination Sensor": 3,
    "Indicator": 3,
    "Speaker": 3,
    "Power Meter": 3,
    "HTTP Lever": 3,
    "HTTP Adapter": 3,
    "Bulletin Pole": 3,
    # --- Tier 4 ---
    "Large Water Pump": 4,
    "Mechanical Fluid Pump": 4,
    "Badwater Rig": 4,
    "Valve": 4,
    "Dynamite": 4,
    "Double Dynamite": 4,
    "Terrain Block": 4,
    "Triple Dynamite": 4,
    "Dirt Excavator": 4,
    "Tunnel": 4,
    "Mine": 4,
    "Detailer": 4,
    "Dance Hall": 4,
    "Mud Pit": 4,
    "Spiral Stairs": 4,
    "Weather Station": 4,
    "Timer": 4,
    "Firework Launcher": 4,
    "Memory": 4,
    "Detonator": 4,
    "Pole Banner": 4,
    "Square Banner": 4,
    "Fountain of Joy": 4,
}

# IronTeeth-exclusive buildings
IT_BUILDING_TIERS: dict[str, int] = {
    # --- Tier 1 ---
    "Rowhouse": 1,
    "Large Barrack": 1,
    "Large Rowhouse": 1,
    "Large Water Wheel": 1,
    "Double Shower": 1,
    "Scratcher": 1,
    "Swimming Pool": 1,
    "Laborer Monument": 1,
    # --- Tier 3 ---
    "Food Factory": 3,
    "Metalsmith": 3,
    "Control Tower": 3,
    "Decontamination Pod": 3,
    "Wind Tunnel": 3,
    "Tubeway": 3,
    "Vertical Tubeway": 3,
    "Tubeway Station": 3,
    "Brazier": 3,
    "Bell": 3,
    "Decorative Clock": 3,
    # --- Tier 4 ---
    "Coffee Brewery": 4,
    "Advanced Breeding Pod": 4,
    "Deep Mechanical Fluid Pump": 4,
    "Badwater Discharge": 4,
    "Irrigation Barrier": 4,
    "Efficient Mine": 4,
    "Grease Factory": 4,
    "Motivatorium": 4,
    "Mud Bath": 4,
    "Tribute to Ingenuity": 4,
    # --- Tier 5 ---
    "Oil Press": 5,
    "Hydroponic Garden": 5,
    "Deep Badwater Pump": 5,
    "Steam Engine": 5,
    "Charging Station": 5,
    "Numbercruncher": 5,
    "Exercise Plaza": 5,
    "Metal Fence": 5,
    "Beaver Bust": 5,
    "Flame of Unity": 5,
}

# Shared buildings where IT has different construction costs than FT
IT_SHARED_OVERRIDES: dict[str, int] = {
    "Beaver Statue": 3,
    "Explosives Factory": 5,
    "Population Counter": 5,
    "Resource Counter": 5,
    "Science Counter": 5,
}


def get_building_tier(building_name: str, faction: str = "Folktails") -> int:
    """Return the resource tier (1-5) for a building, checking faction overrides."""
    if faction == "IronTeeth":
        if building_name in IT_BUILDING_TIERS:
            return IT_BUILDING_TIERS[building_name]
        if building_name in IT_SHARED_OVERRIDES:
            return IT_SHARED_OVERRIDES[building_name]
    return BUILDING_TIERS.get(building_name, 1)
