from pydantic import BaseModel, Field
from typing import List

class InitialScenario(BaseModel):
    scenario_title: str = Field(..., description="Title of the scenario")
    context: str = Field(..., description="Detailed description of the starting situation")
    dilemma: str = Field(..., description="The specific choice the player faces right now")
    choices: List[str] = Field(..., description="A list of possible choices")

class StatsChange(BaseModel):
    wealth: int = Field(default=0, description="Change in wealth score (-20 to 30)")
    happiness: int = Field(default=0, description="Change in happiness score (-20 to 30)")
    health: int = Field(default=0, description="Change in health score (-20 to 30)")

class RegretMetrics(BaseModel):
    missed_opportunity: str = Field(..., description="The exact cost (money, time, or relationship) of their foregone path")
    regret_score_change: int = Field(default=0, description="The integer increase in regret score")

class NextScenario(BaseModel):
    scenario_title: str = Field(..., description="Title of the next phase")
    context: str = Field(..., description="What their life looks like now")
    dilemma: str = Field(..., description="The new dilemma they face")
    choices: List[str] = Field(..., description="A list of possible choices")

class TurnConsequences(BaseModel):
    outcome: str = Field(..., description="What actually happened based on their choice")
    parallel_reality: str = Field(..., description="What would have happened if they chose the obvious alternative")
    stats_change: StatsChange
    regret_engine: RegretMetrics
    bias_detected: str = Field(..., description="A short note on what psychological bias this choice reveals")
    next_scenario: NextScenario

class EndGameSummary(BaseModel):
    life_summary: str = Field(..., description="A brutal but honest summary of how their life turned out")
    bias_revelation: str = Field(..., description="Detailed analysis of their decision-making patterns and hidden biases")
    biggest_regret: str = Field(..., description="Identify their most costly mistake")
    final_insight: str = Field(..., description="A profound concluding thought on their playstyle")
