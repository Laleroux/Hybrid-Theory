import streamlit as st
import pandas as pd
import json
import os
import datetime
import altair as alt

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
DATA_FILE = "challenge_data_v3.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                # Ensure backward compatibility for colors
                if "contestants" in data:
                    default_colors = ["#FF69B4", "#3366CC", "#109618", "#FF9900", "#990099", "#0099C6", "#DD4477", "#66AA00", "#B82E2E", "#316395"]
                    for idx, (name, c_info) in enumerate(data["contestants"].items()):
                        if "color" not in c_info:
                            c_info["color"] = default_colors[idx % len(default_colors)]
                return data
        except Exception:
            pass
    
    # Default initial state with 2 default contestants, colors, and a start date
    default_structure = {
        "start_date": "2026-09-01",
        "contestants": {
            "Contestant 1": {"email": "", "color": "#FF69B4", "days": {str(day): {f"habit_{i}": False for i in range(1, 11)} | {"bonus": 0, "notes": ""} for day in range(1, 29)}},
            "Contestant 2": {"email": "", "color": "#3366CC", "days": {str(day): {f"habit_{i}": False for i in range(1, 11)} | {"bonus": 0, "notes": ""} for day in range(1, 29)}}
        }
    }
    return default_structure

def save_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        st.error(f"Error saving data: {e}")

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

# --- SIDEBAR: CHALLENGE & CONTESTANT MANAGEMENT ---
st.sidebar.subheader("📅 Challenge Calendar Sync")
current_start_str = st.session_state.app_data.get("start_date", "2026-09-01")
try:
    parsed_start_date = datetime.date.fromisoformat(current_start_str)
except ValueError:
    parsed_start_date = datetime.date(2026, 9, 1)

selected_start_date = st.sidebar.date_input("Challenge Start Date", value=parsed_start_date)
st.session_state.app_data["start_date"] = selected_start_date.isoformat()

st.sidebar.markdown("---")
st.sidebar.subheader("👥 Contestants Management (Max 10)")

contestant_names = list(st.session_state.app_data["contestants"].keys())

# Add new contestant
if len(contestant_names) < 10:
    new_name = st.sidebar.text_input("Add New Contestant Name")
    if st.sidebar.button("Add Contestant") and new_name:
        if new_name in contestant_names:
            st.sidebar.error("Contestant name already exists!")
        else:
            default_colors = ["#FF69B4", "#3366CC", "#109618", "#FF9900", "#990099", "#0099C6", "#DD4477", "#66AA00", "#B82E2E", "#316395"]
            assigned_color = default_colors[len(contestant_names) % len(default_colors)]
            st.session_state.app_data["contestants"][new_name] = {
                "email": "",
                "color": assigned_color,
                "days": {str(day): {f"habit_{i}": False for i in range(1, 11)} | {"bonus": 0, "notes": ""} for day in range(1, 29)}
            }
            save_data(st.session_state.app_data)
            st.rerun()

# Remove existing contestants
if len(contestant_names) > 1:
    with st.sidebar.expander("Manage Existing Contestants"):
        target_to_remove = st.selectbox("Select to Remove", ["None"] + contestant_names)
        if target_to_remove != "None" and st.button("Remove Contestant"):
            del st.session_state.app_data["contestants"][target_to_remove]
            save_data(st.session_state.app_data)
            st.rerun()

# Refresh contestant list after potential modifications
contestant_names = list(st.session_state.app_data["contestants"].keys())

# Contestant Line Colors Configuration for Graphs
st.sidebar.markdown("---")
st.sidebar.subheader("🎨 Contestant Line Colors")
for name in contestant_names:
    c_info = st.session_state.app_data["contestants"][name]
    current_color = c_info.get("color", "#FF69B4")
    new_color = st.sidebar.color_picker(f"{name} Color", value=current_color, key=f"color_{name}")
    c_info["color"] = new_color
save_data(st.session_state.app_data)

