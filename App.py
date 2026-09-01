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
DATA_FILE = "challenge_data_v2.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    # Default initial state with 2 default contestants and email structure
    default_structure = {
        "Contestant 1": {
            "email": "",
            "days": {str(day): {f"habit_{i}": False for i in range(1, 11)} | {"bonus": 0, "notes": ""} for day in range(1, 29)}
        },
        "Contestant 2": {
            "email": "",
            "days": {str(day): {f"habit_{i}": False for i in range(1, 11)} | {"bonus": 0, "notes": ""} for day in range(1, 29)}
        }
    }
    return default_structure

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Initialize Session State
if "app_data" not in st.session_state:
    st.session_state.app_data = load_data()

# --- SIDEBAR: CONTESTANTS MANAGEMENT & NAVIGATION ---
st.sidebar.subheader("👥 Contestants Management (Max 10)")
contestant_names = list(st.session_state.app_data.keys())

# Add new contestant if under 10
if len(contestant_names) < 10:
    new_name = st.sidebar.text_input("Add New Contestant Name")
    if st.sidebar.button("Add Contestant") and new_name:
        if new_name in contestant_names:
            st.sidebar.error("Contestant name already exists!")
        else:
            st.session_state.app_data[new_name] = {
                "email": "",
                "days": {str(day): {f"habit_{i}": False for i in range(1, 11)} | {"bonus": 0, "notes": ""} for day in range(1, 29)}
            }
            save_data(st.session_state.app_data)
            st.rerun()

# Remove existing contestants (must keep at least 1)
if len(contestant_names) > 1:
    with st.sidebar.expander("Manage Existing Contestants"):
        target_to_remove = st.selectbox("Select to Remove", ["None"] + contestant_names)
        if target_to_remove != "None" and st.button("Remove Contestant"):
            del st.session_state.app_data[target_to_remove]
            save_data(st.session_state.app_data)
            st.rerun()

contestant_names = list(st.session_state.app_data.keys())

st.sidebar.markdown("---")
view_mode = st.sidebar.radio("Navigation", ["Daily Logger", "28-Day Overview Grid", "Combined Scoreboard & Reports"])

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

def calculate_total(contestant_entry):
    total = 0
    c_days = contestant_entry["days"]
    for day in range(1, 29):
        d_str = str(day)
        core = sum(1 for i in range(1, 11) if c_days[d_str].get(f"habit_{i}", False))
        bonus = c_days[d_str].get("bonus", 0)
        total += core + bonus
    return total

if view_mode == "Daily Logger":
    contestant = st.selectbox("Select Profile", contestant_names)
    c_data = st.session_state.app_data[contestant]
    
    # Email input field for weekly reports
    user_email = st.text_input(f"📧 Email Address for Weekly Reports ({contestant})", value=c_data.get("email", ""))
    c_data["email"] = user_email
    
    selected_day = st.selectbox("Select Day to Log", list(range(1, 29)), format_func=lambda x: f"Day {x}")
    
    day_str = str(selected_day)
    day_state = c_data["days"][day_str]
    
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
        prev_core = sum(1 for i in range(1, 11) if c_data["days"][prev_day_str].get(f"habit_{i}", False))
        if core_completed < 7 and prev_core < 7:
            st.markdown('<p class="alert-box">🚨 "Never Miss Twice" Alert: Your core score has dropped below 7 for two consecutive days. Time for a quick bounce-back tomorrow!</p>', unsafe_allow_html=True)

    # Cumulative Progress on Logger screen
    total_cumulative = calculate_total(c_data)
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
    contestant = st.selectbox("Select Profile for Grid", contestant_names)
    
    grid_data = []
    c_days = st.session_state.app_data[contestant]["days"]
    for day in range(1, 29):
        d_str = str(day)
        core = sum(1 for i in range(1, 11) if c_days[d_str].get(f"habit_{i}", False))
        bonus = c_days[d_str].get("bonus", 0)
        notes = c_days[d_str].get("notes", "")
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
    st.subheader("📊 Team Leaderboard & Weekly Reports")
    
    contestant_totals = {name: calculate_total(st.session_state.app_data[name]) for name in contestant_names}
    combined_total = sum(contestant_totals.values())
    
    cols = st.columns(len(contestant_names) if len(contestant_names) <= 3 else 3)
    for idx, (name, pts) in enumerate(contestant_totals.items()):
        col_idx = idx % 3
        cols[col_idx].metric(name, f"{pts} pts")
    
    st.metric("Combined Team Total", f"{combined_total} pts")
    
    st.write("---")
    st.subheader("🎉 Joint Team Goal Status (Target: 500+ Combined Points)")
    if combined_total >= 500:
        st.markdown('<p class="success-box">🥂 UNLOCKED! Spa Day, Lunch & Shopping Trip Achieved Together! Amazing job!</p>', unsafe_allow_html=True)
        st.balloons()
    else:
        points_needed = 500 - combined_total
        st.info(f"🎯 **{max(0, points_needed)} more combined points** needed to unlock your joint Girls' Day Out reward!")

    st.write("---")
    st.subheader("📧 Weekly Habit Performance Report Generator")
    report_contestant = st.selectbox("Select Contestant for Weekly Report", contestant_names, key="rep_select")
    rep_entry = st.session_state.app_data[report_contestant]
    rep_email = rep_entry.get("email", "")
    
    if st.button("📥 Generate Weekly Overview Summary"):
        st.success(f"Weekly report generated successfully for **{report_contestant}**!")
        total_pts = calculate_total(rep_entry)
        
        # Calculate most missed habits across recorded entries
        missed_counts = {f"habit_{i}": 0 for i in range(1, 11)}
        for day in range(1, 29):
            d_str = str(day)
            for i in range(1, 11):
                h_key = f"habit_{i}"
                if not rep_entry["days"][d_str].get(h_key, False):
                    missed_counts[h_key] += 1
                    
        st.write(f"### 📋 Weekly Overview for {report_contestant}")
        st.write(f"- **Total Accumulated Points:** {total_pts}")
        st.write(f"- **Registered Email:** {rep_email if rep_email else 'Not provided yet'}")
        st.write(f"- **Habit Drop-off Areas (Most missed items):**")
        
        sorted_misses = sorted(missed_counts.items(), key=lambda x: x[1], reverse=True)
        for h_key, count in sorted_misses[:3]:
            habit_name = habits_list[int(h_key.split('_')[1])-1]
            st.write(f"  * *{habit_name}* (Missed across {count} logged days)")
            
        if rep_email:
            st.info(f"📬 In a fully live web deployment, this formatted summary would be automatically emailed to **{rep_email}**.")
        else:
            st.warning("⚠️ Enter your email address in the Daily Logger view to prepare for automated weekly report delivery.")
