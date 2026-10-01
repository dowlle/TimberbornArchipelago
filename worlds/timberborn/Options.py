from dataclasses import dataclass
from Options import (Choice, Range, Toggle, OptionSet, PerGameCommonOptions, StartInventoryPool,
                     Visibility)


class _ClampedRange(Range):
    """A Range that clamps out-of-range numbers instead of failing, so YAMLs written
    for an older, wider range still generate."""

    def __init__(self, value: int):
        super().__init__(min(max(int(value), self.range_start), self.range_end))


class Faction(Choice):
    """
    Which beaver faction to play as?
    - folktails: Nature-loving beavers with unique buildings like Beehive, Aquatic Farmhouse, Bakery.
    - iron_teeth: Industrial beavers with unique buildings like Steam Engine, Rowhouse, Coffee Brewery.

    Use ``random`` in YAML for a random faction per seed.
    The client will block connection if you load the wrong faction in-game.

    NOTE: Iron Teeth must be unlocked in-game before selecting it here.
    Unlock it by reaching average well-being 8 in a Folktails game first,
    or the Archipelago mod may auto-unlock it for you.
    """
    display_name = "Faction"
    option_folktails = 0
    option_iron_teeth = 1
    default = 0


class GoalSelection(OptionSet):
    """
    Which victory conditions are in play? Pick any combination, or use
    ``random-range-1-3`` in YAML to randomize how many are active.

    Possible values:
    - **Wonder**: Build your faction's Wonder building.
    - **Population**: Reach the target beaver population (see population_goal).
    - **Droughts**: Survive a number of drought cycles (see drought_cycles_goal).
    - **Badtides**: Survive a number of badtide cycles (see badtide_cycles_goal).
    - **Well-being**: Reach a target average well-being level (see wellbeing_goal).
    - **Bots**: Construct a number of bots (see bots_goal).
    - **Water Storage**: Reach a water storage capacity threshold (see water_storage_goal).

    At least one goal must be selected. If the resolved set is empty,
    the game falls back to Wonder.
    """
    display_name = "Goal Selection"
    valid_keys = {
        "Wonder",
        "Population",
        "Droughts",
        "Badtides",
        "Well-being",
        "Bots",
        "Water Storage",
    }
    default = {"Wonder"}


class GoalRequirement(Choice):
    """
    Of the goals selected in *Goal Selection*, how many must be completed?
    - any: Complete ANY ONE of the selected goals to win.
    - all: Complete ALL selected goals to win.
    """
    display_name = "Goal Requirement"
    option_any = 0
    option_all = 1
    default = 0


class RandomizationStyle(Choice):
    """
    Which buildings are shuffled into the multiworld?
    - shuffle: Only buildings that normally cost Science Points are randomized.
    - grand_chaos: All buildings (including basic ones like Paths and Stockpiles) are randomized.
    """
    display_name = "Randomization Style"
    option_shuffle = 0
    option_grand_chaos = 1
    default = 0


class PopulationMode(Choice):
    """
    When the 'Population' goal is active, what counts toward the target?
    - beavers_only: Only beavers count.
    - bots_only: Only bots count.
    - beavers_and_bots: Both beavers and bots count together.
    """
    display_name = "Population Mode"
    option_beavers_only = 0
    option_bots_only = 1
    option_beavers_and_bots = 2
    default = 0


class PopulationGoal(Range):
    """When 'Population' goal is active, the total count required (see population_mode)."""
    display_name = "Population Goal"
    range_start = 10
    range_end = 500
    default = 100


class DroughtCyclesGoal(_ClampedRange):
    """When 'Droughts' goal is active, the number of droughts to survive.
    A drought counts when it ends, and only droughts after you connect count.
    About one cycle per drought; logic asks for more water control the more droughts
    you need (early up to 5, mid up to 15, late above). Older YAML values above 40 are
    lowered to 40."""
    display_name = "Drought Cycles Goal"
    range_start = 5
    range_end = 40
    default = 15


