# LifeLens AI (Decision Engine)

A text-based RPG / Life Simulator powered by advanced LLM reasoning (Gemini 1.5 Pro). This project is designed to evaluate decision-making through a psychological lens, focusing heavily on AI intelligence rather than standard graphics.

## Core Features

- **Decision Survival Game**: Traverse through 5 phases of adulthood (ages 22 to 34), making critical life choices.
- **Bias Detection**: The AI secretly monitors your psychological traits based on your choices (e.g., risk aversion, sunk cost fallacy, short-term vs. long-term focus).
- **Regret Engine**: After every decision, the AI calculates a "Regret Score" and reveals the exact opportunity cost of the path not taken.
- **Parallel Reality**: Glimpse into the alternate timeline showing exactly what would have happened if you took the obvious alternative.

This project demonstrates:
- LLM Reasoning & Structured Generation
- Behavioral Psychology Modeling
- Deep Simulation Thinking
- Stateful Memory Systems

## Getting Started

1. Ensure you have Python 3.8+ installed.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and insert your Gemini API Key:
   ```bash
   GEMINI_API_KEY=your_actual_api_key
   ```
4. Run the simulation:
   ```bash
   python lifelens.py
   ```

## Gameplay Example

**Reality**: You optimized for a high salary at a toxic corporate job. You now make $150k but suffer severe burnout.
**Parallel Reality Engine**: Had you chosen the startup, you would have made $70k but the company was acquired 2 years later, netting you a $300k equity payout and deep industry connections.
**Regret Engine**: Lost $300k equity and mental wellbeing. Regret Score: +15
**Bias Detected**: "Short-term financial optimization over long-term growth and mental health."
