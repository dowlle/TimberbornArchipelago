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


@dataclass
class TimberbornOptions(PerGameCommonOptions):
    goal: Goal
    randomization_style: RandomizationStyle
    population_goal: PopulationGoal
    survival_cycles_goal: SurvivalCyclesGoal
    drought_difficulty: DroughtDifficulty
    include_traps: IncludeTraps
