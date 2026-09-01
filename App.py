import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="28-Day Hybrid Habit Challenge", page_icon="🌸", layout="centered")

# Custom Styling
st.markdown("""
    <style>
    .main-title { font-size: 26px; font-weight: bold; color: #2E4053; text-align: center; }
    .subtitle { font-size: 14px; color: #7F8C8D; text-align: center; margin-bottom: 20px; }
    .alert-box { background-color: #FADBD8; padding: 10px; border-radius: 5px; color: #922B21; font-weight: bold; }
    .success-box { background-color: #D4EFDF; padding: 10px; border-radius: 5px; color: #145A32; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🌸 28-Day Hybrid Habit Challenge</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Consistency over perfection. Never miss twice!</p>', unsafe_allow_html=True)

# Session State Initialization for Data Persistence during the session
if "data_c1" not in st.session_state:
    st.session_state.data_c1 = {day: {f"habit_{i}": False for i in range(1, 11)} | {"bonus": 0} for day in range(1, 29)}
if "data_c2" not in st.session_state:
    st.session_state.data_c2 = {day: {f"habit_{i}": False for i in range(1, 11)} | {"bonus": 0} for day in range(1, 29)}

# Sidebar Navigation
contestant = st.sidebar.selectbox("Select Profile", ["Contestant 1", "Contestant 2", "Combined Scoreboard"])
current_data = st.session_state.data_c1 if contestant == "Contestant 1" else st.session_state.data_c2

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

if contestant in ["Contestant 1", "Contestant 2"]:
    st.subheader(f"📝 Daily Log — {contestant}")
    selected_day = st.selectbox("Select Day to Log", list(range(1, 29)), format_func=lambda x: f"Day {x}")
    
    st.write(f"Check off your completed habits for **Day {selected_day}**:")
    
    day_key = selected_day
    day_state = current_data[day_key]
    
    # Render Checkboxes
    col1, col2 = st.columns(2)
    with col1:
        for i in range(1, 6):
            day_state[f"habit_{i}"] = st.checkbox(habits_list[i-1], value=day_state[f"habit_{i}"], key=f"{contestant}_d{selected_day}_h{i}")
    with col2:
        for i in range(6, 11):
            day_state[f"habit_{i}"] = st.checkbox(habits_list[i-1], value=day_state[f"habit_{i}"], key=f"{contestant}_d{selected_day}_h{i}")

    # Bonus Points Input
    bonus_pts = st.number_input("⭐ Daily Bonus Points (Max 3)", min_value=0, max_value=3, value=day_state["bonus"], key=f"{contestant}_d{selected_day}_bonus")
    day_state["bonus"] = bonus_pts

    # Calculate Daily Subtotal
    core_completed = sum(1 for i in range(1, 11) if day_state[f"habit_{i}"])
    daily_total = core_completed + bonus_pts
    
    st.info(f"✨ **Day {selected_day} Score:** {core_completed} (Core) + {bonus_pts} (Bonus) = **{daily_total} Points**")

    # "Never Miss Twice" Check logic
    if selected_day > 1:
        prev_core = sum(1 for i in range(1, 11) if current_data[selected_day-1][f"habit_{i}"])
        if core_completed < 7 and prev_core < 7:
            st.markdown('<p class="alert-box">🚨 "Never Miss Twice" Alert: Your core score has dropped below 7 for two consecutive days. Time for a quick bounce-back tomorrow!</p>', unsafe_allow_html=True)

    # Calculate 28-Day Cumulative Total
    total_cumulative = sum(sum(1 for i in range(1, 11) if current_data[d][f"habit_{i}"]) + current_data[d]["bonus"] for d in range(1, 29))
    
    st.write("---")
    st.subheader("🏆 Your Milestone Rewards Tracker")
    st.write(f"**Total Cumulative Points:** {total_cumulative} / 280")
    
    # Reward Unlocks
    if total_cumulative >= 280:
        st.markdown('<p class="success-box">🏆 Level 3 Unlocked: Full Transformation Grand Reward Achieved!</p>', unsafe_allow_html=True)
    elif total_cumulative >= 200:
        st.markdown('<p class="success-box">🌟 Level 2 Unlocked: Mid-Challenge Reward Unlocked!</p>', unsafe_allow_html=True)
    elif total_cumulative >= 100:
        st.markdown('<p class="success-box">🎉 Level 1 Unlocked: Little Treat Unlocked!</p>', unsafe_allow_html=True)
    else:
        st.write("🌱 Keep going! Hit 100 points to unlock your first milestone treat.")

else:
    # Combined Scoreboard View
    st.subheader("📊 Team Leaderboard & Joint Target")
    
    c1_total = sum(sum(1 for i in range(1, 11) if st.session_state.data_c1[d][f"habit_{i}"]) + st.session_state.data_c1[d]["bonus"] for d in range(1, 29))
    c2_total = sum(sum(1 for i in range(1, 11) if st.session_state.data_c2[d][f"habit_{i}"]) + st.session_state.data_c2[d]["bonus"] for d in range(1, 29))
    combined_total = c1_total + c2_total
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Contestant 1", f"{c1_total} pts")
    col_b.metric("Contestant 2", f"{c2_total} pts")
    col_c.metric("Combined Team Total", f"{combined_total} / 560 pts")
    
    st.write("---")
    st.subheader("🎉 Joint Team Goal Status (Target: 500+ Combined Points)")
    if combined_total >= 500:
        st.markdown('<p class="success-box">🥂 UNLOCKED! Spa Day, Lunch & Shopping Trip Achieved Together! Amazing job!</p>', unsafe_allow_html=True)
    else:
        points_needed = 500 - combined_total
        st.info(f"🎯 **{max(0, points_needed)} more combined points** needed to unlock your joint Girls' Day Out reward!")
