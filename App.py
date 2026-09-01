import streamlit as st
import pandas as pd
import json
import os
import datetime
import altair as alt

# Page Configuration
st.set_page_config(page_title="Hybrid Theory - 28 Day Challenge", page_icon="🌸", layout="centered")

# Ensure uploads directory exists for photo proof
os.makedirs("uploads", exist_ok=True)

# Custom Styling (Updated Font Sizing: Main Title 60px, Sub-Title 58px, Subsections 50px)
st.markdown("""
    <style>
    .main-title { font-size: 60px; font-weight: 800; color: #2E4053; text-align: center; margin-bottom: 0px; line-height: 1.1; }
    .sub-title { font-size: 58px; font-weight: 700; color: #566573; text-align: center; margin-top: 4px; margin-bottom: 4px; line-height: 1.1; }
    .subtitle { font-size: 14px; color: #7F8C8D; text-align: center; margin-bottom: 25px; }
    .section-header { font-size: 50px; font-weight: 700; color: #34495E; margin-top: 20px; margin-bottom: 12px; line-height: 1.1; }
    .alert-box { background-color: #FADBD8; padding: 12px; border-radius: 8px; color: #922B21; font-weight: bold; margin-bottom: 10px; }
    .success-box { background-color: #D4EFDF; padding: 12px; border-radius: 8px; color: #145A32; font-weight: bold; }
    .activity-card { background-color: #F8F9F9; padding: 10px; border-left: 4px solid #3366CC; border-radius: 4px; margin-bottom: 8px; font-size: 13px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">Hybrid Theory</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">28 Day Challenge</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Consistency over perfection. Never miss twice!</p>', unsafe_allow_html=True)

# Data Persistence File
DATA_FILE = "challenge_data_v6.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                if "contestants" in data:
                    default_colors = ["#FF69B4", "#3366CC", "#109618", "#FF9900", "#990099", "#0099C6", "#DD4477", "#66AA00", "#B82E2E", "#316395"]
                    for idx, (name, c_info) in enumerate(data["contestants"].items()):
                        if "color" not in c_info:
                            c_info["color"] = default_colors[idx % len(default_colors)]
                return data
        except Exception:
            pass
    
    default_structure = {
        "start_date": "2026-09-01",
        "contestants": {
            "Contestant 1": {"email": "", "color": "#FF69B4", "days": {str(day): {f"habit_{i}": False for i in range(1, 11)} | {"notes": "", "photo": ""} for day in range(1, 29)}},
            "Contestant 2": {"email": "", "color": "#3366CC", "days": {str(day): {f"habit_{i}": False for i in range(1, 11)} | {"notes": "", "photo": ""} for day in range(1, 29)}}
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

# Updated Habit definitions
habits_info = {
    "habit_1": ("1. Daily H2O", "💧 **Guideline:** Drink between 6 to 8 glasses of water a day."),
    "habit_2": ("2. Clean Fuel (1,500 Cal)", "🥗 **Guideline:** Stick to the high-volume 1500-calorie clean meal structure (gluten-free, lactose-free, sugar-free)."),
    "habit_3": ("3. Lean & Green", "🥩 **Guideline:** Prioritize lean proteins (chicken, extra-lean beef mince, steak, tuna, whey) and volume vegetables."),
    "habit_4": ("4. 8k - 10k step goal", "🚶‍♀️ **Guideline:** Walk between 8,000 and 10,000 steps daily."),
    "habit_5": ("5. Daily Fitness Session", "💪 **Guideline:** Complete your scheduled resistance workout or dedicated active recovery session."),
    "habit_6": ("6. Word & Prayer", "📖 **Guideline:** Dedicate quiet time to prayer, scripture reading, or spiritual reflection."),
    "habit_7": ("7. Lights Out Goal", "🌙 **Guideline:** Wind down and get to bed on time to ensure quality rest."),
    "habit_8": ("8. Pre-Sleep Unplug", "📵 **Guideline:** Disconnect from phones and screens for at least 30 minutes before sleep."),
    "habit_9": ("9. Glow Routine", "✨ **Guideline:** Complete your intentional skincare and personal self-care rituals."),
    "habit_10": ("10. Mind & Journal", "🧘‍♀️ **Guideline:** Engage in an activity that boosts mental wellness, reading, journaling, or relaxing.")
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
                "days": {str(day): {f"habit_{i}": False for i in range(1, 11)} | {"notes": "", "photo": ""} for day in range(1, 29)}
            }
            save_data(st.session_state.app_data)
            st.rerun()

if len(contestant_names) > 1:
    with st.sidebar.expander("Manage Existing Contestants"):
        target_to_remove = st.selectbox("Select to Remove", ["None"] + contestant_names)
        if target_to_remove != "None" and st.button("Remove Contestant"):
            del st.session_state.app_data["contestants"][target_to_remove]
            save_data(st.session_state.app_data)
            st.rerun()

contestant_names = list(st.session_state.app_data["contestants"].keys())

st.sidebar.markdown("---")
st.sidebar.subheader("🎨 Contestant Line Colors")
for name in contestant_names:
    c_info = st.session_state.app_data["contestants"][name]
    current_color = c_info.get("color", "#FF69B4")
    new_color = st.sidebar.color_picker(f"{name} Color", value=current_color, key=f"color_{name}")
    c_info["color"] = new_color
save_data(st.session_state.app_data)

st.sidebar.markdown("---")
view_mode = st.sidebar.radio("Navigation", ["Daily Logger", "28-Day Overview Grid", "Rules & Guidelines", "Analytics & Graphs", "Leaderboard & Activity Feed"])

def calculate_total(c_name):
    total = 0
    c_days = st.session_state.app_data["contestants"][c_name]["days"]
    for day in range(1, 29):
        d_str = str(day)
        core = sum(1 for i in range(1, 11) if c_days[d_str].get(f"habit_{i}", False))
        total += core
    return total

start_dt = datetime.date.fromisoformat(st.session_state.app_data["start_date"])
day_date_map = {day: start_dt + datetime.timedelta(days=day-1) for day in range(1, 29)}

if view_mode == "Daily Logger":
    col_sel1, col_sel2 = st.columns(2)
    my_profile = col_sel1.selectbox("Your Profile (Editable)", contestant_names, key="my_prof")
    other_choices = ["None"] + [n for n in contestant_names if n != my_profile]
    compare_profile = col_sel2.selectbox("Compare With (Side-by-Side)", other_choices, key="cmp_prof")
    
    c_data_profile = st.session_state.app_data["contestants"][my_profile]
    user_email = st.text_input(f"📧 Email Address for Weekly Reports ({my_profile})", value=c_data_profile.get("email", ""))
    c_data_profile["email"] = user_email
    
    selected_day = st.selectbox(
        "Select Day to Log", 
        list(range(1, 29)), 
        format_func=lambda x: f"Day {x} — {day_date_map[x].strftime('%A, %d %B %Y')}"
    )
    
    day_str = str(selected_day)
    day_state = c_data_profile["days"][day_str]
    
    daily_total = sum(1 for i in range(1, 11) if day_state.get(f"habit_{i}", False))

    if daily_total < 5:
        st.markdown(f'<p class="alert-box">⚠️ Low Score Warning: Your daily score is {daily_total} (below 5 points). Let\'s push to hit more habits tomorrow!</p>', unsafe_allow_html=True)

    if selected_day > 1:
        prev_day_str = str(selected_day - 1)
        prev_core = sum(1 for i in range(1, 11) if c_data_profile["days"][prev_day_str].get(f"habit_{i}", False))
        if daily_total < 7 and prev_core < 7:
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

    st.markdown(f'<p class="section-header">📝 Check-in for Day {selected_day} ({day_date_map[selected_day].strftime("%d %B %Y")})</p>', unsafe_allow_html=True)
    
    if compare_profile != "None":
        cmp_data_profile = st.session_state.app_data["contestants"][compare_profile]
        cmp_day_state = cmp_data_profile["days"][day_str]
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown(f"**👤 {my_profile} (You)**")
            for i in range(1, 11):
                h_key = f"habit_{i}"
                day_state[h_key] = st.checkbox(habits_info[h_key][0], value=day_state.get(h_key, False), key=f"{my_profile}_d{selected_day}_{h_key}")
        
        with col_right:
            st.markdown(f"**👥 {compare_profile} (Comparison)**")
            for i in range(1, 11):
                h_key = f"habit_{i}"
                st.checkbox(habits_info[h_key][0], value=cmp_day_state.get(h_key, False), disabled=True, key=f"cmp_{compare_profile}_d{selected_day}_{h_key}")
        
        st.markdown("---")
        col_n1, col_n2 = st.columns(2)
        with col_n1:
            daily_notes = st.text_area(f"📖 {my_profile}'s Daily Notes", value=day_state.get("notes", ""), key=f"{my_profile}_d{selected_day}_notes")
            day_state["notes"] = daily_notes
        with col_n2:
            st.markdown(f"📖 **{compare_profile}'s Daily Notes:**")
            cmp_notes = cmp_day_state.get("notes", "")
            st.info(cmp_notes if cmp_notes else "No notes recorded.")
            
        st.markdown("---")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.write(f"📸 **{my_profile}'s Photo Proof**")
            uploaded_file = st.file_uploader("Upload image snapshot", type=["jpg", "jpeg", "png"], key=f"{my_profile}_d{selected_day}_photo_upload")
            if uploaded_file is not None:
                file_path = os.path.join("uploads", f"{my_profile}_day_{selected_day}_{uploaded_file.name}")
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                day_state["photo"] = file_path
            if day_state.get("photo") and os.path.exists(day_state["photo"]):
                st.image(day_state["photo"], caption=f"Proof for Day {selected_day} ({my_profile})", width=250)
        with col_p2:
            st.write(f"📸 **{compare_profile}'s Photo Proof**")
            if cmp_day_state.get("photo") and os.path.exists(cmp_day_state["photo"]):
                st.image(cmp_day_state["photo"], caption=f"Proof for Day {selected_day} ({compare_profile})", width=250)
            else:
                st.info("No photo uploaded.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            for i in range(1, 6):
                h_key = f"habit_{i}"
                day_state[h_key] = st.checkbox(habits_info[h_key][0], value=day_state.get(h_key, False), key=f"{my_profile}_d{selected_day}_{h_key}")
        with col2:
            for i in range(6, 11):
                h_key = f"habit_{i}"
                day_state[h_key] = st.checkbox(habits_info[h_key][0], value=day_state.get(h_key, False), key=f"{my_profile}_d{selected_day}_{h_key}")

        daily_notes = st.text_area("📖 Daily Notes / Reflections / Prayer Journal", value=day_state.get("notes", ""), key=f"{my_profile}_d{selected_day}_notes")
        day_state["notes"] = daily_notes

        st.markdown("---")
        st.write("📸 **Optional Meal / Workout Photo Proof**")
        uploaded_file = st.file_uploader("Upload image snapshot", type=["jpg", "jpeg", "png"], key=f"{my_profile}_d{selected_day}_photo_upload")
        if uploaded_file is not None:
            file_path = os.path.join("uploads", f"{my_profile}_day_{selected_day}_{uploaded_file.name}")
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            day_state["photo"] = file_path

        if day_state.get("photo") and os.path.exists(day_state["photo"]):
            st.image(day_state["photo"], caption=f"Proof for Day {selected_day} ({my_profile})", width=300)

    save_data(st.session_state.app_data)

    daily_total = sum(1 for i in range(1, 11) if day_state.get(f"habit_{i}", False))
    
    st.write("---")
    st.info(f"✨ **Day {selected_day} Score for {my_profile}:** **{daily_total} / 10 Points**")

    total_cumulative = calculate_total(my_profile)
    st.write("---")
    st.markdown(f'<p class="section-header">🏆 Milestone Rewards Status ({my_profile})</p>', unsafe_allow_html=True)
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
        notes = c_days[d_str].get("notes", "")
        photo_status = "📷 Attached" if c_days[d_str].get("photo") else "—"
        grid_data.append({
            "Day": f"Day {day}",
            "Date": day_date_map[day].strftime('%d %b %Y'),
            "Score (/10)": core,
            "Photo": photo_status,
            "Notes / Journal": notes if notes else "—"
        })
    
    df_grid = pd.DataFrame(grid_data)
    st.dataframe(df_grid, use_container_width=True)

elif view_mode == "Rules & Guidelines":
    st.subheader("📜 Challenge Rules & Guidelines")
    st.markdown("Welcome to **Hybrid Theory: 28 Day Challenge**! Remember our core philosophy: **Consistency over perfection. Never miss twice!**")
    st.markdown("---")
    
    st.markdown("### 📋 Daily Habit Guidelines")
    for h_key, (title, desc) in habits_info.items():
        st.markdown(f"**{title}**")
        st.markdown(f"> {desc}")
        st.markdown("")
        
    st.markdown("---")
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
            running_total += core
            chart_data.append({
                "Day": day,
                "Contestant": name,
                "Cumulative Points": running_total
            })
            
    df_chart = pd.DataFrame(chart_data)
    
    color_domain = list(contestants_dict.keys())
    color_range = [contestants_dict[name].get("color", "#1f77b4") for name in color_domain]
    
    line_chart = alt.Chart(df_chart).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X('Day:Q', title='Day of Challenge'),
        y=alt.Y('Cumulative Points:Q', title='Cumulative Points'),
        color=alt.Color('Contestant:N', scale=alt.Scale(domain=color_domain, range=color_range), title='Contestant'),
        tooltip=['Contestant', 'Day', 'Cumulative Points']
    ).properties(
        width=700,
        height=400
    ).interactive()
    
    st.altair_chart(line_chart, use_container_width=True)

    st.markdown("---")
    st.subheader("🔥 Individual Habit Heatmaps & Completion Breakdown")
    st.markdown("Analyze how consistently each specific habit is completed across all logged days.")
    
    habit_summary = []
    for h_key, (h_title, _) in habits_info.items():
        completed_count = 0
        for name, c_info in contestants_dict.items():
            for day in range(1, 29):
                if c_info["days"][str(day)].get(h_key, False):
                    completed_count += 1
        habit_summary.append({
            "Habit": h_title.split(". ")[1],
            "Completions": completed_count
        })
        
    df_habits = pd.DataFrame(habit_summary)
    habit_chart = alt.Chart(df_habits).mark_bar(color="#5D6D7E").encode(
        x=alt.X('Completions:Q', title='Total Check-ins Across All Contestants & Days'),
        y=alt.Y('Habit:N', sort='-x', title='Habit'),
        tooltip=['Habit', 'Completions']
    ).properties(
        width=700,
        height=350
    )
    st.altair_chart(habit_chart, use_container_width=True)

else:
    st.subheader("📊 Group Leaderboard & Live Activity Feed")
    
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
    st.subheader("⚡ Live Group Activity Feed")
    
    activity_stream = []
    for name, c_info in st.session_state.app_data["contestants"].items():
        for day in range(1, 29):
            d_str = str(day)
            d_data = c_info["days"][d_str]
            core = sum(1 for i in range(1, 11) if d_data.get(f"habit_{i}", False))
            if core > 0:
                activity_stream.append({
                    "day": day,
                    "contestant": name,
                    "score": core,
                    "notes": d_data.get("notes", "")
                })
    
    activity_stream.sort(key=lambda x: x["day"], reverse=True)
    
    if activity_stream:
        for act in activity_stream[:8]:
            note_text = f' — "{act["notes"]}"' if act["notes"] else ""
            st.markdown(f'<div class="activity-card"><b>{act["contestant"]}</b> checked in for Day {act["day"]} with <b>{act["score"]} points</b>{note_text}</div>', unsafe_allow_html=True)
    else:
        st.info("No activity recorded yet. Start logging your daily habits to populate the live feed!")

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
        st.write(f"- **Areas where points were gained:** Consistent core habit completions.")
        st.write(f"- **Habit Drop-off Areas (Most missed items across recorded days):**")
        
        sorted_misses = sorted(missed_counts.items(), key=lambda x: x[1], reverse=True)
        for h_key, count in sorted_misses[:3]:
            st.write(f"  * *{habits_info[h_key][0]}* (Missed {count} times)")
            
        if rep_email:
            st.info(f"📬 In a fully hosted deployment, this formatted report would automatically be dispatched to **{rep_email}** every week!")
        else:
            st.warning("⚠️ Enter your email address in the Daily Logger view to enable automatic weekly report deliveries.")
