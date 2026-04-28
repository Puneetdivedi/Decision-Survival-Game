import json
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import ValidationError

from .schemas import InitialScenario, TurnConsequences, EndGameSummary
from .exceptions import EngineInitializationError, GenerationError, ParsingError

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTIONS = """
You are LifeLens AI, an advanced, highly realistic life simulation and psychological analysis engine.
Your goal is to simulate a realistic, gritty, and deep life path based on the user's choices.
You must model behavioral psychology, track hidden biases (like risk aversion, sunk cost fallacy, instant gratification), simulate parallel realities (what would have happened), and calculate a "Regret Score".

IMPORTANT RULES:
1. Consequences MUST be realistic, compounding, and sometimes unexpected. No generic "you lived happily ever after".
2. You must track their biases secretly.
3. Every response MUST be valid JSON matching the exact schema requested. Do not include markdown formatting like ```json ... ```, just pure JSON.
"""

class LifeLensEngine:
    def __init__(self, api_key: str):
        if not api_key:
            raise EngineInitializationError("API Key must be provided")
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            'gemini-1.5-pro',
            generation_config={"response_mime_type": "application/json"}
        )
        logger.info("LifeLensEngine initialized asynchronously.")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), retry=retry_if_exception_type(GenerationError))
    async def _call_ai_async(self, prompt: str) -> str:
        try:
            logger.info("Calling Gemini API asynchronously...")
            response = await self.model.generate_content_async(SYSTEM_INSTRUCTIONS + "\n\n" + prompt)
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            return text.strip()
        except Exception as e:
            logger.error(f"Error communicating with AI: {e}")
            raise GenerationError(f"Failed to generate response: {e}")

    async def generate_initial_scenario(self) -> InitialScenario:
        prompt = """
        Generate the initial scenario for the player. They are 22 years old, starting their adult life. 
        Make the scenario challenging but realistic (e.g., heavy student debt, a toxic but high-paying first job, or an unconventional high-risk path).
        Provide the first major life dilemma.

        Return ONLY JSON matching this structure:
        {
          "scenario_title": "string",
          "context": "string",
          "dilemma": "string",
          "choices": ["string", "string", "string"]
        }
        """
        text_response = await self._call_ai_async(prompt)
        try:
            return InitialScenario.model_validate_json(text_response)
        except ValidationError as e:
            logger.error(f"Validation error for InitialScenario: {e}")
            raise ParsingError(f"Failed to parse InitialScenario: {e}")

    async def simulate_turn(self, turn: int, max_turns: int, current_age: int, history: list, current_dilemma: str, choice: str) -> TurnConsequences:
        prompt = f"""
        The player is on phase {turn} out of {max_turns}. Current age: {current_age}.
        Their entire past history: {json.dumps(history)}
        For their current dilemma: "{current_dilemma}"
        They chose: "{choice}"

        Analyze the decision and generate the outcome, parallel reality, regret metrics, and the next scenario (which takes place 3 years later).
        Return ONLY JSON matching this structure:
        {{
          "outcome": "string",
          "parallel_reality": "string",
          "stats_change": {{
            "wealth": int,
            "happiness": int,
            "health": int
          }},
          "regret_engine": {{
            "missed_opportunity": "string",
            "regret_score_change": int
          }},
          "bias_detected": "string",
          "next_scenario": {{
            "scenario_title": "string",
            "context": "string",
            "dilemma": "string",
            "choices": ["string", "string", "string"]
          }}
        }}
        """
        text_response = await self._call_ai_async(prompt)
        try:
            return TurnConsequences.model_validate_json(text_response)
        except ValidationError as e:
            logger.error(f"Validation error for TurnConsequences: {e}")
            raise ParsingError(f"Failed to parse TurnConsequences: {e}")

    async def generate_end_game(self, history: list, total_regret: int) -> EndGameSummary:
        prompt = f"""
        The game has ended. The player's complete decision history is:
        {json.dumps(history)}
        Their final accumulated regret score is {total_regret}.

        Analyze their entire life path. Detect their overarching biases, their biggest mistake, and provide a final evaluation.
        Return ONLY JSON matching this structure:
        {{
          "life_summary": "string",
          "bias_revelation": "string",
          "biggest_regret": "string",
          "final_insight": "string"
        }}
        """
        text_response = await self._call_ai_async(prompt)
        try:
            return EndGameSummary.model_validate_json(text_response)
        except ValidationError as e:
            logger.error(f"Validation error for EndGameSummary: {e}")
            raise ParsingError(f"Failed to parse EndGameSummary: {e}")
