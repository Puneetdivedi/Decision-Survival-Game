import os
import json
import time
from typing import List, Dict, Any
from google import genai
from google.genai import types
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.text import Text
from dotenv import load_dotenv

load_dotenv()
console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class LifeLensGame:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            console.print(Panel("[bold red]CRITICAL ERROR[/bold red]: GEMINI_API_KEY not found in environment.\nPlease set it in a .env file or export it.", border_style="red"))
            exit(1)
        
        self.client = genai.Client(api_key=self.api_key)
        
        self.history = []
        self.turn = 1
        self.max_turns = 5
        self.total_regret_score = 0
        
        self.system_instructions = """
You are LifeLens AI, an advanced, highly realistic life simulation and psychological analysis engine.
Your goal is to simulate a realistic, gritty, and deep life path based on the user's choices.
You must model behavioral psychology, track hidden biases (like risk aversion, sunk cost fallacy, instant gratification), simulate parallel realities (what would have happened), and calculate a "Regret Score".

IMPORTANT RULES:
1. Consequences MUST be realistic, compounding, and sometimes unexpected. No generic "you lived happily ever after".
2. You must track their biases secretly.
3. Every response MUST be valid JSON. Do not include markdown formatting like ```json ... ```, just pure JSON.
"""

    def call_ai(self, prompt: str) -> Dict[str, Any]:
        with console.status("[bold cyan]LifeLens Engine is simulating outcomes...[/bold cyan]", spinner="dots"):
            response = self.client.models.generate_content(
                model='gemini-1.5-pro',
                contents=self.system_instructions + "\n\n" + prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            try:
                text = response.text.strip()
                # Clean markdown wrapper if LLM includes it despite instructions
                if text.startswith("```json"):
                    text = text[7:]
                if text.endswith("```"):
                    text = text[:-3]
                return json.loads(text.strip())
            except Exception as e:
                console.print(f"[red]Error parsing AI response: {e}[/red]")
                # Fallback empty structure
                return {}

    def start_game(self):
        clear_screen()
        console.print(Panel(Text("LifeLens AI: Decision Engine", justify="center", style="bold magenta"), border_style="magenta", padding=(1, 2)))
        console.print("[dim]Initializing Life Simulator... Loading Parallel Reality Modules... Calibrating Regret Engine...[/dim]\n")
        time.sleep(2)

        prompt = """
Generate the initial scenario for the player. They are 22 years old, starting their adult life. 
Make the scenario challenging but realistic (e.g., heavy student debt, a toxic but high-paying first job, or an unconventional high-risk path).
Provide the first major life dilemma.

Return ONLY JSON matching this structure:
{
  "scenario_title": "Title of the scenario",
  "context": "Detailed description of the starting situation...",
  "dilemma": "The specific choice they face right now.",
  "choices": ["Choice 1", "Choice 2", "Choice 3"]
}
"""
        state = self.call_ai(prompt)
        if not state:
            console.print("[red]Failed to initialize scenario. Exiting.[/red]")
            return
            
        self.play_turn(state)

    def play_turn(self, state: dict):
        while self.turn <= self.max_turns:
            current_age = 22 + (self.turn - 1) * 3  # Time jumps 3 years per turn
            console.print(f"\n[bold yellow]=== YEAR {current_age} (Phase {self.turn}/{self.max_turns}) ===[/bold yellow]")
            console.print(Panel(state.get("context", ""), title=state.get("scenario_title", "Current Situation"), border_style="blue"))
            console.print(f"[bold white]{state.get('dilemma', '')}[/bold white]\n")
            
            choices = state.get("choices", [])
            for i, choice in enumerate(choices, 1):
                console.print(f"  [cyan]{i}.[/cyan] {choice}")
            
            # Use IntPrompt from rich for robust integer input
            user_choice_idx = IntPrompt.ask("\nMake your decision", choices=[str(i) for i in range(1, len(choices)+1)])
            user_choice = choices[user_choice_idx - 1]
            
            self.history.append({
                "age": current_age,
                "context": state.get("context"), 
                "dilemma": state.get("dilemma"), 
                "choice": user_choice
            })
            
            prompt = f"""
The player is on phase {self.turn} out of {self.max_turns}. Current age: {current_age}.
Their entire past history: {json.dumps(self.history)}
For their current dilemma: "{state.get("dilemma")}"
They chose: "{user_choice}"

Analyze the decision and generate the outcome, parallel reality, regret metrics, and the next scenario (which takes place 3 years later).
Return ONLY JSON matching this structure:
{{
  "outcome": "What actually happened based on their choice (financial, career, emotional impact). Be realistic and impactful.",
  "parallel_reality": "What would have happened if they chose the most obvious alternative. Show the divergence.",
  "regret_engine": {{
    "missed_opportunity": "The exact cost (money, time, or relationship) of their foregone path.",
    "regret_score_change": <integer between 0 and 20>
  }},
  "bias_detected": "A short note on what psychological bias this choice reveals (e.g. 'Risk Aversion', 'Short-term thinking', 'Sunk Cost').",
  "next_scenario": {{
    "scenario_title": "Title of the next phase",
    "context": "What their life looks like now, 3 years later.",
    "dilemma": "The new dilemma they face.",
    "choices": ["Choice 1", "Choice 2", "Choice 3"]
  }}
}}
"""
            result = self.call_ai(prompt)
            if not result:
                console.print("[red]Engine error. Fast-forwarding...[/red]")
                break
                
            # Display results
            clear_screen()
            console.print(f"\n[bold yellow]=== CONSEQUENCES (Age {current_age}) ===[/bold yellow]")
            console.print(Panel(result.get("outcome", ""), title="Reality", border_style="green"))
            
            console.print(Panel(f"[dim]{result.get('parallel_reality', '')}[/dim]", title="[dim]Parallel Reality Engine[/dim]", border_style="magenta"))
            
            regret = result.get("regret_engine", {})
            score_change = regret.get("regret_score_change", 0)
            self.total_regret_score += score_change
            
            console.print(f"[bold red]Regret Engine:[/bold red] {regret.get('missed_opportunity', '')}")
            console.print(f"[bold red]Regret +{score_change} (Total: {self.total_regret_score})[/bold red]\n")
            
            time.sleep(2)
            self.turn += 1
            if self.turn <= self.max_turns:
                state = result.get("next_scenario", {})
        
        self.end_game()

    def end_game(self):
        console.print("\n[bold cyan]=== SIMULATION COMPLETE ===[/bold cyan]")
        console.print("Processing life trajectory and psychological profile...\n")
        
        prompt = f"""
The game has ended. The player's complete decision history is:
{json.dumps(self.history)}
Their final accumulated regret score is {self.total_regret_score}.

Analyze their entire life path. Detect their overarching biases, their biggest mistake, and provide a final evaluation.
Return ONLY JSON matching this structure:
{{
  "life_summary": "A 2-3 sentence brutal but honest summary of how their life turned out.",
  "bias_revelation": "Detailed analysis of their decision-making patterns and hidden biases (e.g. 'You optimized for comfort but sacrificed growth. You exhibit extreme risk aversion').",
  "biggest_regret": "Identify their most costly mistake across the phases based on the regret score.",
  "final_insight": "A profound concluding thought on their playstyle."
}}
"""
        final = self.call_ai(prompt)
        if not final:
            return
            
        console.print(Panel(final.get("life_summary", ""), title="Life Summary", border_style="blue"))
        console.print(Panel(final.get("bias_revelation", ""), title="Bias Detector", border_style="red"))
        console.print(Panel(final.get("biggest_regret", ""), title="Biggest Regret", border_style="magenta"))
        console.print(f"\n[bold italic white]LifeLens Insight:[/bold italic white] {final.get('final_insight', '')}\n")

if __name__ == "__main__":
    try:
        game = LifeLensGame()
        game.start_game()
    except KeyboardInterrupt:
        console.print("\n[red]Simulation aborted.[/red]")