st.sidebar.markdown("---")
view_mode = st.sidebar.radio("Navigation", ["Daily Logger", "28-Day Overview Grid", "Rules & Guidelines", "Analytics & Graphs", "Leaderboard & Reports"])

# Helper function to calculate totals
def calculate_total(c_name):
    total = 0
    c_days = st.session_state.app_data["contestants"][c_name]["days"]
    for day in range(1, 29):
        d_str = str(day)
        core = sum(1 for i in range(1, 11) if c_days[d_str].get(f"habit_{i}", False))
        bonus = c_days[d_str].get("bonus", 0)
        total += core + bonus
    return total

# Generate Date Mapping dictionary for the 28 days
start_dt = datetime.date.fromisoformat(st.session_state.app_data["start_date"])
day_date_map = {day: start_dt + datetime.timedelta(days=day-1) for day in range(1, 29)}

if view_mode == "Daily Logger":
    current_profile = st.selectbox("Select Profile", contestant_names)
    
    # Email input field
    c_data_profile = st.session_state.app_data["contestants"][current_profile]
    user_email = st.text_input(f"📧 Email Address for Weekly Reports ({current_profile})", value=c_data_profile.get("email", ""))
    c_data_profile["email"] = user_email
    
    # Day selection formatted with real calendar dates
    selected_day = st.selectbox(
        "Select Day to Log", 
        list(range(1, 29)), 
        format_func=lambda x: f"Day {x} — {day_date_map[x].strftime('%A, %d %B %Y')}"
    )
    
    day_str = str(selected_day)
    day_state = c_data_profile["days"][day_str]
    
    st.write(f"### 📝 Check-in for Day {selected_day} ({day_date_map[selected_day].strftime('%d %B %Y')}) — {current_profile}")
    
    # Render Checkboxes cleanly without individual info dropdowns
    col1, col2 = st.columns(2)
    
    with col1:
        for i in range(1, 6):
            h_key = f"habit_{i}"
            day_state[h_key] = st.checkbox(habits_info[h_key][0], value=day_state.get(h_key, False), key=f"{current_profile}_d{selected_day}_{h_key}")
    with col2:
        for i in range(6, 11):
            h_key = f"habit_{i}"
            day_state[h_key] = st.checkbox(habits_info[h_key][0], value=day_state.get(h_key, False), key=f"{current_profile}_d{selected_day}_{h_key}")

    # Bonus Points Input
    bonus_pts = st.number_input("⭐ Daily Bonus Points (Max 3)", min_value=0, max_value=3, value=day_state.get("bonus", 0), key=f"{current_profile}_d{selected_day}_bonus")
    day_state["bonus"] = bonus_pts

    # Daily Notes / Journal
    daily_notes = st.text_area("📖 Daily Notes / Reflections / Prayer Journal", value=day_state.get("notes", ""), key=f"{current_profile}_d{selected_day}_notes")
    day_state["notes"] = daily_notes

    # Save automatically to JSON
    save_data(st.session_state.app_data)

    # Calculate Daily Subtotal
    core_completed = sum(1 for i in range(1, 11) if day_state.get(f"habit_{i}", False))
    daily_total = core_completed + bonus_pts
    
    st.write("---")
    st.info(f"✨ **Day {selected_day} Score:** {core_completed} (Core) + {bonus_pts} (Bonus) = **{daily_total} Points**")

    # --- WARNING LOGIC ---
    if daily_total < 5:
        st.markdown(f'<p class="alert-box">⚠️ Low Score Warning: Your daily score is {daily_total} (below 5 points). Let\'s push to hit more habits tomorrow!</p>', unsafe_allow_html=True)

    if selected_day > 1:
        prev_day_str = str(selected_day - 1)
        prev_core = sum(1 for i in range(1, 11) if c_data_profile["days"][prev_day_str].get(f"habit_{i}", False))
        if core_completed < 7 and prev_core < 7:
            st.markdown('<p class="alert-box">🚨 "Never Miss Twice" Alert: Your core score has dropped below 7 for two consecutive days. Time for a quick bounce-back!</p>', unsafe_allow_html=True)

    if selected_day > 1:
        prev_day_str = str(selected_day - 1)
        prev_day_data = c_data_profile["days"][prev_day_str]
        missed_twice_list = []
        for i in range(1, 11):
            h_key = f"habit_{i}"
            if not day_state.get(h_key, False) and not prev_day_data.get(h_key, False):
                missed_twice_list.append(habits_info[h_key][0])
        
        if missed_twice_list:
            missed_str = ", ".join([item.split(". ")[1] for item in missed_twice_list])
            st.markdown(f'<p class="alert-box">🔄 Habit Repeat Miss Warning: You have missed the following item(s) two days in a row: <b>{missed_str}</b>. Focus on breaking this streak!</p>', unsafe_allow_html=True)

    # Cumulative Progress
    total_cumulative = calculate_total(current_profile)
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
    current_profile = st.selectbox("Select Profile for Grid", contestant_names)
    
    grid_data = []
    c_days = st.session_state.app_data["contestants"][current_profile]["days"]
    for day in range(1, 29):
        d_str = str(day)
        core = sum(1 for i in range(1, 11) if c_days[d_str].get(f"habit_{i}", False))
        bonus = c_days[d_str].get("bonus", 0)
        notes = c_days[d_str].get("notes", "")
        grid_data.append({
            "Day": f"Day {day}",
            "Date": day_date_map[day].strftime('%d %b %Y'),
            "Core Habits (/10)": core,
            "Bonus": bonus,
            "Total": core + bonus,
            "Notes / Journal": notes if notes else "—"
        })
    
    df_grid = pd.DataFrame(grid_data)
    st.dataframe(df_grid, use_container_width=True)

