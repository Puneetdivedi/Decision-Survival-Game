import os
import json
import time
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.text import Text
from dotenv import load_dotenv

from src.engine import LifeLensEngine
from src.exceptions import LifeLensException

load_dotenv()
console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class LifeLensCLI:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            console.print(Panel("[bold red]CRITICAL ERROR[/bold red]: GEMINI_API_KEY not found in environment.\nPlease set it in a .env file or export it.", border_style="red"))
            exit(1)
        
        self.engine = LifeLensEngine(api_key=self.api_key)
        
        self.history = []
        self.turn = 1
        self.max_turns = 5
        self.total_regret_score = 0
        self.wealth = 50
        self.happiness = 50
        self.health = 50
        self.traits = []

    async def start_game(self):
        clear_screen()
        console.print(Panel(Text("LifeLens AI: Decision Engine", justify="center", style="bold magenta"), border_style="magenta", padding=(1, 2)))
        console.print("[dim]Initializing Life Simulator... Loading Parallel Reality Modules... Calibrating Regret Engine...[/dim]\n")
        time.sleep(1)
        
        console.print(Panel("Character Creation", style="cyan"))
        player_name = Prompt.ask("[bold cyan]Enter your name[/bold cyan]", default="Alex")
        ambition = Prompt.ask("[bold cyan]What is your core ambition in life?[/bold cyan]", default="To build a successful tech startup and achieve financial freedom.")
        console.print("\n")

        try:
            with console.status("[bold cyan]LifeLens Engine is generating your destiny...[/bold cyan]", spinner="dots"):
                scenario = await self.engine.generate_initial_scenario(player_name, ambition)
            await self.play_turn(scenario)
        except LifeLensException as e:
            console.print(f"[red]Engine Error: {e}[/red]")
            exit(1)
        except Exception as e:
            console.print(f"[red]Failed to initialize scenario: {e}[/red]")
            exit(1)

    async def play_turn(self, state):
        # state is either InitialScenario or NextScenario
        while self.turn <= self.max_turns:
            current_age = 22 + (self.turn - 1) * 3  # Time jumps 3 years per turn
            console.print(f"\n[bold yellow]=== YEAR {current_age} (Phase {self.turn}/{self.max_turns}) ===[/bold yellow]")
            console.print(Panel(state.context, title=state.scenario_title, border_style="blue"))
            console.print(f"[bold white]{state.dilemma}[/bold white]\n")
            
            for i, choice in enumerate(state.choices, 1):
                console.print(f"  [cyan]{i}.[/cyan] {choice}")
            
            user_choice_idx = IntPrompt.ask("\nMake your decision", choices=[str(i) for i in range(1, len(state.choices)+1)])
            user_choice = state.choices[user_choice_idx - 1]
            
            self.history.append({
                "age": current_age,
                "context": state.context, 
                "dilemma": state.dilemma, 
                "choice": user_choice
            })
            
            try:
                with console.status("[bold cyan]Simulating parallel realities...[/bold cyan]", spinner="dots"):
                    result = await self.engine.simulate_turn(
                        self.turn, self.max_turns, current_age, self.history, self.traits, state.dilemma, user_choice
                    )
            except Exception as e:
                console.print(f"[red]Engine error during simulation: {e}[/red]")
                break
                
            clear_screen()
            console.print(f"\n[bold yellow]=== CONSEQUENCES (Age {current_age}) ===[/bold yellow]")
            console.print(Panel(result.outcome, title="Reality", border_style="green"))
            
            console.print(Panel(f"[dim]{result.parallel_reality}[/dim]", title="[dim]Parallel Reality Engine[/dim]", border_style="magenta"))
            
            score_change = result.regret_engine.regret_score_change
            self.total_regret_score += score_change
            
            w_diff = result.stats_change.wealth
            hap_diff = result.stats_change.happiness
            hlth_diff = result.stats_change.health
            
            self.wealth = max(0, min(100, self.wealth + w_diff))
            self.happiness = max(0, min(100, self.happiness + hap_diff))
            self.health = max(0, min(100, self.health + hlth_diff))
            
            console.print(Panel(
                f"[green]Wealth: {self.wealth}/100 ({w_diff:+d})[/green] | "
                f"[yellow]Happiness: {self.happiness}/100 ({hap_diff:+d})[/yellow] | "
                f"[blue]Health: {self.health}/100 ({hlth_diff:+d})[/blue]",
                title="Life Stats Updated",
                border_style="cyan"
            ))
            
            if hasattr(result, 'acquired_traits') and result.acquired_traits:
                new_traits = []
                for trait in result.acquired_traits:
                    if trait not in self.traits:
                        self.traits.append(trait)
                        new_traits.append(trait)
                if new_traits:
                    console.print(f"[bold green]🎒 Acquired New Traits/Assets:[/bold green] {', '.join(new_traits)}")
            
            console.print(f"\n[bold red]Regret Engine:[/bold red] {result.regret_engine.missed_opportunity}")
            console.print(f"[bold red]Regret +{score_change} (Total: {self.total_regret_score})[/bold red]\n")
            
            time.sleep(2)
            self.turn += 1
            if self.turn <= self.max_turns:
                state = result.next_scenario
        
        await self.end_game()

    async def end_game(self):
        console.print("\n[bold cyan]=== SIMULATION COMPLETE ===[/bold cyan]")
        console.print("Processing life trajectory and psychological profile...\n")
        
        try:
            with console.status("[bold cyan]Analyzing biases...[/bold cyan]", spinner="dots"):
                final = await self.engine.generate_end_game(self.history, self.total_regret_score)
        except Exception as e:
            console.print(f"[red]Failed to generate end game: {e}[/red]")
            return
            
        console.print(Panel(final.life_summary, title="Life Summary", border_style="blue"))
        console.print(Panel(final.bias_revelation, title="Bias Detector", border_style="red"))
        console.print(Panel(final.biggest_regret, title="Biggest Regret", border_style="magenta"))
        console.print(f"\n[bold italic white]LifeLens Insight:[/bold italic white] {final.final_insight}\n")

if __name__ == "__main__":
    try:
        game = LifeLensCLI()
        asyncio.run(game.start_game())
    except KeyboardInterrupt:
        console.print("\n[red]Simulation aborted.[/red]")