class BadtideCyclesGoal(_ClampedRange):
    """When 'Badtides' goal is active, the number of badtides to survive.
    A badtide counts when it ends, and only badtides after you connect count.
    Badtides start after a few cycles and come in about 40% of cycles, so each takes
    two to three cycles. Logic asks for floodgates, tanks and cures (early up to 3,
    mid up to 10, late above). Older YAML values above 20 are lowered to 20."""
    display_name = "Badtide Cycles Goal"
    range_start = 1
    range_end = 20
    default = 5


class WellbeingGoal(Range):
    """When 'Well-being' goal is active, the average well-being level to reach.
    In-game well-being ranges from roughly 0 to 50 in a mature settlement."""
    display_name = "Well-being Goal"
    range_start = 5
    range_end = 50
    default = 15


class BotsGoal(Range):
    """When 'Bots' goal is active, the number of bots to construct."""
    display_name = "Bots Goal"
    range_start = 1
    range_end = 50
    default = 10


class WaterStorageGoal(Range):
    """When 'Water Storage' goal is active, the water storage capacity to reach."""
    display_name = "Water Storage Goal"
    range_start = 500
    range_end = 50000
    default = 5000


class DroughtDifficulty(Range):
    """Removed: this option never had an effect. Hazardous Weather traps set the
    difficulty instead. Kept hidden so older YAMLs that set it still generate."""
    display_name = "Drought Difficulty (removed)"
    range_start = 1
    range_end = 5
    default = 3
    visibility = Visibility.none


class IncludeTraps(Toggle):
    """If enabled, trap items (Hazardous Weather, Hungry Beavers, Thirsty Beavers) can appear in the item pool.
    This is the master switch for traps. Trap Percentage sets how many traps there are, and the
    trap weight options set how often each trap type appears."""
    display_name = "Include Traps"
    default = 1


class TrapPercentage(Range):
    """Percentage of the filler slots that become traps. Filler slots are the item slots
    left after blueprints, boosts, scouts and skips; the ones that do not become traps
    get resource packages. The trap count is rounded half up: the default 15 gives
    10 traps from the 69 filler slots of a default seed. 0 means no traps.
    Include Traps must be on for any trap to appear, and the trap weights set the mix."""
    display_name = "Trap Percentage"
    range_start = 0
    range_end = 100
    default = 15


class _TrapWeight(Range):
    range_start = 0
    range_end = 100


class HazardousWeatherTrapWeight(_TrapWeight):
    """How often Hazardous Weather traps appear, relative to the other trap weights.
    Each trap in the pool is drawn with a chance of this weight divided by the sum of
    all three trap weights. 0 removes this trap. If all three weights are 0, there are
    no traps at all. Include Traps must be on for any trap to appear."""
    display_name = "Hazardous Weather Trap Weight"
    default = 50


class HungryBeaversTrapWeight(_TrapWeight):
    """How often Hungry Beavers traps appear, relative to the other trap weights.
    Each trap in the pool is drawn with a chance of this weight divided by the sum of
    all three trap weights. 0 removes this trap. If all three weights are 0, there are
    no traps at all. Include Traps must be on for any trap to appear."""
    display_name = "Hungry Beavers Trap Weight"
    default = 30


class ThirstyBeaversTrapWeight(_TrapWeight):
    """How often Thirsty Beavers traps appear, relative to the other trap weights.
    Each trap in the pool is drawn with a chance of this weight divided by the sum of
    all three trap weights. 0 removes this trap. If all three weights are 0, there are
    no traps at all. Include Traps must be on for any trap to appear."""
    display_name = "Thirsty Beavers Trap Weight"
    default = 20


class TrapMode(Choice):
    """
    How Hazardous Weather traps behave when a hazardous cycle is already active or pending:
    - queue: Weather traps wait until the current weather ends, then trigger in order.
    - skip: Weather traps are discarded if weather is already active.
    """
    display_name = "Trap Mode"
    option_queue = 0
    option_skip = 1
    default = 0