elif view_mode == "Rules & Guidelines":
    st.subheader("📜 Challenge Rules & Guidelines")
    st.markdown("Welcome to the **28-Day Hybrid Habit Challenge**! Remember our core philosophy: **Consistency over perfection. Never miss twice!**")
    st.markdown("---")
    
    st.markdown("### 📋 Daily Habit Guidelines")
    for h_key, (title, desc) in habits_info.items():
        st.markdown(f"**{title}**")
        st.markdown(f"> {desc}")
        st.markdown("")
        
    st.markdown("---")
    st.markdown("### ⭐ Bonus Points (Max 3 per day)")
    st.markdown("You can earn up to **3 extra bonus points** each day by completing additional stretch goals, such as extra physical activity, dedicated deep-work sessions, or going above and beyond your daily routine.")
    
    st.markdown("### ⚠️ The 'Never Miss Twice' Rule")
    st.markdown("Life happens, and missing a habit once is entirely fine! However, the golden rule is **never miss the same habit two days in a row**. The app will actively alert you if a core score drops too low or if any habit is missed on consecutive days.")

    st.markdown("### 🏆 Milestone Rewards")
    st.markdown("- **100 Points:** Level 1 Unlocked — *Little Treat*")
    st.markdown("- **200 Points:** Level 2 Unlocked — *Mid-Challenge Reward*")
    st.markdown("- **280 Points:** Level 3 Unlocked — *Full Transformation Grand Reward*")

    st.markdown("### 🥂 Group Joint Goal")
    st.markdown("- **500+ Combined Points:** Spa Day, Lunch & Shopping Trip Achieved Together!")

