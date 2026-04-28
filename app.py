import streamlit as st
import os
import json
import pandas as pd
import asyncio
from dotenv import load_dotenv

from src.engine import LifeLensEngine

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
    st.session_state.stats_history = {
        "Age": [22],
        "Wealth": [50],
        "Happiness": [50],
        "Health": [50]
    }
    st.session_state.state = None
    st.session_state.consequences = None
    st.session_state.end_game = None

def get_engine():
    if not st.session_state.api_key:
        return None
    return LifeLensEngine(api_key=st.session_state.api_key)

def generate_initial_scenario():
    engine = get_engine()
    if not engine:
        return
    with st.spinner("Initializing Life Simulator... Calibrating Regret Engine..."):
        try:
            st.session_state.state = asyncio.run(engine.generate_initial_scenario())
        except Exception as e:
            st.error(f"Error communicating with AI: {e}")

def submit_decision(choice):
    engine = get_engine()
    if not engine:
        return
    
    current_age = 22 + (st.session_state.turn - 1) * 3
    state = st.session_state.state
    
    st.session_state.history.append({
        "age": current_age,
        "context": state.context,
        "dilemma": state.dilemma,
        "choice": choice
    })
    
    with st.spinner("Simulating Parallel Realities..."):
        try:
            result = asyncio.run(engine.simulate_turn(
                st.session_state.turn,
                st.session_state.max_turns,
                current_age,
                st.session_state.history,
                state.dilemma,
                choice
            ))
            
            st.session_state.consequences = result
            st.session_state.total_regret_score += result.regret_engine.regret_score_change
            
            st.session_state.wealth = max(0, min(100, st.session_state.wealth + result.stats_change.wealth))
            st.session_state.happiness = max(0, min(100, st.session_state.happiness + result.stats_change.happiness))
            st.session_state.health = max(0, min(100, st.session_state.health + result.stats_change.health))
            
            next_age = current_age + 3
            st.session_state.stats_history["Age"].append(next_age)
            st.session_state.stats_history["Wealth"].append(st.session_state.wealth)
            st.session_state.stats_history["Happiness"].append(st.session_state.happiness)
            st.session_state.stats_history["Health"].append(st.session_state.health)
            
            st.session_state.turn += 1
            if st.session_state.turn <= st.session_state.max_turns:
                st.session_state.state = result.next_scenario
            else:
                generate_end_game()
        except Exception as e:
            st.error(f"Engine Error: {e}")

def generate_end_game():
    engine = get_engine()
    if not engine:
        return
    with st.spinner("Processing life trajectory and psychological profile..."):
        try:
            st.session_state.end_game = asyncio.run(engine.generate_end_game(st.session_state.history, st.session_state.total_regret_score))
        except Exception as e:
            st.error(f"Engine Error: {e}")

def reset_game():
    st.session_state.history = []
    st.session_state.turn = 1
    st.session_state.total_regret_score = 0
    st.session_state.wealth = 50
    st.session_state.happiness = 50
    st.session_state.health = 50
    st.session_state.stats_history = {
        "Age": [22],
        "Wealth": [50],
        "Happiness": [50],
        "Health": [50]
    }
    st.session_state.state = None
    st.session_state.consequences = None
    st.session_state.end_game = None

# UI rendering
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    .stApp {
        background: radial-gradient(circle at top, #0f172a 0%, #020617 100%);
        color: #f8fafc;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white !important;
        font-weight: 600;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5);
        background: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%);
    }
    [data-testid="stExpander"] {
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

st.title("🧠 LifeLens AI Dashboard")
st.markdown("Decision Survival Game powered by **Gemini 1.5 Pro**. Focuses on logic, behavioral modeling, and consequence simulation.")

st.sidebar.title("⚙️ API Configuration")
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
    stats_delta = st.session_state.consequences.stats_change if st.session_state.consequences else None
    m1.metric("Wealth", f"{st.session_state.wealth}", stats_delta.wealth if stats_delta else 0)
    m2.metric("Happiness", f"{st.session_state.happiness}", stats_delta.happiness if stats_delta else 0)
    m3.metric("Health", f"{st.session_state.health}", stats_delta.health if stats_delta else 0)
    
    st.markdown("---")
    
    st.metric("Phase", f"{min(st.session_state.turn, st.session_state.max_turns)} / {st.session_state.max_turns}")
    current_age = 22 + (min(st.session_state.turn, st.session_state.max_turns) - 1) * 3
    st.metric("Simulated Age", f"{current_age} Years Old")
    st.metric("Cumulative Regret Score", st.session_state.total_regret_score)
    
    st.markdown("### 📈 Life Trajectory")
    df_stats = pd.DataFrame(st.session_state.stats_history).set_index("Age")
    st.line_chart(df_stats, use_container_width=True)
    
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
        st.info(f"**Life Summary:**\n{final.life_summary}")
        st.warning(f"**Bias Detector:**\n{final.bias_revelation}")
        st.error(f"**Biggest Regret:**\n{final.biggest_regret}")
        st.success(f"**Final Insight:**\n{final.final_insight}")
        
        if st.button("Start New Life"):
            reset_game()
            st.rerun()
            
    elif st.session_state.state:
        # Display consequences of previous turn if it exists
        if st.session_state.consequences and st.session_state.turn > 1:
            with st.expander(f"Consequences of Phase {st.session_state.turn - 1} Choice", expanded=True):
                cons = st.session_state.consequences
                st.success(f"**Reality:** {cons.outcome}")
                st.info(f"**Parallel Reality Engine:** {cons.parallel_reality}")
                regret = cons.regret_engine
                st.error(f"**Regret (+{regret.regret_score_change}):** {regret.missed_opportunity}")
                st.warning(f"**Bias Detected:** {cons.bias_detected}")
        
        # Display current scenario
        st.subheader(f"Year {current_age} - {st.session_state.state.scenario_title}")
        st.write(st.session_state.state.context)
        
        st.markdown(f"### **{st.session_state.state.dilemma}**")
        
        choices = st.session_state.state.choices
        for choice in choices:
            if st.button(choice, key=choice, use_container_width=True):
                submit_decision(choice)
                st.rerun()
