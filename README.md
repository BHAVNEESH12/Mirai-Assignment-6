# 🧠 Life-OS — Wellbeing Dashboard

```
> a synthetic-data-powered, AI-coached, screen-time reality check

$ status
> [ONLINE] streamlit dashboard ready
> [ONLINE] gemini-2.5-flash coach connected
> [WARNING] your TikTok usage has been flagged
```

A capstone project for the **MirAI School of Technology — AI Builder Track**.
Life-OS turns 14 days of (synthetic) screen time data into a real SaaS-style
dashboard, then hands that data to Gemini and asks it to coach you — bluntly,
but constructively — on what to do instead of scrolling.

<<<<<<< HEAD
---
=======
1. Clone the repository and navigate into the project folder:
   git clone https://github.com/BHAVNEESH12/Mirai-Assignment-6
   cd Mirai-Assignment-6
>>>>>>> 94c6486eba37661a9255760659e769bb76a75f4f

## ▸ Features

```
$ ls features/
data_pipeline.csv        # 14+ days of synthetic screen time, 4 categories
command_center_ui/       # sidebar filters + goal slider + KPI row
visualizations/          # 14-day trend line + per-day category bar chart
ai_coach/                # Gemini-powered "brutal but fair" life coach
accountability_link/     # shareable URL via st.query_params (Phase 4 pick)
```

- **📊 Data Pipeline** — `screentime.csv` with `Date, App_Name, Category, Minutes_Used` across 14 days and 14 apps (Social Media, Entertainment, Education, Coding).
- **🎛️ Command Center UI** — sidebar `st.selectbox` to pick a day, `st.slider` to set your daily goal, all laid out in `st.columns`.
- **📈 KPI Row** — total screen time, most-used app, and a delta vs. your goal (colored `inverse` so going *over* budget reads red).
- **📉 Visualizations** — 14-day trend line chart + a per-day category breakdown bar chart.
- **🤖 AI Coach ("Coach O")** — aggregates your day into clean JSON (never dumps a raw DataFrame at the model), sends it to Gemini with a strict prompt, and renders the verdict in `st.info` / `st.warning` / `st.error` depending on how far over goal you were.
- **🔗 Accountability Link** *(Phase 4 pick: Shareable Link)* — one click writes your day's stats into the URL via `st.query_params` so a friend can open the link and instantly see how you did.

---

## ▸ Quickstart

```
$ git clone <your-repo-url>
$ cd lifeos-dashboard
$ python -m venv venv
$ source venv/bin/activate      # Windows: venv\Scripts\activate
$ pip install -r requirements.txt
```

### Set your Gemini API key

Get a free key at **https://aistudio.google.com/apikey**, then either:

**Option A — .env file (local dev)**
```
$ cp .env.example .env
$ nano .env      # paste GEMINI_API_KEY=xxxxx
```

**Option B — paste it directly in the sidebar** when the app is running (it's a password-masked input, never stored).

### Run it

```
$ streamlit run app.py
```

Open **http://localhost:8501** and you're live.

---

## ▸ How the AI integration actually works

```
$ cat ai_flow.txt
```

1. **The Data Bridge** (`summarize_day_for_ai()`) — groups the selected day's rows by `Category` and by `App_Name`, sums `Minutes_Used`, and serializes it to compact JSON. The model never sees a raw pandas DataFrame.
2. **The System Prompt** (`build_coach_prompt()`) — an f-string that injects that JSON and instructs Gemini to act as "Coach O": a holistic life coach who must name a specific real-world replacement activity (a walk, meal-prepping, calling a friend) instead of just saying "use your phone less."
3. **The Call** — `google-genai`'s `client.models.generate_content(model="gemini-2.5-flash", ...)`.
4. **The Render** — the verdict is dropped into `st.info` (under goal), `st.warning` (over goal), or `st.error` (way over goal — 90+ min past your target).

---

## ▸ Deploying (Streamlit Community Cloud)

```
$ git push origin main
```

1. Go to **https://share.streamlit.io** → **New app**.
2. Point it at your GitHub repo, branch `main`, file path `app.py`.
3. In **Settings → Secrets**, paste:
   ```toml
   GEMINI_API_KEY = "your_real_key_here"
   ```
4. Deploy. Your live URL is what you submit to the portal.

*(Render or Hugging Face Spaces work too — just set `GEMINI_API_KEY` as an environment variable / secret there and point the start command at `streamlit run app.py`.)*

---

## ▸ Project structure

```
$ tree
lifeos-dashboard/
├── app.py                          # main Streamlit app (all 4 phases)
├── generate_data.py                # regenerates screentime.csv (optional)
├── screentime.csv                  # 14-day synthetic dataset
├── requirements.txt
├── .env.example                    # template — copy to .env, never commit .env
├── .gitignore                      # keeps .env and secrets.toml out of git
├── .streamlit/
│   ├── config.toml                 # dark SaaS theme
│   └── secrets.toml.example        # template for Streamlit Cloud secrets
└── README.md
```

<<<<<<< HEAD
=======
4. Run the Streamlit app:
   streamlit run app.py
>>>>>>> 94c6486eba37661a9255760659e769bb76a75f4f
