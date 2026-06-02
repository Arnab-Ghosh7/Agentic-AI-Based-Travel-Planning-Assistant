# Agentic AI-Style Travel Planning Assistant

Vagabond is a premium, high-fidelity offline **Travel Planning Assistant** built using **Python** and **Streamlit**. It mimics the advanced multi-step reasoning, constraints relaxation, and decision justification of an Agentic AI travel planner entirely offline, ensuring 100% free, reliable, and instant operations.

## ✨ Features

 class.

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
