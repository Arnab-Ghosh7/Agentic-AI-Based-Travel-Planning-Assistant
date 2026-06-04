# Agentic AI-Style Travel Planning Assistant


## ✨ Features

 - **Obsidian Glassmorphic UI**: A dark theme incorporating visual gradients, clear margins, and responsive layouts.
- **5 Core Planning Tools**:
  - **Flight Search**: Searches local catalogs, ranking by value or pricing tier.
  - **Hotel Recommendation**: Matches amenities, star ratings, and prices with smart **Constraint Relaxation** fallback mechanisms.
  - **Places Discovery**: Schedules local spots of interest per day, filtering by rating and sights type.
  - **Live Weather Lookup**: Fetches active weather data from the free **Open-Meteo API** (or falls back to seasonal climate profiles offline).
  - **Budget Estimation**: Combines flight, hotel, and daily per-diem transport/food allowances for overall budgets.
- **AI Agent Chat Simulator**: An interactive chatbot panel that answers natural language questions about selected flights, hotel amenities, weather conditions, or travel expenses dynamically.
- **Weather-Aware Activity Scheduling**: Sourced meteorological data translates into actionable tips (e.g., advising indoor museum plans on thundery afternoons).
- **Decision Justifications**: Provides reasoning fields highlighting why specific flights or hotels were selected for the user's budgetclass.

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Logic**: Python, requests
- **Data Layers**: Local static JSON databases (`flights.json`, `hotels.json`, `places.json`)
- **API**: Open-Meteo (Free weather forecasting)

---

## 📂 Project Architecture

```
f:\Agentic AI Travel Planner\
├── app.py           # Streamlit Web Application frontend
├── planner.py       # Offline Planning engine (rules & heuristics)
├── tools.py         # Data loaders & external weather APIs
├── test_suite.py    # Formal unit tests
├── flights.json     # Local flight dataset
├── hotels.json      # Local hotels dataset
└── places.json      # Local attractions dataset
```

---

## 🚀 Setup & Execution
### 1. Pre-requisites
Ensure Python 3.8+ is installed on your machine.


### 2. Install Dependencies
Install the required lightweight dependencies (Streamlit, requests, and pandas):
```bash
pip install streamlit requests pandas
```

### 3. Run the Streamlit Application
Launch the frontend dashboard locally:
```bash
streamlit run app.py
```

### 4. Running Unit Tests
Validate all tools and planner logic:
```bash
python test_suite.py
```

---

## 🧪 Verification & Reliability

Vagabond features a comprehensive suite of unit tests validating all core data operations, ensuring no edge-case input crashes the travel builder. All 6 tests in `test_suite.py` pass out-of-the-box.


## Author
Arnab Ghosh
