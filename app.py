import streamlit as st
import os
import json
from typing import Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="LifeLens AI Dashboard", layout="wide")

# Init session state
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")

if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.turn = 1
    st.session_state.max_turns = 5
    st.session_state.total_regret_score = 0
    st.session_state.wealth = 50
    st.session_state.happiness = 50
    st.session_state.health = 50
    st.session_state.state = None
    st.session_state.consequences = None
    st.session_state.end_game = None

system_instructions = """
You are LifeLens AI, an advanced, highly realistic life simulation and psychological analysis engine.
Your goal is to simulate a realistic, gritty, and deep life path based on the user's choices.
You must model behavioral psychology, track hidden biases (like risk aversion, sunk cost fallacy, instant gratification), simulate parallel realities (what would have happened), and calculate a "Regret Score".

IMPORTANT RULES:
1. Consequences MUST be realistic, compounding, and sometimes unexpected. No generic "you lived happily ever after".
2. You must track their biases secretly.
3. Every response MUST be valid JSON. Do not include markdown formatting like ```json ... ```, just pure JSON.
"""

def call_ai(prompt: str) -> Dict[str, Any]:
    try:
        genai.configure(api_key=st.session_state.api_key)
        model = genai.GenerativeModel('gemini-1.5-pro', generation_config={"response_mime_type": "application/json"})
        response = model.generate_content(system_instructions + "\n\n" + prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        st.error(f"Error communicating with AI: {e}")
        return {}

def generate_initial_scenario():
    with st.spinner("Initializing Life Simulator... Calibrating Regret Engine..."):
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
        st.session_state.state = call_ai(prompt)

def submit_decision(choice):
    current_age = 22 + (st.session_state.turn - 1) * 3
    state = st.session_state.state
    
    st.session_state.history.append({
        "age": current_age,
        "context": state.get("context"),
        "dilemma": state.get("dilemma"),
        "choice": choice
    })
    
    with st.spinner("Simulating Parallel Realities..."):
        prompt = f"""
        The player is on phase {st.session_state.turn} out of {st.session_state.max_turns}. Current age: {current_age}.
        Their entire past history: {json.dumps(st.session_state.history)}
        For their current dilemma: "{state.get("dilemma")}"
        They chose: "{choice}"

        Analyze the decision and generate the outcome, parallel reality, regret metrics, and the next scenario (which takes place 3 years later).
        Return ONLY JSON matching this structure:
        {{
          "outcome": "What actually happened based on their choice (financial, career, emotional impact). Be realistic and impactful.",
          "parallel_reality": "What would have happened if they chose the most obvious alternative. Show the divergence.",
          "stats_change": {
            "wealth": <integer between -20 and +30>,
            "happiness": <integer between -20 and +30>,
            "health": <integer between -20 and +30>
          },
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
        result = call_ai(prompt)
        if result:
            st.session_state.consequences = result
            regret = result.get("regret_engine", {})
            st.session_state.total_regret_score += regret.get("regret_score_change", 0)
            
            stats_change = result.get("stats_change", {})
            st.session_state.wealth = max(0, min(100, st.session_state.wealth + stats_change.get("wealth", 0)))
            st.session_state.happiness = max(0, min(100, st.session_state.happiness + stats_change.get("happiness", 0)))
            st.session_state.health = max(0, min(100, st.session_state.health + stats_change.get("health", 0)))
            
            st.session_state.turn += 1
            if st.session_state.turn <= st.session_state.max_turns:
                st.session_state.state = result.get("next_scenario", {})
            else:
                generate_end_game()

def generate_end_game():
    with st.spinner("Processing life trajectory and psychological profile..."):
        prompt = f"""
        The game has ended. The player's complete decision history is:
        {json.dumps(st.session_state.history)}
        Their final accumulated regret score is {st.session_state.total_regret_score}.

        Analyze their entire life path. Detect their overarching biases, their biggest mistake, and provide a final evaluation.
        Return ONLY JSON matching this structure:
        {{
          "life_summary": "A 2-3 sentence brutal but honest summary of how their life turned out.",
          "bias_revelation": "Detailed analysis of their decision-making patterns and hidden biases (e.g. 'You optimized for comfort but sacrificed growth. You exhibit extreme risk aversion').",
          "biggest_regret": "Identify their most costly mistake across the phases based on the regret score.",
          "final_insight": "A profound concluding thought on their playstyle."
        }}
        """
        st.session_state.end_game = call_ai(prompt)

def reset_game():
    st.session_state.history = []
    st.session_state.turn = 1
    st.session_state.total_regret_score = 0
    st.session_state.wealth = 50
    st.session_state.happiness = 50
    st.session_state.health = 50
    st.session_state.state = None
    st.session_state.consequences = None
    st.session_state.end_game = None

# UI rendering
st.title("🧠 LifeLens AI Dashboard")
st.markdown("Decision Survival Game powered by Gemini 1.5 Pro. Focuses on logic, behavioral modeling, and consequence simulation.")

st.sidebar.title("API Configuration")
api_input = st.sidebar.text_input("Gemini API Key", value=st.session_state.api_key, type="password")
if api_input != st.session_state.api_key:
    st.session_state.api_key = api_input
    
if not st.session_state.api_key:
    st.warning("Please enter your Gemini API Key in the sidebar to begin.")
    st.stop()

if st.session_state.state is None and st.session_state.end_game is None:
    if st.button("Start Simulation", type="primary"):
        generate_initial_scenario()
        st.rerun()

col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("📊 Engine Metrics")
    
    m1, m2, m3 = st.columns(3)
    stats_delta = st.session_state.consequences.get("stats_change", {}) if st.session_state.consequences else {}
    m1.metric("Wealth", f"{st.session_state.wealth}", stats_delta.get("wealth", 0))
    m2.metric("Happiness", f"{st.session_state.happiness}", stats_delta.get("happiness", 0))
    m3.metric("Health", f"{st.session_state.health}", stats_delta.get("health", 0))
    
    st.markdown("---")
    
    st.metric("Phase", f"{min(st.session_state.turn, st.session_state.max_turns)} / {st.session_state.max_turns}")
    current_age = 22 + (min(st.session_state.turn, st.session_state.max_turns) - 1) * 3
    st.metric("Simulated Age", f"{current_age} Years Old")
    st.metric("Cumulative Regret Score", st.session_state.total_regret_score)
    
    if st.session_state.history:
        st.markdown("### 🕒 Timeline History")
        for entry in reversed(st.session_state.history):
            with st.expander(f"Age {entry['age']} Decision"):
                st.write(f"**Dilemma:** {entry['dilemma']}")
                st.write(f"**Choice:** {entry['choice']}")

with col1:
    if st.session_state.end_game:
        st.error("### 🛑 SIMULATION COMPLETE")
        final = st.session_state.end_game
        st.info(f"**Life Summary:**\\n{final.get('life_summary', '')}")
        st.warning(f"**Bias Detector:**\\n{final.get('bias_revelation', '')}")
        st.error(f"**Biggest Regret:**\\n{final.get('biggest_regret', '')}")
        st.success(f"**Final Insight:**\\n{final.get('final_insight', '')}")
        
        if st.button("Start New Life"):
            reset_game()
            st.rerun()
            
    elif st.session_state.state:
        # Display consequences of previous turn if it exists
        if st.session_state.consequences and st.session_state.turn > 1:
            with st.expander(f"Consequences of Phase {st.session_state.turn - 1} Choice", expanded=True):
                cons = st.session_state.consequences
                st.success(f"**Reality:** {cons.get('outcome', '')}")
                st.info(f"**Parallel Reality Engine:** {cons.get('parallel_reality', '')}")
                regret = cons.get("regret_engine", {})
                st.error(f"**Regret (+{regret.get('regret_score_change', 0)}):** {regret.get('missed_opportunity', '')}")
                st.warning(f"**Bias Detected:** {cons.get('bias_detected', '')}")
        
        # Display current scenario
        st.subheader(f"Year {current_age} - {st.session_state.state.get('scenario_title', 'Current Phase')}")
        st.write(st.session_state.state.get("context", ""))
        
        st.markdown(f"### **{st.session_state.state.get('dilemma', '')}**")
        
        choices = st.session_state.state.get("choices", [])
        for choice in choices:
            if st.button(choice, key=choice, use_container_width=True):
                submit_decision(choice)
                st.rerun()
