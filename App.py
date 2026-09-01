import streamlit as st
import pandas as pd
import json
import os

# Page Configuration
st.set_page_config(page_title="28-Day Hybrid Habit Challenge", page_icon="🌸", layout="centered")

# Custom Styling for Polish
st.markdown("""
    <style>
    .main-title { font-size: 26px; font-weight: bold; color: #2E4053; text-align: center; }
    .subtitle { font-size: 14px; color: #7F8C8D; text-align: center; margin-bottom: 20px; }
    .alert-box { background-color: #FADBD8; padding: 12px; border-radius: 8px; color: #922B21; font-weight: bold; }
    .success-box { background-color: #D4EFDF; padding: 12px; border-radius: 8px; color: #145A32; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🌸 28-Day Hybrid Habit Challenge</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Consistency over perfection. Never miss twice!</p>', unsafe_allow_html=True)

# Data Persistence File
DATA_FILE = "challenge_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    # Default initial state for Contestant 1 and Contestant 2
    default_structure = {
        "Contestant 1": {str(day): {f"habit_{i}": False for i in range(1, 11)} | {"bonus": 0, "notes": ""} for day in range(1, 29)},
        "Contestant 2": {str(day): {f"habit_{i}": False for i in range(1, 11)} | {"bonus": 0, "notes": ""} for day in range(1, 29)}
    }
    return default_structure

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Initialize Session State
if "app_data" not in st.session_state:
    st.session_state.app_data = load_data()

# Sidebar Navigation
view_mode = st.sidebar.radio("Navigation", ["Daily Logger", "28-Day Overview Grid", "Combined Scoreboard & Rewards"])

habits_list = [
    "1. Hydration (Water Goal)",
    "2. Unified Nutrition (Calories & Clean Meals)",
    "3. Protein & Greens Target",
    "4. Daily Movement / Step Count",
    "5. Structured Workout / Active Recovery",
    "6. Spiritual Time (Bible / Prayer)",
    "7. Bedtime Discipline",
    "8. Screen-Free Wind-Down (30 min)",
    "9. Self-Care / Skincare Routine",
    "10. Mental Wellbeing Activity"
]

def calculate_total(contestant_data):
    total = 0
    for day in range(1, 29):
        d_str = str(day)
        core = sum(1 for i in range(1, 11) if contestant_data[d_str].get(f"habit_{i}", False))
        bonus = contestant_data[d_str].get("bonus", 0)
        total += core + bonus
    return total

if view_mode == "Daily Logger":
    contestant = st.selectbox("Select Profile", ["Contestant 1", "Contestant 2"])
    selected_day = st.selectbox("Select Day to Log", list(range(1, 29)), format_func=lambda x: f"Day {x}")
    
    day_str = str(selected_day)
    day_state = st.session_state.app_data[contestant][day_str]
    
    st.write(f"### 📝 Check-in for Day {selected_day} ({contestant})")
    
    # Render Checkboxes
    col1, col2 = st.columns(2)
    with col1:
        for i in range(1, 6):
            day_state[f"habit_{i}"] = st.checkbox(habits_list[i-1], value=day_state.get(f"habit_{i}", False), key=f"{contestant}_d{selected_day}_h{i}")
    with col2:
        for i in range(6, 11):
            day_state[f"habit_{i}"] = st.checkbox(habits_list[i-1], value=day_state.get(f"habit_{i}", False), key=f"{contestant}_d{selected_day}_h{i}")

    # Bonus Points Input
    bonus_pts = st.number_input("⭐ Daily Bonus Points (Max 3)", min_value=0, max_value=3, value=day_state.get("bonus", 0), key=f"{contestant}_d{selected_day}_bonus")
    day_state["bonus"] = bonus_pts

    # Daily Notes / Journal
    daily_notes = st.text_area("📖 Daily Notes / Reflections / Prayer Journal", value=day_state.get("notes", ""), key=f"{contestant}_d{selected_day}_notes")
    day_state["notes"] = daily_notes

    # Save automatically to JSON
    save_data(st.session_state.app_data)

    # Calculate Daily Subtotal
    core_completed = sum(1 for i in range(1, 11) if day_state.get(f"habit_{i}", False))
    daily_total = core_completed + bonus_pts
    
    st.info(f"✨ **Day {selected_day} Score:** {core_completed} (Core) + {bonus_pts} (Bonus) = **{daily_total} Points**")

    # "Never Miss Twice" Check logic
    if selected_day > 1:
        prev_day_str = str(selected_day - 1)
        prev_core = sum(1 for i in range(1, 11) if st.session_state.app_data[contestant][prev_day_str].get(f"habit_{i}", False))
        if core_completed < 7 and prev_core < 7:
            st.markdown('<p class="alert-box">🚨 "Never Miss Twice" Alert: Your core score has dropped below 7 for two consecutive days. Time for a quick bounce-back tomorrow!</p>', unsafe_allow_html=True)

    # Cumulative Progress on Logger screen
    total_cumulative = calculate_total(st.session_state.app_data[contestant])
    st.write("---")
    st.subheader("🏆 Milestone Rewards Status")
    st.write(f"**Total Cumulative Points:** {total_cumulative} / 280")
    
    if total_cumulative >= 280:
        st.markdown('<p class="success-box">🏆 Level 3 Unlocked: Full Transformation Grand Reward Achieved!</p>', unsafe_allow_html=True)
    elif total_cumulative >= 200:
        st.markdown('<p class="success-box">🌟 Level 2 Unlocked: Mid-Challenge Reward Unlocked!</p>', unsafe_allow_html=True)
    elif total_cumulative >= 100:
        st.markdown('<p class="success-box">🎉 Level 1 Unlocked: Little Treat Unlocked!</p>', unsafe_allow_html=True)
    else:
        st.write("🌱 Keep going! Hit 100 points to unlock your first milestone treat.")

elif view_mode == "28-Day Overview Grid":
    st.subheader("📊 28-Day Summary Grid")
    contestant = st.selectbox("Select Profile for Grid", ["Contestant 1", "Contestant 2"])
    
    grid_data = []
    c_data = st.session_state.app_data[contestant]
    for day in range(1, 29):
        d_str = str(day)
        core = sum(1 for i in range(1, 11) if c_data[d_str].get(f"habit_{i}", False))
        bonus = c_data[d_str].get("bonus", 0)
        notes = c_data[d_str].get("notes", "")
        grid_data.append({
            "Day": f"Day {day}",
            "Core Habits (/10)": core,
            "Bonus": bonus,
            "Total": core + bonus,
            "Notes / Journal": notes if notes else "—"
        })
    
    df_grid = pd.DataFrame(grid_data)
    st.dataframe(df_grid, use_container_width=True)

else:
    st.subheader("📊 Team Leaderboard & Joint Target")
    
    c1_total = calculate_total(st.session_state.app_data["Contestant 1"])
    c2_total = calculate_total(st.session_state.app_data["Contestant 2"])
    combined_total = c1_total + c2_total
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Contestant 1", f"{c1_total} pts")
    col_b.metric("Contestant 2", f"{c2_total} pts")
    col_c.metric("Combined Total", f"{combined_total} / 560 pts")
    
    st.write("---")
    st.subheader("🎉 Joint Team Goal Status (Target: 500+ Combined Points)")
    if combined_total >= 500:
        st.markdown('<p class="success-box">🥂 UNLOCKED! Spa Day, Lunch & Shopping Trip Achieved Together! Amazing job!</p>', unsafe_allow_html=True)
        st.balloons()
    else:
        points_needed = 500 - combined_total
        st.info(f"🎯 **{max(0, points_needed)} more combined points** needed to unlock your joint Girls' Day Out reward!")