elif view_mode == "Analytics & Graphs":
    st.subheader("📈 Contestants Cumulative Progress Line Graph")
    st.markdown("Compare the performance and trajectory of all contestants across the 28-day challenge.")
    
    chart_data = []
    contestants_dict = st.session_state.app_data["contestants"]
    
    for name, c_info in contestants_dict.items():
        running_total = 0
        c_days = c_info["days"]
        for day in range(1, 29):
            d_str = str(day)
            core = sum(1 for i in range(1, 11) if c_days[d_str].get(f"habit_{i}", False))
            bonus = c_days[d_str].get("bonus", 0)
            running_total += core + bonus
            chart_data.append({
                "Day": day,
                "Contestant": name,
                "Cumulative Points": running_total
            })
            
    df_chart = pd.DataFrame(chart_data)
    
    # Extract custom contestant colors mapped to Altair scale
    color_domain = list(contestants_dict.keys())
    color_range = [contestants_dict[name].get("color", "#1f77b4") for name in color_domain]
    
    line_chart = alt.Chart(df_chart).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X('Day:Q', title='Day of Challenge'),
        y=alt.Y('Cumulative Points:Q', title='Cumulative Points'),
        color=alt.Color('Contestant:N', scale=alt.Scale(domain=color_domain, range=color_range), title='Contestant'),
        tooltip=['Contestant', 'Day', 'Cumulative Points']
    ).properties(
        width=700,
        height=450
    ).interactive()
    
    st.altair_chart(line_chart, use_container_width=True)

else:
    st.subheader("📊 Group Leaderboard & Weekly Reports")
    
    contestant_totals = {name: calculate_total(name) for name in contestant_names}
    combined_total = sum(contestant_totals.values())
    
    cols = st.columns(len(contestant_names) if len(contestant_names) <= 3 else 3)
    for idx, (name, pts) in enumerate(contestant_totals.items()):
        col_idx = idx % 3
        cols[col_idx].metric(name, f"{pts} pts")
    
    st.metric("Combined Group Total", f"{combined_total} pts")
    
    st.write("---")
    st.subheader("🎉 Group Joint Goal Status (Target: 500+ Combined Points)")
    if combined_total >= 500:
        st.markdown('<p class="success-box">🥂 UNLOCKED! Spa Day, Lunch & Shopping Trip Achieved Together! Amazing job!</p>', unsafe_allow_html=True)
        st.balloons()
    else:
        points_needed = 500 - combined_total
        st.info(f"🎯 **{max(0, points_needed)} more combined points** needed to unlock your joint group reward!")

    st.write("---")
    st.subheader("📧 Weekly Habit Performance Report Simulator")
    report_profile = st.selectbox("Select Profile for Report", contestant_names, key="rep_profile")
    rep_data = st.session_state.app_data["contestants"][report_profile]
    rep_email = rep_data.get("email", "")
    
    if st.button("📥 Generate Weekly Report Summary"):
        st.success(f"Report compiled successfully for **{report_profile}** (Target Email: {rep_email if rep_email else 'No email set yet'})!")
        
        total_gained = calculate_total(report_profile)
        
        missed_counts = {f"habit_{i}": 0 for i in range(1, 11)}
        for day in range(1, 29):
            d_str = str(day)
            for i in range(1, 11):
                h_key = f"habit_{i}"
                if not rep_data["days"][d_str].get(h_key, False):
                    missed_counts[h_key] += 1
                    
        st.write(f"### 📋 Performance Breakdown for {report_profile}")
        st.write(f"- **Total Accumulated Points:** {total_gained}")
        st.write(f"- **Challenge Start Date Synced:** {start_dt.strftime('%d %B %Y')}")
        st.write(f"- **Areas where points were gained:** Consistent core habit completions & daily bonuses.")
        st.write(f"- **Habit Drop-off Areas (Most missed items across recorded days):**")
        
        sorted_misses = sorted(missed_counts.items(), key=lambda x: x[1], reverse=True)
        for h_key, count in sorted_misses[:3]:
            st.write(f"  * *{habits_info[h_key][0]}* (Missed {count} times)")
            
        if rep_email:
            st.info(f"📬 In a fully hosted deployment, this formatted report would automatically be dispatched to **{rep_email}** every week!")
        else:
            st.warning("⚠️ Enter your email address in the Daily Logger view to enable automatic weekly report deliveries.")
 
