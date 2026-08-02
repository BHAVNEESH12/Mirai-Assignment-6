import os
import urllib.parse
from dotenv import load_dotenv
import pandas as pd
import google.generativeai as genai
import streamlit as st

load_dotenv()

st.set_page_config(page_title="Life-OS Dashboard", layout="wide")

@st.cache_data
def load_data():
    if not os.path.exists("screentime.csv"):
        return None
    df = pd.read_csv("screentime.csv")
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df

df = load_data()

if df is None:
    st.error("screentime.csv file not found in directory.")
    st.stop()

st.title("Life-OS: Digital Wellbeing Dashboard")
st.caption("Track daily screen usage, analyze habits, and get actionable coaching.")

st.sidebar.header("Controls")
available_dates = sorted(df['Date'].unique(), reverse=True)
selected_date = st.sidebar.selectbox("Select Date", available_dates)

daily_goal_hours = st.sidebar.slider("Daily Screen Time Goal (Hours)", min_value=1.0, max_value=12.0, value=6.0, step=0.5)
daily_goal_minutes = daily_goal_hours * 60

day_df = df[df['Date'] == selected_date]

total_minutes = day_df['Minutes_Used'].sum()
total_hours = round(total_minutes / 60, 2)

if not day_df.empty:
    most_used_app = day_df.groupby('App_Name')['Minutes_Used'].sum().idxmax()
else:
    most_used_app = "None"

delta_minutes = total_minutes - daily_goal_minutes
delta_hours = round(delta_minutes / 60, 2)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total Screen Time", value=f"{total_hours} hrs ({total_minutes} mins)")

with col2:
    st.metric(label="Most Used App", value=most_used_app)

with col3:
    st.metric(
        label="Goal Difference",
        value=f"{abs(delta_hours)} hrs {'Over' if delta_hours > 0 else 'Under'}",
        delta=f"{delta_hours} hrs vs Goal",
        delta_color="inverse" if delta_hours > 0 else "normal"
    )

st.divider()

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("14-Day Screen Time Trend")
    trend_df = df.groupby('Date')['Minutes_Used'].sum().reset_index()
    trend_df['Hours_Used'] = trend_df['Minutes_Used'] / 60
    st.line_chart(trend_df, x='Date', y='Hours_Used')

with col_right:
    st.subheader("Category Breakdown")
    category_df = day_df.groupby('Category')['Minutes_Used'].sum().reset_index()
    st.bar_chart(category_df, x='Category', y='Minutes_Used')

st.divider()

st.subheader("AI Life Coach Audit")

def prepare_summary(data_frame):
    cat_summary = data_frame.groupby('Category')['Minutes_Used'].sum().to_dict()
    app_summary = data_frame.groupby('App_Name')['Minutes_Used'].sum().to_dict()
    return f"Category Breakdown: {cat_summary}\nApp Breakdown: {app_summary}"

summary_str = prepare_summary(day_df)

api_keys = [
    os.getenv("GEMINI_API_KEY"),
    os.getenv("GEMINI_API_KEY_BACKUP_1"),
    os.getenv("GEMINI_API_KEY_BACKUP_2")
]

valid_keys = [k for k in api_keys if k]

if not valid_keys:
    st.error("No API keys found in environment variables.")
else:
    if st.button("Generate Advice"):
        with st.spinner("Analyzing usage patterns..."):
            
            prompt = f"""
You are a direct life coach analyzing daily screen time data.
Data for today:
{summary_str}
Total Minutes Spent: {total_minutes}
Target Goal Minutes: {daily_goal_minutes}

Provide a response formatted as follows:
1. Evaluation: Direct feedback on productivity vs wasted time today.
2. Real-World Replacements: Suggest physical, offline alternatives for excessive screen time categories.
3. Avatar Prompt: End your response with a line formatted as:
AVATAR_PROMPT: <a concise 1-sentence image description representing their mental state today>
"""
            ai_response = None
            
            for i, key in enumerate(valid_keys):
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    res = model.generate_content(prompt)
                    if res and res.text:
                        ai_response = res.text
                        break
                except Exception as e:
                    if i == len(valid_keys) - 1:
                        st.error(f"API failed across all keys: {e}")
                    else:
                        continue

            if ai_response:
                avatar_description = "a developer working at a clean desk, digital art"
                clean_response = ai_response
                
                if "AVATAR_PROMPT:" in ai_response:
                    parts = ai_response.split("AVATAR_PROMPT:")
                    clean_response = parts[0].strip()
                    avatar_description = parts[1].strip()

                if total_minutes > daily_goal_minutes:
                    st.warning("Screen time limit exceeded.")
                else:
                    st.info("Daily goal met.")

                col_text, col_img = st.columns([2, 1])

                with col_text:
                    st.markdown(clean_response)

                with col_img:
                    st.caption("Daily Persona Avatar")
                    try:
                        encoded_prompt = urllib.parse.quote(avatar_description)
                        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=400&height=400&nologo=true"
                        st.image(image_url)
                    except Exception:
                        st.write("Could not load image.")