class MaxScienceCost(Range):
    """Maximum science cost for the most expensive shop location."""
    display_name = "Max Science Cost"
    range_start = 1000
    range_end = 20000
    default = 5000


class ScienceCostMultiplier(Range):
    """
    Percentage multiplier applied to all shop science costs.
    50 = half price (faster unlocks), 100 = default, 200 = double price (slower).
    """
    display_name = "Science Cost Multiplier"
    range_start = 10
    range_end = 1000
    default = 100


class SkipCount(Range):
    """Number of Skip items added to the item pool. Skips let you check a shop location for free."""
    display_name = "Skip Count"
    range_start = 0
    range_end = 10
    default = 3


class ProgressiveItems(Choice):
    """
    Merge related size-upgrade buildings into progressive item chains.
    Each receipt of a progressive item unlocks the next tier in the sequence
    (e.g. Progressive Platforms: Platform → Double Platform → Triple Platform).
    - off: Each building is a separate item (classic behavior).
    - grouped_random: Each chain is randomly enabled or disabled per seed.
    - on: All progressive chains are active.
    """
    display_name = "Progressive Items"
    option_off = 0
    option_grouped_random = 1
    option_on = 2
    default = 2


class IncludePopulationMilestones(Toggle):
    """Include population milestone locations (beaver count thresholds, first born/grown)."""
    display_name = "Include Population Milestones"
    default = 1


class IncludeWellbeingMilestones(Toggle):
    """Include well-being milestone locations (well-being level thresholds)."""
    display_name = "Include Well-being Milestones"
    default = 1


class IncludeSurvivalMilestones(Toggle):
    """Include drought and badtide survival milestone locations."""
    display_name = "Include Survival Milestones"
    default = 1


class IncludeWonderMilestone(Toggle):
    """Include the Wonder completion milestone location."""
    display_name = "Include Wonder Milestone"
    default = 1


class IncludeResourceMilestones(Toggle):
    """Include resource-threshold milestone locations (e.g. Reach 500 Logs, Reach 250 Metal Blocks).
    Each location fires once when your global resource count first passes the threshold.
    Provides mid-game progression anchors tied to your production chain development.
    Resource Milestone Set chooses how many are included."""
    display_name = "Include Resource Milestones"
    default = 1


class ResourceMilestoneSet(Choice):
    """
    Which resource milestones are included when Include Resource Milestones is on.
    Each milestone fires when your stock of that good first reaches the threshold.
    A milestone is only in logic once you can produce the good with your own
    buildings; received resource packages never count for logic.
    - classic: the original 13 milestones (Logs, Planks, Gears, Metal Blocks,
      Treated Planks, Scrap Metal, and 500 Bread or 500 Corn Rations).
    - lite: classic plus 18 early steps (10, 25 and 50 of the classic goods,
      100 and 250 Logs, 50 and 100 Planks).
    - full: lite plus 30 more milestones for other goods of your faction
      (food, Pine Resin, Water, Extract, Explosives and more). 61 in total.
    """
    display_name = "Resource Milestone Set"
    option_classic = 0
    option_lite = 1
    option_full = 2
    default = 2


class ResourcePackageSize(Range):
    """
    Percentage applied to the amount of every resource package you receive.
    100 = default amounts (for example 100 Logs or 60 Bread), 50 = half, 300 = triple.
    Amounts are rounded, and every package delivers at least 1.
    """
    display_name = "Resource Package Size"
    range_start = 10
    range_end = 1000
    default = 100


class GoodsDelivery(Choice):
    """
    Where received resource packages are delivered in your colony.
    - district_center: into the District Center with the most beavers, the way the game
      gives your starting goods. Its workers haul the goods to storage, builders can use
      them right away, and beavers eat and drink from it. Goods it does not take go to
      storage.
    - storage: into finished storage buildings (warehouses, piles, tanks) that take the
      good and have room.
    In both modes, goods that find no place wait and are delivered as soon as there is room.
    """
    display_name = "Goods Delivery"
    option_district_center = 0
    option_storage = 1
    default = 0


