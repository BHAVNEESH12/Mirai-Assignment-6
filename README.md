# Life-OS Wellbeing Dashboard

A Streamlit dashboard that visualizes daily screen time data and uses the Gemini API to act as a lifestyle and productivity coach.

## Features
- Interactive controls to filter dates and set screen time goals.
- Metrics display for total screen time, top used app, and goal variance.
- Data charts showing 14-day trends and category breakdowns.
- AI life coaching using Gemini API with automatic key rotation.
- Persona avatar generation based on productivity habits.

## How to Run

1. Clone the repository and navigate into the project folder:
   git clone https://github.com/BHAVNEESH12/Mirai-Assignment-6
   cd Mirai-Assignment-6

2. Install dependencies:
   pip install -r requirements.txt

3. Create a `.env` file in the root directory and add your API keys:
   GEMINI_API_KEY=your_primary_key
   GEMINI_API_KEY_BACKUP_1=your_backup_key_1
   GEMINI_API_KEY_BACKUP_2=your_backup_key_2

4. Run the Streamlit app:
   streamlit run app.py
