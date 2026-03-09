from dataclasses import dataclass
from Options import Choice, Range, Toggle, PerGameCommonOptions


class Goal(Choice):
    """
    What is required to complete the game?
    - complete_wonder: Construct your faction's Wonder building.
    - reach_population: Reach the target population (see population_goal).
    - survive_cycles: Survive a set number of drought cycles (see survival_cycles_goal).
    """
    display_name = "Goal"
    option_complete_wonder = 0
    option_reach_population = 1
    option_survive_cycles = 2
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


class PopulationGoal(Range):
    """When goal is 'reach_population', the number of beavers required."""
    display_name = "Population Goal"
    range_start = 10
    range_end = 500
    default = 100


class SurvivalCyclesGoal(Range):
    """When goal is 'survive_cycles', the number of drought cycles to survive."""
    display_name = "Survival Cycles Goal"
    range_start = 5
    range_end = 100
    default = 30


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
    """If enabled, trap items (Early Drought, Hungry Beavers, Badwater Leak) can appear in the item pool."""
    display_name = "Include Traps"
    default = 1


class MaxScienceCost(Range):
    """Maximum science cost for the most expensive shop location."""
    display_name = "Max Science Cost"
    range_start = 1000
    range_end = 20000
    default = 5000


class SkipCount(Range):
    """Number of Skip items added to the item pool. Skips let you check a shop location for free."""
    display_name = "Skip Count"
    range_start = 0
    range_end = 10
    default = 3


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


@dataclass
class TimberbornOptions(PerGameCommonOptions):
    goal: Goal
    randomization_style: RandomizationStyle
    population_goal: PopulationGoal
    survival_cycles_goal: SurvivalCyclesGoal
    drought_difficulty: DroughtDifficulty
    include_traps: IncludeTraps
    max_science_cost: MaxScienceCost
    skip_count: SkipCount
    include_population_milestones: IncludePopulationMilestones
    include_wellbeing_milestones: IncludeWellbeingMilestones
    include_survival_milestones: IncludeSurvivalMilestones
    include_wonder_milestone: IncludeWonderMilestone
