"""
generate_data.py
-----------------
One-off helper script used to build screentime.csv.
Not required to run the app (screentime.csv is already generated and
committed), but kept in the repo so the dataset is reproducible /
easy to regenerate with different numbers.

Run with: python generate_data.py
"""

import csv
import random
from datetime import date, timedelta

random.seed(42)

APPS = {
    "Instagram": "Social Media",
    "TikTok": "Social Media",
    "X (Twitter)": "Social Media",
    "Reddit": "Social Media",
    "WhatsApp": "Social Media",
    "YouTube": "Entertainment",
    "Netflix": "Entertainment",
    "Spotify": "Entertainment",
    "Duolingo": "Education",
    "Coursera": "Education",
    "Khan Academy": "Education",
    "VS Code": "Coding",
    "LeetCode": "Coding",
    "GitHub": "Coding",
}

# 14 days ending "today" (Aug 17, 2026 -> Aug 4 - Aug 17, 2026)
END_DATE = date(2026, 8, 17)
NUM_DAYS = 14

rows = []
for i in range(NUM_DAYS):
    day = END_DATE - timedelta(days=(NUM_DAYS - 1 - i))
    is_weekend = day.weekday() >= 5

    # pick which apps were touched that day (not every app every day)
    n_apps = random.randint(5, 8)
    todays_apps = random.sample(list(APPS.keys()), n_apps)

    for app in todays_apps:
        category = APPS[app]

        if category == "Social Media":
            base = random.randint(20, 65)
            if is_weekend:
                base += random.randint(15, 40)  # more doomscrolling on weekends
        elif category == "Entertainment":
            base = random.randint(15, 55)
            if is_weekend:
                base += random.randint(10, 45)
        elif category == "Education":
            base = random.randint(10, 35)
            if is_weekend:
                base = max(5, base - random.randint(5, 15))  # less studying on weekends
        else:  # Coding
            base = random.randint(20, 90)
            if is_weekend:
                base = max(5, base - random.randint(10, 40))  # less coding on weekends

        rows.append([day.isoformat(), app, category, base])

with open("screentime.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Date", "App_Name", "Category", "Minutes_Used"])
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows across {NUM_DAYS} days to screentime.csv")
