import streamlit as st
import pandas as pd
import json
import os

# Page Configuration
st.set_page_config(page_title="28-Day Hybrid Habit Challenge", page_icon="🌸", layout="centered")

# Custom Styling
st.markdown("""
    <style>
    .main-title { font-size: 26px; font-weight: bold; color: #2E4053; text-align: center; }
    .subtitle { font-size: 14px; color: #7F8C8D; text-align: center; margin-bottom: 20px; }
    .alert-box { background-color: #FADBD8; padding: 12px; border-radius: 8px; color: #922B21; font-weight: bold; margin-bottom: 10px; }
    .success-box { background-color: #D4EFDF; padding: 12px; border-radius: 8px; color: #145A32; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🌸 28-Day Hybrid Habit Challenge</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Consistency over perfection. Never miss twice!</p>', unsafe_allow_html=True)

# Data Persistence File
DATA_FILE = "challenge_data_v2.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    # Default initial state with customizable names and emails
    default_structure = {
        "names": {"c1": "Contestant 1", "c2": "Contestant 2"},
        "emails": {"c1": "", "c2": ""},
        "Contestant 1": {str(day): {f"habit_{i}": False for i in range(1, 11)} | {"bonus": 0, "notes": ""} for day in range(1, 29)},
        "Contestant 2": {str(day): {f"habit_{i}": False for i in range(1, 11)} | {"bonus": 0, "notes": ""} for day in range(1, 29)}
    }
    return default_structure

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

if "app_data" not in st.session_state:
    st.session_state.app_data = load_data()

# Habit definitions and detailed info sheets
habits_info = {
    "habit_1": ("1. Hydration (Water Goal)", "💧 **Guideline:** Drink between 6 to 8 glasses of water a day."),
    "habit_2": ("2. Unified Nutrition (Calories & Clean Meals)", "🥗 **Guideline:** Stick to the high-volume 1500-calorie clean meal structure (gluten-free, lactose-free, sugar-free)."),
    "habit_3": ("3. Protein & Greens Target", "🥩 **Guideline:** Prioritize lean proteins (chicken, extra-lean beef mince, steak, tuna, whey) and volume vegetables."),
    "habit_4": ("4. Daily Movement / Step Count", "🚶‍♀️ **Guideline:** Walk between 8,000 and 10,000 steps daily."),
    "habit_5": ("5. Structured Workout / Active Recovery", "💪 **Guideline:** Complete your scheduled resistance workout or dedicated active recovery session."),
    "habit_6": ("6. Spiritual Time (Bible / Prayer)", "📖 **Guideline:** Dedicate quiet time to prayer, scripture reading, or spiritual reflection."),
    "habit_7": ("7. Bedtime Discipline", "🌙 **Guideline:** Wind down and get to bed on time to ensure quality rest."),
    "habit_8": ("8. Screen-Free Wind-Down (30 min)", "📵 **Guideline:** Disconnect from phones and screens for at least 30 minutes before sleep."),
    "habit_9": ("9. Self-Care / Skincare Routine", "✨ **Guideline:** Complete your intentional skincare and personal self-care rituals."),
    "habit_10": ("10. Mental Wellbeing Activity", "🧘‍♀️ **Guideline:** Engage in an activity that boosts mental wellness, reading, journaling, or relaxing.")
}

# Sidebar Profile & Name Settings
st.sidebar.subheader("⚙️ Challenge Settings")
c1_editable = st.sidebar.text_input("Name for Profile 1", value=st.session_state.app_data["names"]["c1"])
c2_editable = st.sidebar.text_input("Name for Profile 2", value=st.session_state.app_data["names"]["c2"])

st.session_state.app_data["names"]["c1"] = c1_editable
st.session_state.app_data["names"]["c2"] = c2_editable

# Save names back to structure keys if they changed
name_map = {c1_editable: "Contestant 1", c2_editable: "Contestant 2"}
profile_options = [c1_editable, c2_editable]

view_mode = st.sidebar.radio("Navigation", ["Daily Logger", "28-Day Overview Grid", "Combined Scoreboard & Reports"])

def get_internal_key(display_name):
    return "Contestant 1" if display_name == c1_editable else "Contestant 2"

def calculate_total(contestant_key):
    total = 0
    c_data = st.session_state.app_data[contestant_key]
    for day in range(1, 29):
        d_str = str(day)
        core = sum(1 for i in range(1, 11) if c_data[d_str].get(f"habit_{i}", False))
        bonus = c_data[d_str].get("bonus", 0)
        total += core + bonus
    return total

if view_mode == "Daily Logger":
    current_profile_display = st.selectbox("Select Profile", profile_options)
    internal_key = get_internal_key(current_profile_display)
    
    # Email input field for weekly report
    current_email_key = "c1" if internal_key == "Contestant 1" else "c2"
    user_email = st.text_input(f"📧 Email Address for Weekly Reports ({current_profile_display})", value=st.session_state.app_data["emails"][current_email_key])
    st.session_state.app_data["emails"][current_email_key] = user_email
    
    selected_day = st.selectbox("Select Day to Log", list(range(1, 29)), format_func=lambda x: f"Day {x}")
    
    day_str = str(selected_day)
    day_state = st.session_state.app_data[internal_key][day_str]
    
    st.write(f"### 📝 Check-in for Day {selected_day} — {current_profile_display}")
    st.info("💡 *Tip: Click on the 'ℹ️ Info' expander next to any habit to review its specific daily rule.*")
    
    # Render Checkboxes with Info expanders
    col1, col2 = st.columns(2)
    
    def render_habit_item(i, column):
        h_key = f"habit_{i}"
        title, info_text = habits_info[h_key]
        with column:
            c_col, i_col = st.columns([0.8, 0.2])
            with c_col:
                day_state[h_key] = st.checkbox(title, value=day_state.get(h_key, False), key=f"{internal_key}_d{selected_day}_{h_key}")
            with i_col:
                with st.popover("ℹ️"):
                    st.markdown(info_text)

    with col1:
        for i in range(1, 6):
            render_habit_item(i, col1)
    with col2:
        for i in range(6, 11):
            render_habit_item(i, col2)

    # Bonus Points Input
    bonus_pts = st.number_input("⭐ Daily Bonus Points (Max 3)", min_value=0, max_value=3, value=day_state.get("bonus", 0), key=f"{internal_key}_d{selected_day}_bonus")
    day_state["bonus"] = bonus_pts

    # Daily Notes / Journal
    daily_notes = st.text_area("📖 Daily Notes / Reflections / Prayer Journal", value=day_state.get("notes", ""), key=f"{internal_key}_d{selected_day}_notes")
    day_state["notes"] = daily_notes

    # Save automatically to JSON
    save_data(st.session_state.app_data)

    # Calculate Daily Subtotal
    core_completed = sum(1 for i in range(1, 11) if day_state.get(f"habit_{i}", False))
    daily_total = core_completed + bonus_pts
    
    st.write("---")
    st.info(f"✨ **Day {selected_day} Score:** {core_completed} (Core) + {bonus_pts} (Bonus) = **{daily_total} Points**")

    # --- WARNING LOGIC ---
    # 1. Warning if daily score is below 5
    if daily_total < 5:
        st.markdown(f'<p class="alert-box">⚠️ Low Score Warning: Your daily score is {daily_total} (below 5 points). Let\'s push to hit more habits tomorrow!</p>', unsafe_allow_html=True)

    # 2. Warning if core score < 7 for two consecutive days ("Never Miss Twice")
    if selected_day > 1:
        prev_day_str = str(selected_day - 1)
        prev_core = sum(1 for i in range(1, 11) if st.session_state.app_data[internal_key][prev_day_str].get(f"habit_{i}", False))
        if core_completed < 7 and prev_core < 7:
            st.markdown('<p class="alert-box">🚨 "Never Miss Twice" Alert: Your core score has dropped below 7 for two consecutive days. Time for a quick bounce-back!</p>', unsafe_allow_html=True)

    # 3. Warning if the SAME individual item has been missed twice in a row
    if selected_day > 1:
        prev_day_str = str(selected_day - 1)
        prev_day_data = st.session_state.app_data[internal_key][prev_day_str]
        missed_twice_list = []
        for i in range(1, 11):
            h_key = f"habit_{i}"
            if not day_state.get(h_key, False) and not prev_day_data.get(h_key, False):
                missed_twice_list.append(habits_info[h_key][0])
        
        if missed_twice_list:
            missed_str = ", ".join([item.split(". ")[1] for item in missed_twice_list])
            st.markdown(f'<p class="alert-box">🔄 Habit Repeat Miss Warning: You have missed the following item(s) two days in a row: <b>{missed_str}</b>. Focus on breaking this streak!</p>', unsafe_allow_html=True)

    # Cumulative Progress on Logger screen
    total_cumulative = calculate_total(internal_key)
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
    current_profile_display = st.selectbox("Select Profile for Grid", profile_options)
    internal_key = get_internal_key(current_profile_display)
    
    grid_data = []
    c_data = st.session_state.app_data[internal_key]
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
    st.subheader("📊 Team Leaderboard & Weekly Reports")
    
    c1_total = calculate_total("Contestant 1")
    c2_total = calculate_total("Contestant 2")
    combined_total = c1_total + c2_total
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric(c1_editable, f"{c1_total} pts")
    col_b.metric(c2_editable, f"{c2_total} pts")
    col_c.metric("Combined Total", f"{combined_total} / 560 pts")
    
    st.write("---")
    st.subheader("🎉 Joint Team Goal Status (Target: 500+ Combined Points)")
    if combined_total >= 500:
        st.markdown('<p class="success-box">🥂 UNLOCKED! Spa Day, Lunch & Shopping Trip Achieved Together! Amazing job!</p>', unsafe_allow_html=True)
        st.balloons()
    else:
        points_needed = 500 - combined_total
        st.info(f"🎯 **{max(0, points_needed)} more combined points** needed to unlock your joint Girls' Day Out reward!")

    st.write("---")
    st.subheader("📧 Weekly Habit Performance Report Simulator")
    st.write("Generate a detailed summary breakdown of points gained and habits missed to review or email out:")
    
    report_profile = st.selectbox("Select Profile for Report", profile_options, key="rep_profile")
    rep_internal = get_internal_key(report_profile)
    rep_email = st.session_state.app_data["emails"]["c1" if rep_internal == "Contestant 1" else "c2"]
    
    if st.button("📥 Generate Weekly Report Summary"):
        st.success(f"Report compiled successfully for **{report_profile}** (Target Email: {rep_email if rep_email else 'No email set yet'})!")
        
        # Calculate weekly breakdown stats
        c_data = st.session_state.app_data[rep_internal]
        total_gained = calculate_total(rep_internal)
        
        # Count missed habits across all days logged so far
        missed_counts = {f"habit_{i}": 0 for i in range(1, 11)}
        for day in range(1, 29):
            d_str = str(day)
            for i in range(1, 11):
                h_key = f"habit_{i}"
                if not c_data[d_str].get(h_key, False):
                    missed_counts[h_key] += 1
                    
        st.write(f"### 📋 Performance Breakdown for {report_profile}")
        st.write(- f"**Total Accumulated Points:** {total_gained}")
        st.write(f"**Areas where points were gained:** Consistent core habit completions & daily bonuses.")
        st.write(f"**Habit Drop-off Areas (Most missed items across recorded days):**")
        
        sorted_misses = sorted(missed_counts.items(), key=lambda x: x[1], reverse=True)
        for h_key, count in sorted_misses[:3]: # show top 3 missed
            st.write(f"- *{habits_info[h_key][0]}* (Missed {count} times)")
            
        if rep_email:
            st.info(f"📬 In a fully hosted deployment, this formatted report would automatically be dispatched to **{rep_email}** every week!")
        else:
            st.warning("⚠️ Enter your email address in the Daily Logger sidebar/menu to enable automatic weekly report deliveries.")
 
