from dataclasses import dataclass
from Options import Choice, Range, Toggle, OptionSet, PerGameCommonOptions


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


class DroughtCyclesGoal(Range):
    """When 'Droughts' goal is active, the number of drought cycles to survive."""
    display_name = "Drought Cycles Goal"
    range_start = 5
    range_end = 100
    default = 25


class BadtideCyclesGoal(Range):
    """When 'Badtides' goal is active, the number of badtide cycles to survive."""
    display_name = "Badtide Cycles Goal"
    range_start = 1
    range_end = 50
    default = 10


class WellbeingGoal(Range):
    """When 'Well-being' goal is active, the average well-being level to reach."""
    display_name = "Well-being Goal"
    range_start = 5
    range_end = 20
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
    """
    Scaling factor (1–5) for how hard droughts are during the randomizer run.
    Higher values mean longer, more severe droughts.
    """
    display_name = "Drought Difficulty"
    range_start = 1
    range_end = 5
    default = 3


class IncludeTraps(Toggle):
    """If enabled, trap items (Early Drought, Hungry Beavers, Badwater Leak, Thirsty Beavers) can appear in the item pool."""
    display_name = "Include Traps"
    default = 1


class TrapMode(Choice):
    """
    How weather traps (Early Drought, Badwater Leak) behave when hazardous weather is already active:
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


class ForceEarlyItems(Toggle):
    """
    When enabled, essential early-game blueprints (Forester, Stairs, Levee, Gear Workshop)
    are forced into the first reachable sphere, guaranteeing they are available right away.
    Platform and Floodgate are progression items and will also appear early, but are not
    forced into sphere 1 to avoid fill errors when milestones are disabled.

    When disabled, these items are placed freely like any other progression item and may
    appear anywhere in the multiworld. This makes the early game significantly harder and
    less predictable, but allows for more varied and challenging seeds.
    """
    display_name = "Force Early Items"
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
    """
    Controls how strict the logic is for milestone accessibility.
    - standard: Milestones are gated by tier only (lenient — assumes creative survival).
    - strict: Survival milestones also require specific buildings
      (e.g., badtide milestones require Levee + Floodgate, drought milestones require
      water infrastructure). Ensures the solver places survival-critical items before
      survival milestones become reachable.
    """
    display_name = "Logic Difficulty"
    option_standard = 0
    option_strict = 1
    default = 1


@dataclass
class TimberbornOptions(PerGameCommonOptions):
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
    trap_mode: TrapMode
    max_science_cost: MaxScienceCost
    science_cost_multiplier: ScienceCostMultiplier
    skip_count: SkipCount
    progressive_items: ProgressiveItems
    include_population_milestones: IncludePopulationMilestones
    include_wellbeing_milestones: IncludeWellbeingMilestones
    include_survival_milestones: IncludeSurvivalMilestones
    include_wonder_milestone: IncludeWonderMilestone
    force_early_items: ForceEarlyItems
    extra_early_survival: ExtraEarlySurvival
    logic_difficulty: LogicDifficulty
