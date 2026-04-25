# LifeLens AI (Decision Survival Game)

A high-intelligence, stateful text-based RPG and Life Simulator powered by advanced LLM reasoning (Gemini 1.5 Pro). This project is designed to evaluate decision-making through a behavioral psychology lens, running on a highly interactive **Streamlit Dashboard** or a rigorous **Terminal interface**.

## 🧠 Core Features

- **Decision Survival Engine**: Traverse through 5 phases of adulthood (ages 22 to 34), making critical life choices.
- **Dynamic Life Stats**: Your **Wealth**, **Happiness**, and **Health** are mathematically impacted by every decision, dynamically bounded and tracked in real-time.
- **Bias Detection**: The AI secretly monitors your psychological traits (e.g., risk aversion, sunk cost fallacy, short-term vs. long-term focus) and provides a brutal psychological breakdown at the end of the simulation.
- **Regret Engine**: After every decision, the AI calculates a mathematical "Regret Score" and reveals the exact opportunity cost of the path not taken.
- **Parallel Reality**: Glimpse into the alternate timeline showing exactly what would have happened if you took the obvious alternative.

## 🚀 Getting Started

1. Ensure you have Python 3.8+ installed.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Get a free Gemini API Key from [Google AI Studio](https://aistudio.google.com/).

### Option A: Web Dashboard (Recommended)
Launch the beautiful, interactive Streamlit UI:
```bash
streamlit run app.py
```
*You can securely enter your API key directly in the dashboard sidebar.*

### Option B: Terminal Mode (Hardcore)
1. Copy `.env.example` to `.env` and insert your Gemini API Key:
   ```bash
   GEMINI_API_KEY=your_actual_api_key
   ```
2. Run the simulation in pure text mode:
   ```bash
   python lifelens.py
   ```

## 🎮 Gameplay Example

**Reality**: You optimized for a high salary at a toxic corporate job. You now make $150k but suffer severe burnout.
**Life Stats**: Wealth (+20), Happiness (-15), Health (-10)
**Parallel Reality Engine**: Had you chosen the startup, you would have made $70k but the company was acquired 2 years later, netting you a $300k equity payout and deep industry connections.
**Regret Engine**: Lost $300k equity and mental wellbeing. Regret Score: +15
**Bias Detected**: "Short-term financial optimization over long-term growth and mental health."
