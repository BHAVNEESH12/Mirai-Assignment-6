"""
Life-OS: The Wellbeing Dashboard
---------------------------------
A Streamlit dashboard that visualizes daily screen time data and uses
the Gemini API to act as a personalized, brutal-but-fair productivity
and lifestyle coach.

Run locally:
    streamlit run app.py
"""

import os
import json
from datetime import datetime

import pandas as pd
import streamlit as st

# google-genai is optional at import time so the app doesn't crash if the
# package isn't installed yet / no key is configured — we degrade gracefully.
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ----------------------------------------------------------------------
# Page config & style
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Life-OS | Wellbeing Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0rem;
    }
    .subtitle {
        color: #888;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    div[data-testid="stMetric"] {
        background-color: rgba(128,128,128,0.08);
        border: 1px solid rgba(128,128,128,0.2);
        padding: 15px 15px 5px 15px;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------
# Phase 1: Data Pipeline
# ----------------------------------------------------------------------
@st.cache_data
def load_data(path: str = "screentime.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    return df


df = load_data()
all_dates = sorted(df["Date"].unique())


# ----------------------------------------------------------------------
# Phase 2: Sidebar controls
# ----------------------------------------------------------------------
st.sidebar.markdown("## ⚙️ Command Center Controls")

selected_day = st.sidebar.selectbox(
    "📅 Select a day to inspect",
    options=all_dates,
    index=len(all_dates) - 1,  # default to the most recent day = "today"
    format_func=lambda d: d.strftime("%A, %b %d, %Y"),
)

daily_goal_minutes = st.sidebar.slider(
    "🎯 Daily screen time goal (minutes)",
    min_value=30,
    max_value=480,
    value=180,
    step=15,
    help="Set the maximum amount of daily screen time you're aiming for.",
)
st.sidebar.caption(f"That's about **{daily_goal_minutes / 60:.1f} hours** per day.")

st.sidebar.divider()
st.sidebar.markdown("## 🔑 Gemini API")
api_key_input = st.sidebar.text_input(
    "Gemini API Key (optional)",
    value="",
    type="password",
    placeholder="Using key from secrets" if os.environ.get("GEMINI_API_KEY") else "Paste your Gemini API key",
    help="Leave blank to use the GEMINI_API_KEY set in secrets/.env. Only fill this in to override it.",
)
)

st.sidebar.divider()
st.sidebar.caption("Life-OS · MirAI School of Technology · AI Builder Track")


# ----------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------
st.markdown('<div class="main-title">🧠 Life-OS: Wellbeing Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Your screen time, visualized — and honestly evaluated by AI.</div>',
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------
# Phase 2: KPI Row
# ----------------------------------------------------------------------
day_df = df[df["Date"] == selected_day].copy()
total_minutes_today = int(day_df["Minutes_Used"].sum())

if not day_df.empty:
    top_app_row = day_df.loc[day_df["Minutes_Used"].idxmax()]
    top_app_name = top_app_row["App_Name"]
    top_app_minutes = int(top_app_row["Minutes_Used"])
else:
    top_app_name, top_app_minutes = "—", 0

delta_vs_goal = total_minutes_today - daily_goal_minutes

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="⏱️ Total Screen Time Today",
        value=f"{total_minutes_today} min",
        help=f"{total_minutes_today / 60:.1f} hours across {day_df['App_Name'].nunique()} apps",
    )

with col2:
    st.metric(
        label="📱 Most Used App",
        value=top_app_name,
        delta=f"{top_app_minutes} min" if top_app_name != "—" else None,
        delta_color="off",
    )

with col3:
    st.metric(
        label="🎯 Vs. Daily Goal",
        value=f"{daily_goal_minutes} min goal",
        delta=f"{delta_vs_goal:+d} min",
        delta_color="inverse",  # going OVER the goal should read as "bad" (red)
    )

st.divider()


# ----------------------------------------------------------------------
# Phase 2: Visualizations
# ----------------------------------------------------------------------
viz_col1, viz_col2 = st.columns([1.4, 1])

with viz_col1:
    st.markdown("### 📈 14-Day Screen Time Trend")
    daily_totals = df.groupby("Date")["Minutes_Used"].sum().reindex(all_dates, fill_value=0)
    daily_totals_df = pd.DataFrame({"Total Minutes": daily_totals.values}, index=all_dates)
    st.line_chart(daily_totals_df)

with viz_col2:
    st.markdown(f"### 🗂️ Category Breakdown — {selected_day.strftime('%b %d')}")
    if not day_df.empty:
        category_totals = day_df.groupby("Category")["Minutes_Used"].sum().sort_values(ascending=False)
        st.bar_chart(category_totals)
    else:
        st.info("No usage recorded for this day.")

with st.expander("🔍 See raw app-level data for the selected day"):
    st.dataframe(
        day_df[["App_Name", "Category", "Minutes_Used"]].sort_values(
            "Minutes_Used", ascending=False
        ),
        use_container_width=True,
        hide_index=True,
    )

st.divider()


# ----------------------------------------------------------------------
# Phase 3: The Data Bridge — aggregate + serialize for the LLM
# ----------------------------------------------------------------------
def summarize_day_for_ai(day_df: pd.DataFrame, goal_minutes: int, day) -> str:
    """Aggregate a day's raw app-level rows into a clean, compact string
    that an LLM can reason over (never hand a raw DataFrame to the model).
    """
    if day_df.empty:
        return json.dumps({"date": str(day), "total_minutes": 0, "categories": {}, "goal_minutes": goal_minutes})

    category_summary = (
        day_df.groupby("Category")["Minutes_Used"].sum().sort_values(ascending=False).to_dict()
    )
    app_summary = (
        day_df.groupby("App_Name")["Minutes_Used"].sum().sort_values(ascending=False).to_dict()
    )

    payload = {
        "date": str(day),
        "total_minutes": int(day_df["Minutes_Used"].sum()),
        "goal_minutes": goal_minutes,
        "minutes_over_or_under_goal": int(day_df["Minutes_Used"].sum()) - goal_minutes,
        "minutes_by_category": category_summary,
        "minutes_by_app": app_summary,
    }
    return json.dumps(payload, indent=2)


data_summary_str = summarize_day_for_ai(day_df, daily_goal_minutes, selected_day)


# ----------------------------------------------------------------------
# Phase 3: The System Prompt + Gemini call
# ----------------------------------------------------------------------
def build_coach_prompt(summary_json: str) -> str:
    return f"""You are "Coach O", a holistic life coach embedded inside a personal
wellbeing dashboard called Life-OS. You are brutally honest but fundamentally
supportive — like a strength coach, not a scold. You never simply say "use
your phone less." Every time you flag a problem area, you propose a SPECIFIC,
real-world, physical replacement activity tied to the time that was spent.

Here is the user's screen time data for one day, already aggregated by
category and by app (all values in minutes):

{summary_json}

Write your analysis with this structure, in Markdown:
1. **One-line verdict** on the day (be direct, but not cruel).
2. **What stands out** — call out the single biggest time sink by category,
   and name the specific app(s) driving it.
3. **The swap** — for the worst category, suggest 1-2 concrete real-world
   replacement activities (e.g. "swap 45 min of TikTok for a walk + calling
   a friend" or "trade 30 min of Instagram for meal-prepping tomorrow's
   lunch"). Be specific about duration and activity, not vague ("go
   outside").
4. **One thing they did right** today, if anything in the data supports it
   (e.g. meaningful coding/education time).
5. **Tomorrow's micro-goal** — one small, concrete, achievable target for
   the next 24 hours.

Keep the whole response under 180 words. Do not use exclamation points more
than once. Do not be preachy — be a coach, not a lecture.
"""


def call_gemini(prompt: str, api_key: str) -> str:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text


st.markdown("### 🤖 Coach O's Verdict")

effective_key = api_key_input or os.environ.get("GEMINI_API_KEY", "")

analyze_clicked = st.button("🧠 Analyze My Day", type="primary")

if analyze_clicked:
    if not GENAI_AVAILABLE:
        st.error(
            "The `google-genai` package isn't installed. Run "
            "`pip install -r requirements.txt` and try again."
        )
    elif not effective_key:
        st.warning(
            "No Gemini API key found. Paste one in the sidebar, or set a "
            "`GEMINI_API_KEY` environment variable / `.env` file, then click "
            "the button again."
        )
    else:
        with st.spinner("Coach O is reviewing your day..."):
            try:
                prompt = build_coach_prompt(data_summary_str)
                verdict = call_gemini(prompt, effective_key)

                # Choose the render style based on how bad the day was
                if delta_vs_goal > 90:
                    st.error(verdict)
                elif delta_vs_goal > 0:
                    st.warning(verdict)
                else:
                    st.info(verdict)

            except Exception as e:
                st.error(f"Gemini API call failed: {e}")
else:
    st.caption("Click **Analyze My Day** to get Coach O's personalized breakdown for the selected day.")

with st.expander("🛠️ See the exact data payload sent to the AI"):
    st.code(data_summary_str, language="json")

st.divider()


# ----------------------------------------------------------------------
# Phase 4: Innovation Deliverable — The "Shareable" Accountability Link
# ----------------------------------------------------------------------
st.markdown("### 🔗 Accountability Link")
st.caption(
    "Generate a link that encodes today's total screen time so an "
    "accountability partner can check your stats instantly — no login needed."
)

share_col1, share_col2 = st.columns([1, 2])

with share_col1:
    if st.button("📤 Generate Shareable Link"):
        st.query_params["date"] = str(selected_day)
        st.query_params["total_minutes"] = str(total_minutes_today)
        st.query_params["goal_minutes"] = str(daily_goal_minutes)
        st.query_params["status"] = "over" if delta_vs_goal > 0 else "under"

with share_col2:
    if "date" in st.query_params:
        base_url = st.context.headers.get("origin") if hasattr(st, "context") else None
        query_string = "&".join(f"{k}={v}" for k, v in st.query_params.to_dict().items())
        display_url = f"{base_url or '<your-deployed-app-url>'}/?{query_string}"
        st.code(display_url, language="text")
        st.caption("Copy this URL and send it to your accountability partner.")

# If someone opens the app via a shared accountability link, greet them
if "total_minutes" in st.query_params and "date" in st.query_params:
    shared_date = st.query_params["date"]
    shared_minutes = st.query_params["total_minutes"]
    shared_goal = st.query_params.get("goal_minutes", "—")
    shared_status = st.query_params.get("status", "—")
    icon = "🔴" if shared_status == "over" else "🟢"
    st.info(
        f"{icon} **Accountability check:** on **{shared_date}**, this user logged "
        f"**{shared_minutes} minutes** of screen time against a goal of "
        f"**{shared_goal} minutes** ({shared_status} goal)."
    )

st.divider()
st.caption("Built for the MirAI School of Technology · AI Builder Track · Life-OS Capstone")
