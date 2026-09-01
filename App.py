import streamlit as st
import pandas as pd
import sqlite3
import json
import os
import datetime
import altair as alt

# Page Configuration
st.set_page_config(page_title="HYBRID THEORY - 28 Day Challenge", page_icon="🔥", layout="centered")

# Ensure uploads directory exists for photo proof
os.makedirs("uploads", exist_ok=True)

# Custom Styling for Compact Layout, Fiery Header, and Checkbox Accent Color
st.markdown("""
    <style>
    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 2rem;
    }
    p {
        margin-bottom: 0.5rem !important;
    }
    input[type="checkbox"]:checked {
        accent-color: #D35400 !important;
    }
    .header-container {
        background: linear-gradient(135deg, #C0392B, #D35400, #F39C12);
        padding: 15px 10px;
        border-radius: 8px;
        text-align: center !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: 15px;
        box-shadow: 0 3px 8px rgba(0,0,0,0.15);
    }
    .main-title-custom {
        font-family: 'Impact', 'Arial Black', sans-serif;
        font-size: 46px;
        font-weight: 900;
        color: #FFFFFF !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.0;
        letter-spacing: 2px;
        text-align: center !important;
        width: 100%;
    }
    .sub-title-custom {
        font-size: 22px;
        font-weight: 600;
        color: #FAD7A0 !important;
        margin: 4px 0 0 0 !important;
        padding: 0 !important;
        line-height: 1.2;
        text-align: center !important;
        width: 100%;
    }
    .tagline-custom {
        font-size: 12px;
        color: #FEF9E7 !important;
        margin: 4px 0 0 0 !important;
        padding: 0 !important;
        letter-spacing: 0.5px;
        text-align: center !important;
        width: 100%;
    }
    </style>
    <div class="header-container">
        <h1 class="main-title-custom">HYBRID THEORY</h1>
        <h2 class="sub-title-custom">28 Day Challenge</h2>
        <p class="tagline-custom">Consistency over perfection. Never miss twice!</p>
    </div>
""", unsafe_allow_html=True)

# --- DATABASE SETUP (Cloud-Compatible SQLite / Swappable to Supabase) ---
DB_FILE = "hybrid_theory_cloud.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS challenge_state (key TEXT PRIMARY KEY, value TEXT)''')
    conn.commit()
    
    # Check if data exists, otherwise insert default structure
    c.execute("SELECT value FROM challenge_state WHERE key = 'app_data'")
    row = c.fetchone()
    if not row:
        default_structure = {
            "start_date": "2026-09-01",
            "gladiators": {
                "Gladiator 1": {
                    "email": "", 
                    "color": "#1B4F72", 
                    "vetoed_habit": None,
                    "custom_replacement": {"title": "", "guideline": ""},
                    "days": {str(day): {f"habit_{i}": False for i in range(1, 11)} | {f"bonus_{i}": False for i in range(1, 6)} | {"notes": "", "photo": ""} for day in range(1, 29)}
                },
                "Gladiator 2": {
                    "email": "", 
                    "color": "#117A65", 
                    "vetoed_habit": None,
                    "custom_replacement": {"title": "", "guideline": ""},
                    "days": {str(day): {f"habit_{i}": False for i in range(1, 11)} | {f"bonus_{i}": False for i in range(1, 6)} | {"notes": "", "photo": ""} for day in range(1, 29)}
                }
            }
        }
        c.execute("INSERT INTO challenge_state (key, value) VALUES ('app_data', ?)", (json.dumps(default_structure),))
        conn.commit()
    conn.close()

def load_data():
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT value FROM challenge_state WHERE key = 'app_data'")
    row = c.fetchone()
    conn.close()
    if row:
        try:
            data = json.loads(row[0])
            if "gladiators" in data:
                default_colors = ["#1B4F72", "#117A65", "#B7950B", "#7D3C98", "#2E4053", "#1B3136", "#884EA0", "#1E8449", "#2471A3", "#A04000"]
                for idx, (name, g_info) in enumerate(data["gladiators"].items()):
                    if "color" not in g_info:
                        g_info["color"] = default_colors[idx % len(default_colors)]
                    if "vetoed_habit" not in g_info:
                        g_info["vetoed_habit"] = None
                    if "custom_replacement" not in g_info:
                        g_info["custom_replacement"] = {"title": "", "guideline": ""}
            return data
        except Exception:
            pass
    return {}