class ForceEarlyItems(Toggle):
    """
    When enabled, essential early-game blueprints (Forester, Stairs, Levee, Floodgate,
    Medium Tank, Gear Workshop) are forced into the first reachable sphere, guaranteeing
    they are available right away. The first badtide comes on a fixed cycle, so the
    Floodgate and Medium Tank must not arrive late. With Progressive Items on, the first
    Progressive Flood Control is forced instead of the Floodgate.
    With Starting Blueprints on, Forester and Stairs are starting items instead, so they
    are not forced. With Starting Blueprints off, the first sphere is too small for all of
    them, so Floodgate and Medium Tank are not forced.

    When disabled, these items are placed freely like any other progression item and may
    appear anywhere in the multiworld. This makes the early game significantly harder and
    less predictable, but allows for more varied and challenging seeds.
    """
    display_name = "Force Early Items"
    default = 1


class StartingBlueprints(Toggle):
    """
    When enabled, you start with the Forester, Stairs and Platform blueprints
    (with Progressive Platforms active, you start with its first step, the Platform).
    They are unlocked as soon as you connect, so sustainable wood and basic vertical
    building never wait on another player. These blueprints are taken out of the
    item pool; their slots receive resource packages instead.

    Force Early Items still puts Levee and Gear Workshop in sphere 1. With this
    option off, Forester and Stairs are forced into sphere 1 instead.
    """
    display_name = "Starting Blueprints"
    default = 1


class ExtraEarlySurvival(Toggle):
    """
    When enabled (alongside Force Early Items), one random survival building per category
    — housing, food, wellbeing — is forced into sphere 1 on top of the core essentials.
    Each seed picks different candidates so runs stay varied. Requires milestones enabled
    to avoid fill errors.

    Designed to fix the "useful item scatter" problem where basic housing/food/wellbeing
    buildings can otherwise arrive very late in the multiworld. Disable for lean seeds
    that only force the core 4 progression items.
    """
    display_name = "Extra Early Survival"
    default = 1


class LogicDifficulty(Choice):
    """Removed: standard and strict generated the same logic, because the survival
    requirements already include strict's buildings. Kept hidden so older YAMLs that
    set it still generate."""
    display_name = "Logic Difficulty (removed)"
    option_standard = 0
    option_strict = 1
    default = 1
    visibility = Visibility.none


@dataclass
class TimberbornOptions(PerGameCommonOptions):
    start_inventory_from_pool: StartInventoryPool
    faction: Faction
    goal_selection: GoalSelection
    goal_requirement: GoalRequirement
    randomization_style: RandomizationStyle
    population_goal: PopulationGoal
    population_mode: PopulationMode
    drought_cycles_goal: DroughtCyclesGoal
    badtide_cycles_goal: BadtideCyclesGoal
    wellbeing_goal: WellbeingGoal
    bots_goal: BotsGoal
    water_storage_goal: WaterStorageGoal
    drought_difficulty: DroughtDifficulty
    include_traps: IncludeTraps
    trap_percentage: TrapPercentage
    hazardous_weather_trap_weight: HazardousWeatherTrapWeight
    hungry_beavers_trap_weight: HungryBeaversTrapWeight
    thirsty_beavers_trap_weight: ThirstyBeaversTrapWeight
    trap_mode: TrapMode
    max_science_cost: MaxScienceCost
    science_cost_multiplier: ScienceCostMultiplier
    skip_count: SkipCount
    progressive_items: ProgressiveItems
    include_population_milestones: IncludePopulationMilestones
    include_wellbeing_milestones: IncludeWellbeingMilestones
    include_survival_milestones: IncludeSurvivalMilestones
    include_wonder_milestone: IncludeWonderMilestone
    include_resource_milestones: IncludeResourceMilestones
    resource_milestone_set: ResourceMilestoneSet
    resource_package_size: ResourcePackageSize
    goods_delivery: GoodsDelivery
    force_early_items: ForceEarlyItems
    starting_blueprints: StartingBlueprints
    extra_early_survival: ExtraEarlySurvival
    logic_difficulty: LogicDifficulty