def save_data(data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("REPLACE INTO challenge_state (key, value) VALUES ('app_data', ?)", (json.dumps(data),))
    conn.commit()
    conn.close()

if "app_data" not in st.session_state:
    st.session_state.app_data = load_data()

# Habit definitions
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

bonus_info = {
    "bonus_1": ("🔥 Bonus: Extra Steps (>10k steps)", "🚶‍♀️ Walked more than 10,000 steps today."),
    "bonus_2": ("🔥 Bonus: Extended Training (30–60 mins)", "💪 Exercised between 30 minutes and 1 hour today."),
    "bonus_3": ("🔥 Bonus: High Hydration (>8 glasses)", "💧 Drank more than 8 glasses of water today."),
    "bonus_4": ("🔥 Bonus: Extended Unplug (>30 mins)", "📵 Had more than 30 minutes of intentional non-screen time."),
    "bonus_5": ("🔥 Saturday Parkrun Bonus (+5 pts)", "🏃‍♂️ Completed your Saturday 5km Parkrun event.")
}

# --- SIDEBAR: ROLE PROTECTION & MANAGEMENT ---
st.sidebar.subheader("🔒 Access & Security")
is_admin = st.sidebar.checkbox("Developer / Admin Mode", value=False)

if is_admin:
    admin_pin = st.sidebar.text_input("Enter Admin PIN", type="password")
    if admin_pin != "HYBRID2026":
        st.sidebar.error("Incorrect PIN! Administrative controls locked.")
        is_admin = False
    else:
        st.sidebar.success("Admin Mode Unlocked!")

st.sidebar.markdown("---")
st.sidebar.subheader("📅 Challenge Calendar Sync")
current_start_str = st.session_state.app_data.get("start_date", "2026-09-01")
try:
    parsed_start_date = datetime.date.fromisoformat(current_start_str)
except ValueError:
    parsed_start_date = datetime.date(2026, 9, 1)

if is_admin:
    selected_start_date = st.sidebar.date_input("Challenge Start Date", value=parsed_start_date)
    st.session_state.app_data["start_date"] = selected_start_date.isoformat()
    save_data(st.session_state.app_data)
else:
    st.sidebar.markdown(f"**Challenge Start Date:** {parsed_start_date.strftime('%d %B %Y')}")

st.sidebar.markdown("---")
st.sidebar.subheader("⚔️ Gladiators Management")

gladiator_names = list(st.session_state.app_data["gladiators"].keys())

if is_admin:
    # Add New Gladiator
    if len(gladiator_names) < 10:
        new_name = st.sidebar.text_input("Add New Gladiator Name")
        if st.sidebar.button("Add Gladiator") and new_name:
            if new_name in gladiator_names:
                st.sidebar.error("Gladiator name already exists!")
            else:
                default_colors = ["#1B4F72", "#117A65", "#B7950B", "#7D3C98", "#2E4053", "#1B3136", "#884EA0", "#1E8449", "#2471A3", "#A04000"]
                assigned_color = default_colors[len(gladiator_names) % len(default_colors)]
                st.session_state.app_data["gladiators"][new_name] = {
                    "email": "",
                    "color": assigned_color,
                    "vetoed_habit": None,
                    "custom_replacement": {"title": "", "guideline": ""},
                    "days": {str(day): {f"habit_{i}": False for i in range(1, 11)} | {f"bonus_{i}": False for i in range(1, 6)} | {"notes": "", "photo": ""} for day in range(1, 29)}
                }
                save_data(st.session_state.app_data)
                st.rerun()

    # Edit Existing Gladiator Name
    if len(gladiator_names) > 0:
        with st.sidebar.expander("✏️ Rename Gladiator"):
            target_to_rename = st.selectbox("Select Gladiator to Rename", gladiator_names, key="rename_select")
            new_entered_name = st.text_input("New Name", value=target_to_rename, key="rename_input")
            if st.button("Save New Name"):
                if not new_entered_name.strip():
                    st.sidebar.error("Name cannot be empty!")
                elif new_entered_name in gladiator_names and new_entered_name != target_to_rename:
                    st.sidebar.error("That name already exists!")
                else:
                    updated_gladiators = {}
                    for name, info in st.session_state.app_data["gladiators"].items():
                        if name == target_to_rename:
                            updated_gladiators[new_entered_name] = info
                        else:
                            updated_gladiators[name] = info
                    st.session_state.app_data["gladiators"] = updated_gladiators
                    save_data(st.session_state.app_data)
                    st.success(f"Renamed {target_to_rename} to {new_entered_name}!")
                    st.rerun()

    # Habit Veto & Custom Replacement
    if len(gladiator_names) > 0:
        with st.sidebar.expander("🚫 Veto Habit & Replace (1 per Gladiator)"):
            target_v_gladiator = st.selectbox("Select Gladiator", gladiator_names, key="v_gladiator_select")
            v_g_info = st.session_state.app_data["gladiators"][target_v_gladiator]
            
            current_vetoed = v_g_info.get("vetoed_habit", None)
            habit_options_labels = {k: v[0] for k, v in habits_info.items()}
            habit_keys_list = list(habits_info.keys())
            
            veto_choice = st.selectbox("Select Core Habit to Veto (or None)", ["None"] + habit_keys_list, format_func=lambda x: "No Veto (Keep Standard 10)" if x == "None" else habit_options_labels[x], key="veto_dropdown")
            
            existing_rep = v_g_info.get("custom_replacement", {"title": "", "guideline": ""})
            
            if veto_choice != "None":
                rep_title_input = st.text_input("Replacement Habit Name", value=existing_rep.get("title", ""))
                rep_guide_input = st.text_area("Replacement Rule / Guideline", value=existing_rep.get("guideline", ""))
                
                if st.button("Save Veto & Replacement"):
                    v_g_info["vetoed_habit"] = veto_choice
                    v_g_info["custom_replacement"] = {
                        "title": rep_title_input.strip(),
                        "guideline": rep_guide_input.strip()
                    }
                    save_data(st.session_state.app_data)
                    st.success(f"Habit veto updated for {target_v_gladiator}!")
                    st.rerun()
            else:
                if st.button("Clear Veto & Reset to Standard 10"):
                    v_g_info["vetoed_habit"] = None
                    v_g_info["custom_replacement"] = {"title": "", "guideline": ""}
                    save_data(st.session_state.app_data)
                    st.success(f"Veto cleared for {target_v_gladiator}!")
                    st.rerun()

    # Remove Gladiator
    if len(gladiator_names) > 1:
        with st.sidebar.expander("🗑️ Remove Gladiator"):
            target_to_remove = st.selectbox("Select to Remove", ["None"] + gladiator_names, key="remove_select")
            if target_to_remove != "None" and st.button("Remove Gladiator"):
                del st.session_state.app_data["gladiators"][target_to_remove]
                save_data(st.session_state.app_data)
                st.rerun()

gladiator_names = list(st.session_state.app_data["gladiators"].keys())

if is_admin:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎨 Gladiator Line Colors")
    for name in gladiator_names:
        g_info = st.session_state.app_data["gladiators"][name]
        current_color = g_info.get("color", "#1B4F72")
        new_color = st.sidebar.color_picker(f"{name} Color", value=current_color, key=f"color_{name}")
        g_info["color"] = new_color
    save_data(st.session_state.app_data)

st.sidebar.markdown("---")
view_mode = st.sidebar.radio("Navigation", ["Daily Logger", "28-Day Overview Grid", "Rules & Guidelines", "Analytics & Graphs", "Leaderboard & Activity Feed"])

def calculate_total(g_name):
    total = 0
    g_days = st.session_state.app_data["gladiators"][g_name]["days"]
    for day in range(1, 29):
        d_str = str(day)
        core = sum(1 for i in range(1, 11) if g_days[d_str].get(f"habit_{i}", False))
        bonus_daily = sum(1 for i in range(1, 5) if g_days[d_str].get(f"bonus_{i}", False))
        bonus_weekly = 5 if g_days[d_str].get("bonus_5", False) else 0
        total += (core + bonus_daily + bonus_weekly)
    return total

start_dt = datetime.date.fromisoformat(st.session_state.app_data["start_date"])
day_date_map = {day: start_dt + datetime.timedelta(days=day-1) for day in range(1, 29)}

if view_mode == "Daily Logger":
    col_sel1, col_sel2 = st.columns(2)
    my_profile = col_sel1.selectbox("Your Profile", gladiator_names, key="my_prof")
    other_choices = ["None"] + [n for n in gladiator_names if n != my_profile]
    compare_profile = col_sel2.selectbox("Compare With (Side-by-Side)", other_choices, key="cmp_prof")
    
    # --- RANKING RIBBON / MEDAL DISPLAY ---
    all_totals = {name: calculate_total(name) for name in gladiator_names}
    sorted_rankings = sorted(all_totals.items(), key=lambda x: x[1], reverse=True)
    
    user_rank = 1
    for idx, (g_name, _) in enumerate(sorted_rankings):
        if g_name == my_profile:
            user_rank = idx + 1
            break
            
    my_score = all_totals[my_profile]
    
    if user_rank == 1:
        st.success(f"🏆 **1st Place Ribbon!** You are leading the pack with **{my_score} points**! Keep up the incredible consistency!")
    elif user_rank == 2:
        st.info(f"🥈 **2nd Place Medal!** You're sitting strong at **{my_score} points**—just a stone's throw away from the top spot!")
    elif user_rank == 3:
        st.warning(f"🥉 **3rd Place Medal!** You have **{my_score} points**. Push hard to climb the ranks!")
    else:
        st.markdown(f"🏅 **Rank #{user_rank}** — You have **{my_score} points**. Keep checking off those daily habits to close the gap!")
    
    g_data_profile = st.session_state.app_data["gladiators"][my_profile]
    user_email = st.text_input(f"📧 Email Address for Weekly Reports ({my_profile})", value=g_data_profile.get("email", ""))
    g_data_profile["email"] = user_email
    save_data(st.session_state.app_data)
    
    selected_day = st.selectbox(
        "Select Day to Log", 
        list(range(1, 29)), 
        format_func=lambda x: f"Day {x} — {day_date_map[x].strftime('%A, %d %B %Y')}"
    )
    
    day_str = str(selected_day)
    day_state = g_data_profile["days"][day_str]
    current_day_date = day_date_map[selected_day]
    is_saturday = (current_day_date.weekday() == 5)
    
    if not is_saturday and day_state.get("bonus_5", False):
        day_state["bonus_5"] = False

    core_total = sum(1 for i in range(1, 11) if day_state.get(f"habit_{i}", False))
    bonus_daily_total = sum(1 for i in range(1, 5) if day_state.get(f"bonus_{i}", False))
    bonus_weekly_total = 5 if day_state.get("bonus_5", False) else 0
    daily_total = core_total + bonus_daily_total + bonus_weekly_total

    if core_total < 5:
        st.warning(f"⚠️ Low Score Warning: Your core score is {core_total} (below 5 points). Let's push to hit more habits tomorrow!")

    if selected_day > 1:
        prev_day_str = str(selected_day - 1)
        prev_core = sum(1 for i in range(1, 11) if g_data_profile["days"][prev_day_str].get(f"habit_{i}", False))
        if core_total < 7 and prev_core < 7:
            st.error('🚨 "Never Miss Twice" Alert: Your core score has dropped below 7 for two consecutive days. Time for a quick bounce-back!')

    st.subheader(f"📝 Check-in for Day {selected_day} ({current_day_date.strftime('%A, %d %B %Y')})")
    
    my_veto = g_data_profile.get("vetoed_habit", None)
    my_rep = g_data_profile.get("custom_replacement", {"title": "", "guideline": ""})

    if compare_profile != "None":
        cmp_data_profile = st.session_state.app_data["gladiators"][compare_profile]
        cmp_day_state = cmp_data_profile["days"][day_str]
        cmp_veto = cmp_data_profile.get("vetoed_habit", None)
        cmp_rep = cmp_data_profile.get("custom_replacement", {"title": "", "guideline": ""})
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown(f"**👤 {my_profile} (You)**")
            st.markdown("##### Core Habits (10 Total)")
            for i in range(1, 11):
                h_key = f"habit_{i}"
                label = f"{i}. {my_rep['title']}" if h_key == my_veto and my_rep.get("title") else habits_info[h_key][0]
                day_state[h_key] = st.checkbox(label, value=day_state.get(h_key, False), key=f"{my_profile}_d{selected_day}_{h_key}")
            
            st.markdown("##### 🔥 Daily Bonus Points")
            for i in range(1, 5):
                b_key = f"bonus_{i}"
                day_state[b_key] = st.checkbox(bonus_info[b_key][0], value=day_state.get(b_key, False), key=f"{my_profile}_d{selected_day}_{b_key}")
            
            st.markdown("##### 🏃‍♂️ Saturday Parkrun Bonus")
            if is_saturday:
                day_state["bonus_5"] = st.checkbox(bonus_info["bonus_5"][0], value=day_state.get("bonus_5", False), key=f"{my_profile}_d{selected_day}_bonus_5")
            else:
                st.info("🔒 Parkrun bonus is only available on Saturdays.")
                day_state["bonus_5"] = False
        
        with col_right:
            st.markdown(f"**👥 {compare_profile} (Comparison)**")
            st.markdown("##### Core Habits (10 Total)")
            for i in range(1, 11):
                h_key = f"habit_{i}"
                label = f"{i}. {cmp_rep['title']}" if h_key == cmp_veto and cmp_rep.get("title") else habits_info[h_key][0]
                st.checkbox(label, value=cmp_day_state.get(h_key, False), disabled=True, key=f"cmp_{compare_profile}_d{selected_day}_{h_key}")
            
            st.markdown("##### 🔥 Daily Bonus Points")
            for i in range(1, 5):
                b_key = f"bonus_{i}"
                st.checkbox(bonus_info[b_key][0], value=cmp_day_state.get(b_key, False), disabled=True, key=f"cmp_{compare_profile}_d{selected_day}_{b_key}")
            
            st.markdown("##### 🏃‍♂️ Saturday Parkrun Bonus")
            st.checkbox(bonus_info["bonus_5"][0], value=cmp_day_state.get("bonus_5", False), disabled=True, key=f"cmp_{compare_profile}_d{selected_day}_bonus_5")
        
        st.markdown("---")
        col_n1, col_n2 = st.columns(2)
        with col_n1:
            daily_notes = st.text_area(f"📖 {my_profile}'s Daily Notes", value=day_state.get("notes", ""), key=f"{my_profile}_d{selected_day}_notes")
            day_state["notes"] = daily_notes
        with col_n2:
            st.markdown(f"📖 **{compare_profile}'s Daily Notes:**")
            cmp_notes = cmp_day_state.get("notes", "")
            st.info(cmp_notes if cmp_notes else "No notes recorded.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            for i in range(1, 6):
                h_key = f"habit_{i}"
                label = f"{i}. {my_rep['title']}" if h_key == my_veto and my_rep.get("title") else habits_info[h_key][0]
                day_state[h_key] = st.checkbox(label, value=day_state.get(h_key, False), key=f"{my_profile}_d{selected_day}_{h_key}")
        with col2:
            for i in range(6, 11):
                h_key = f"habit_{i}"
                label = f"{i}. {my_rep['title']}" if h_key == my_veto and my_rep.get("title") else habits_info[h_key][0]
                day_state[h_key] = st.checkbox(label, value=day_state.get(h_key, False), key=f"{my_profile}_d{selected_day}_{h_key}")

        st.markdown("##### 🔥 Daily Bonus Points (+1 each)")
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            for i in range(1, 3):
                b_key = f"bonus_{i}"
                day_state[b_key] = st.checkbox(bonus_info[b_key][0], value=day_state.get(b_key, False), key=f"{my_profile}_d{selected_day}_{b_key}")
        with b_col2:
            for i in range(3, 5):
                b_key = f"bonus_{i}"
                day_state[b_key] = st.checkbox(bonus_info[b_key][0], value=day_state.get(b_key, False), key=f"{my_profile}_d{selected_day}_{b_key}")

        st.markdown("##### 🏃‍♂️ Saturday Parkrun Bonus (+5 pts)")
        if is_saturday:
            day_state["bonus_5"] = st.checkbox(bonus_info["bonus_5"][0], value=day_state.get("bonus_5", False), key=f"{my_profile}_d{selected_day}_bonus_5")
        else:
            st.info("🔒 Parkrun bonus is only available on Saturdays.")
            day_state["bonus_5"] = False

        daily_notes = st.text_area("📖 Daily Notes / Reflections / Prayer Journal", value=day_state.get("notes", ""), key=f"{my_profile}_d{selected_day}_notes")
        day_state["notes"] = daily_notes

    save_data(st.session_state.app_data)

    core_total = sum(1 for i in range(1, 11) if day_state.get(f"habit_{i}", False))
    bonus_daily_total = sum(1 for i in range(1, 5) if day_state.get(f"bonus_{i}", False))
    bonus_weekly_total = 5 if day_state.get("bonus_5", False) else 0
    daily_total = core_total + bonus_daily_total + bonus_weekly_total
    
    st.write("---")
    st.info(f"✨ **Day {selected_day} Score for {my_profile}:** **{daily_total} Points**")

elif view_mode == "28-Day Overview Grid":
    st.subheader("📊 28-Day Summary Grid")
    current_profile = st.selectbox("Select Profile for Grid", gladiator_names)
    
    grid_data = []
    g_days = st.session_state.app_data["gladiators"][current_profile]["days"]
    for day in range(1, 29):
        d_str = str(day)
        core = sum(1 for i in range(1, 11) if g_days[d_str].get(f"habit_{i}", False))
        bonus_daily = sum(1 for i in range(1, 5) if g_days[d_str].get(f"bonus_{i}", False))
        bonus_weekly = 5 if g_days[d_str].get("bonus_5", False) else 0
        notes = g_days[d_str].get("notes", "")
        grid_data.append({
            "Day": f"Day {day}",
            "Date": day_date_map[day].strftime('%d %b %Y'),
            "Score": core + bonus_daily + bonus_weekly,
            "Notes / Journal": notes if notes else "—"
        })
    
    df_grid = pd.DataFrame(grid_data)
    st.dataframe(df_grid, use_container_width=True)

elif view_mode == "Rules & Guidelines":
    st.subheader("📜 Challenge Rules & Guidelines")
    st.markdown("Welcome to **HYBRID THEORY: 28 Day Challenge**! Remember our core philosophy: **Consistency over perfection. Never miss twice!**")
    st.markdown("---")
    
    st.markdown("### 📋 Core Habit Guidelines (10 Total)")
    for h_key, (title, desc) in habits_info.items():
        st.markdown(f"**{title}**")
        st.markdown(f"> {desc}")
        st.markdown("")

elif view_mode == "Analytics & Graphs":
    st.subheader("📈 Gladiators Cumulative Progress Line Graph")
    chart_data = []
    gladiators_dict = st.session_state.app_data["gladiators"]
    
    for name, g_info in gladiators_dict.items():
        running_total = 0
        g_days = g_info["days"]
        for day in range(1, 29):
            d_str = str(day)
            core = sum(1 for i in range(1, 11) if g_days[d_str].get(f"habit_{i}", False))
            bonus_daily = sum(1 for i in range(1, 5) if g_days[d_str].get(f"bonus_{i}", False))
            bonus_weekly = 5 if g_days[d_str].get("bonus_5", False) else 0
            running_total += (core + bonus_daily + bonus_weekly)
            chart_data.append({"Day": day, "Gladiator": name, "Cumulative Points": running_total})
            
    df_chart = pd.DataFrame(chart_data)
    color_domain = list(gladiators_dict.keys())
    color_range = [gladiators_dict[name].get("color", "#1B4F72") for name in color_domain]
    
    line_chart = alt.Chart(df_chart).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X('Day:Q', title='Day of Challenge'),
        y=alt.Y('Cumulative Points:Q', title='Cumulative Points'),
        color=alt.Color('Gladiator:N', scale=alt.Scale(domain=color_domain, range=color_range), title='Gladiator'),
        tooltip=['Gladiator', 'Day', 'Cumulative Points']
    ).properties(width=700, height=400).interactive()
    
    st.altair_chart(line_chart, use_container_width=True)

else:
    st.subheader("📊 Group Leaderboard & Weekly Report Simulator")
    
    gladiator_totals = {name: calculate_total(name) for name in gladiator_names}
    combined_total = sum(gladiator_totals.values())
    
    cols = st.columns(len(gladiator_names) if len(gladiator_names) <= 3 else 3)
    for idx, (name, pts) in enumerate(gladiator_totals.items()):
        col_idx = idx % 3
        cols[col_idx].metric(name, f"{pts} pts")
    
    st.metric("Combined Group Total", f"{combined_total} pts")
    
    st.write("---")
    st.subheader("📧 Weekly Habit Performance Report Simulator")
    report_profile = st.selectbox("Select Profile for Report", gladiator_names, key="rep_profile")
    rep_data = st.session_state.app_data["gladiators"][report_profile]
    rep_email = rep_data.get("email", "")
    rep_veto = rep_data.get("vetoed_habit", None)
    rep_rep = rep_data.get("custom_replacement", {"title": ""})
    
    if st.button("📥 Generate Weekly Report Summary"):
        st.success(f"Report compiled successfully for **{report_profile}**!")
        
        # Primary Report
        total_gained = calculate_total(report_profile)
        missed_counts = {f"habit_{i}": 0 for i in range(1, 11)}
        for day in range(1, 29):
            d_str = str(day)
            for i in range(1, 11):
                h_key = f"habit_{i}"
                if not rep_data["days"][d_str].get(h_key, False):
                    missed_counts[h_key] += 1
                    
        st.write(f"### 📋 Performance Breakdown for {report_profile}")
        st.write(f"**Total Accumulated Points:** {total_gained}")
        st.write(f"**Challenge Start Date Synced:** {start_dt.strftime('%d %B %Y')}")
        st.write(f"**Areas where points were gained:** Consistent core habits, daily bonuses, and Saturday Parkruns.")
        st.write(f"**Habit Drop-off Areas:**")
        
        sorted_misses = sorted(missed_counts.items(), key=lambda x: x[1], reverse=True)
        for idx, (h_key, count) in enumerate(sorted_misses[:3], 1):
            h_label = rep_rep['title'] if h_key == rep_veto and rep_rep.get("title") else habits_info[h_key][0].split(". ")[1]
            st.write(f"{idx}. {h_label} (Missed {count} times)")

        # Other Gladiators Comparison Reports
        other_gladiators = [n for n in gladiator_names if n != report_profile]
        if other_gladiators:
            st.markdown("---")
            st.write(f"### ⚔️ Comparison Stats for Other Gladiators")
            for o_name in other_gladiators:
                o_data = st.session_state.app_data["gladiators"][o_name]
                o_total = calculate_total(o_name)
                o_veto = o_data.get("vetoed_habit", None)
                o_rep = o_data.get("custom_replacement", {"title": ""})
                
                o_missed_counts = {f"habit_{i}": 0 for i in range(1, 11)}
                for day in range(1, 29):
                    d_str = str(day)
                    for i in range(1, 11):
                        h_key = f"habit_{i}"
                        if not o_data["days"][d_str].get(h_key, False):
                            o_missed_counts[h_key] += 1
                
                st.write(f"#### 📋 Performance Breakdown for {o_name}")
                st.write(f"**Total Accumulated Points:** {o_total}")
                st.write(f"**Challenge Start Date Synced:** {start_dt.strftime('%d %B %Y')}")
                st.write(f"**Areas where points were gained:** Consistent core habits, daily bonuses, and Saturday Parkruns.")
                st.write(f"**Habit Drop-off Areas:**")
                
                o_sorted_misses = sorted(o_missed_counts.items(), key=lambda x: x[1], reverse=True)
                for idx, (h_key, count) in enumerate(o_sorted_misses[:3], 1):
                    h_label = o_rep['title'] if h_key == o_veto and o_rep.get("title") else habits_info[h_key][0].split(". ")[1]
                    st.write(f"{idx}. {h_label} (Missed {count} times)")
                st.markdown("")
