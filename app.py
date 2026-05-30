import streamlit as st
import datetime
import pandas as pd
import json
import os
import sys
import textwrap

sys.path.append(r"f:\Agentic AI Travel Planner")
import tools
import planner

st.set_page_config(
    page_title="Vagabond - AI Agentic Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    
    /* Background & Overlays */
    .stApp {
        background-color: #0b0f19;
        background-image: 
            radial-gradient(at 10% 10%, rgba(29, 78, 216, 0.15) 0px, transparent 50%),
            radial-gradient(at 90% 10%, rgba(139, 92, 246, 0.15) 0px, transparent 50%),
            radial-gradient(at 50% 90%, rgba(236, 72, 153, 0.1) 0px, transparent 50%);
        background-attachment: fixed;
    }
    
    /* Title Gradient */
    .title-gradient {
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Cards and Glassmorphism */
    .card {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .card:hover {
        transform: translateY(-2px);
        border-color: rgba(139, 92, 246, 0.3);
        box-shadow: 0 10px 30px rgba(139, 92, 246, 0.1);
    }
    
    /* Day wise timeline card styling */
    .day-card {
        background: rgba(22, 28, 45, 0.7);
        border-left: 4px solid #8b5cf6;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    /* Metrics panel */
    .metric-badge {
        background: rgba(139, 92, 246, 0.1);
        border: 1px solid rgba(139, 92, 246, 0.25);
        color: #c084fc;
        padding: 6px 12px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 8px;
    }
    .metric-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
    }
    .metric-val {
        color: #f8fafc;
        font-size: 1.5rem;
        font-weight: 700;
        font-family: 'Outfit', sans-serif;
    }
    .metric-lbl {
        color: #94a3b8;
        font-size: 0.9rem;
    }
    
    /* Custom advice card styling */
    .advice-box {
        background: rgba(234, 179, 8, 0.08);
        border: 1px dashed rgba(234, 179, 8, 0.3);
        color: #fef08a;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 0.9rem;
        margin-top: 10px;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #080c14;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Custom buttons */
    .stButton>button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 14px rgba(124, 58, 237, 0.4);
        width: 100%;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%);
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# Layout Title
col_title, col_logo = st.columns([5, 1])
with col_title:
    st.markdown('<div class="title-gradient">VAGABOND</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Agentic AI Travel Assistant — Local & High-Fidelity</div>', unsafe_allow_html=True)

# Define standard lists for inputs
CITIES = ["Delhi", "Mumbai", "Goa", "Bangalore", "Chennai", "Hyderabad", "Kolkata", "Jaipur"]
AMENITIES_OPTIONS = ["wifi", "pool", "gym", "breakfast", "parking", "spa"]

# Initialize Session States
if 'itinerary' not in st.session_state:
    st.session_state.itinerary = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Sidebar Form Input
with st.sidebar:
    st.markdown("### 🛠️ Planner Settings")
    st.markdown("---")
    
    origin = st.selectbox("Departure City", CITIES, index=5) # Default Hyderabad
    destination = st.selectbox("Destination City", CITIES, index=0) # Default Delhi
    
    if origin == destination:
        st.warning("Departure and Destination cities must be different.")
        
    # Date Picker
    today = datetime.date.today()
    col_dates = st.columns(2)
    with col_dates[0]:
        start_date = st.date_input("Start Date", today + datetime.timedelta(days=1))
    with col_dates[1]:
        end_date = st.date_input("End Date", today + datetime.timedelta(days=4))
        
    if start_date > end_date:
        st.error("Error: End Date must be after Start Date.")
        
    budget_tier = st.select_slider(
        "Budget Tier Preference",
        options=["budget", "mid-range", "luxury"],
        value="mid-range"
    )
    
    min_stars = st.slider("Min Hotel Star Rating", 1, 5, 3)
    
    selected_amenities = st.multiselect("Required Hotel Amenities", AMENITIES_OPTIONS, default=["wifi"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    plan_button = st.button("✨ Draft Itinerary")

# Track sidebar input changes and regenerate reactively if a plan is already active
current_inputs = {
    "origin": origin,
    "destination": destination,
    "start_date": start_date.strftime("%Y-%m-%d") if isinstance(start_date, datetime.date) else start_date,
    "end_date": end_date.strftime("%Y-%m-%d") if isinstance(end_date, datetime.date) else end_date,
    "budget_tier": budget_tier,
    "min_stars": min_stars,
    "amenities": tuple(selected_amenities)
}

inputs_changed = False
for key, val in current_inputs.items():
    state_key = f"prev_{key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = val
        inputs_changed = True
    elif st.session_state[state_key] != val:
        st.session_state[state_key] = val
        inputs_changed = True

# Reactively regenerate if plan is active and filters changed
if st.session_state.itinerary is not None and inputs_changed:
    if origin != destination and start_date <= end_date:
        itinerary = planner.generate_itinerary(
            origin=origin,
            destination=destination,
            start_date_str=current_inputs["start_date"],
            end_date_str=current_inputs["end_date"],
            budget_tier=budget_tier,
            min_stars=min_stars,
            amenities=selected_amenities
        )
        st.session_state.itinerary = itinerary
        if "chat_history" in st.session_state and len(st.session_state.chat_history) > 0:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"🔄 *System Update: Refreshed your plan dynamically! Budget: **{budget_tier.capitalize()}**, Min Stars: **{min_stars}★**, Amenities: **{', '.join(selected_amenities)}**.*"
            })

# Handle Plan generation from button
if plan_button:
    if origin == destination:
        st.error("Departure and destination cities cannot be identical!")
    elif start_date > end_date:
        st.error("Start date must precede the end date!")
    else:
        with st.spinner("🧠 Synthesizing itineraries, evaluating budget curves, and fetching live weather datasets..."):
            itinerary = planner.generate_itinerary(
                origin=origin,
                destination=destination,
                start_date_str=start_date.strftime("%Y-%m-%d"),
                end_date_str=end_date.strftime("%Y-%m-%d"),
                budget_tier=budget_tier,
                min_stars=min_stars,
                amenities=selected_amenities
            )
            st.session_state.itinerary = itinerary
            # Reset chatbot conversations for new trip
            st.session_state.chat_history = [
                {
                    "role": "assistant",
                    "content": f"Hello! I am your AI Agentic Travel Assistant. I have crafted a gorgeous **{itinerary['budget_tier']}** trip to **{itinerary['destination']}** from **{itinerary['origin']}** ({itinerary['duration_days']} Days).\n\nYou can ask me specific questions like:\n- *'Why did you select this hotel?'*\n- *'Break down the trip budget for me.'*\n- *'What is the weather forecast for Day 2?'*\n- *'What's our flight detail?'*"
                }
            ]
            st.success("🎉 Itinerary successfully generated and optimized!")

# Main Panel Display
if st.session_state.itinerary:
    itin = st.session_state.itinerary
    
    # 2-Tab Panel: 1. Main Itinerary Explorer, 2. Chat with AI Agent
    tab_planner, tab_agent = st.tabs(["🗺️ Itinerary Explorer", "💬 Agent Chat Assistant"])
    
    with tab_planner:
        # Top Cards: Trip Overview & Metric Summary
        col_overview, col_metrics = st.columns([3, 2])
        
        with col_overview:
            st.markdown(f"""
            <div class="card">
                <h3 style="margin-top:0; color:#a78bfa;">🌴 Trip Overview</h3>
                <h2 style="margin: 5px 0 15px 0; color:#f8fafc;">{itin['origin']} to {itin['destination']}</h2>
                <div style="display:flex; gap:10px; margin-bottom:15px;">
                    <span class="metric-badge">📅 {itin['duration_days']} Days ({itin['start_date']} to {itin['end_date']})</span>
                    <span class="metric-badge">💰 {itin['budget_tier']} Budget</span>
                </div>
                <p style="color:#94a3b8; font-size:0.95rem; line-height:1.5;">
                    This travel plan is customized to balance travel convenience, accommodation comfort, and daily attractions.
                    We have queried live meteorology databases and local catalogs to secure a budget-friendly flight,
                    highly rated hotel stays, and custom local attractions matching your filters.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_metrics:
            st.markdown('<div class="card" style="padding-bottom:15px;">', unsafe_allow_html=True)
            st.markdown('<h3 style="margin-top:0; color:#f472b6;">📊 Budget Analysis</h3>', unsafe_allow_html=True)
            
            breakdown = itin['budget_breakdown']
            
            # Interactive Metric rows
            st.markdown(f"""
            <div class="metric-container">
                <span class="metric-lbl">✈️ Flight Cost</span>
                <span class="metric-val">Rs. {breakdown['flight_cost']:,}</span>
            </div>
            <div class="metric-container">
                <span class="metric-lbl">🏨 Hotel ({itin['duration_days'] - 1} Nights)</span>
                <span class="metric-val">Rs. {breakdown['accommodation_cost']:,}</span>
            </div>
            <div class="metric-container">
                <span class="metric-lbl">🍔 Food & Daily Local Travel</span>
                <span class="metric-val">Rs. {breakdown['food_transport_cost']:,}</span>
            </div>
            <div class="metric-container" style="background: rgba(139, 92, 246, 0.15); border-color: rgba(139, 92, 246, 0.4);">
                <span class="metric-lbl" style="font-weight:700; color:#d8b4fe;">💸 TOTAL ESTIMATED EXPENSE</span>
                <span class="metric-val" style="color:#e9d5ff;">Rs. {breakdown['total_cost']:,}</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Flights & Hotels Section
        col_flight, col_hotel = st.columns(2)
        
        with col_flight:
            flight = itin['selected_flight']
            st.markdown(f"""
            <div class="card" style="height: 100%;">
                <h3 style="margin-top:0; color:#3b82f6; display:flex; align-items:center; gap:8px;">✈️ Selected Flight</h3>
                <h4 style="margin: 10px 0 5px 0; color:#f8fafc;">{flight['airline']} • {flight['flight_id']}</h4>
                <p style="color:#cbd5e1; font-size:0.9rem; margin-bottom:12px;">
                    <strong>Route:</strong> {flight['from']} ➡️ {flight['to']}<br>
                    <strong>Departs:</strong> {flight['departure_time'].replace('T', ' ')}<br>
                    <strong>Arrives:</strong> {flight['arrival_time'].replace('T', ' ')}
                </p>
                <div style="font-size:1.15rem; font-weight:700; color:#38bdf8; margin-bottom:15px;">
                    Price: Rs. {flight['price']:,}
                </div>
                <div style="background:rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.2); padding:12px; border-radius:8px; font-size:0.88rem; color:#93c5fd; line-height:1.4;">
                    💡 <strong>Agent Justification:</strong> {itin['flight_reasoning']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_hotel:
            hotel = itin['selected_hotel']
            stars_str = "⭐" * hotel['stars']
            st.markdown(f"""
            <div class="card" style="height: 100%;">
                <h3 style="margin-top:0; color:#10b981; display:flex; align-items:center; gap:8px;">🏨 Booked Accommodation</h3>
                <h4 style="margin: 10px 0 5px 0; color:#f8fafc;">{hotel['name']} • {stars_str}</h4>
                <p style="color:#cbd5e1; font-size:0.9rem; margin-bottom:12px;">
                    <strong>Location:</strong> {hotel['city']}<br>
                    <strong>Amenities:</strong> {', '.join(hotel['amenities']).title()}
                </p>
                <div style="font-size:1.15rem; font-weight:700; color:#34d399; margin-bottom:15px;">
                    Price: Rs. {hotel['price_per_night']:,}/night
                </div>
                <div style="background:rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2); padding:12px; border-radius:8px; font-size:0.88rem; color:#a7f3d0; line-height:1.4;">
                    💡 <strong>Agent Justification:</strong> {itin['hotel_reasoning']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Day-by-Day Timeline Planner
        st.markdown("<br><h2 style='color:#f8fafc; border-bottom:1px solid rgba(255,255,255,0.08); padding-bottom:8px;'>📅 Day-by-Day Plan & Activities</h2>", unsafe_allow_html=True)
        
        # Display coordinate map of destination
        coords = tools.CITY_COORDINATES.get(itin['destination'])
        if coords:
            with st.expander("📍 Destination Location Map", expanded=False):
                df_map = pd.DataFrame([{"lat": coords["lat"], "lon": coords["lon"]}])
                st.map(df_map, zoom=11)
        
        for day in itin['itinerary']:
            st.html(f"""
            <div class="day-card">
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom:8px; margin-bottom:12px;">
                    <h3 style="margin:0; color:#a78bfa;">Day {day['day']} — {day['date']}</h3>
                    <span style="background: rgba(244, 114, 182, 0.15); color: #f472b6; border: 1px solid rgba(244, 114, 182, 0.3); padding: 4px 10px; border-radius: 6px; font-size:0.85rem; font-weight:600;">
                        ☁️ {day['weather']['condition']} ({day['weather']['temp_min']} to {day['weather']['temp_max']})
                    </span>
                </div>
                
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px;">
                    <div>
                        <strong style="color:#60a5fa; font-size:0.9rem;">🌅 MORNING ACTIVITY ({day['morning_activity']['time']})</strong>
                        <h4 style="margin:4px 0 2px 0; color:#e2e8f0;">🏛️ {day['morning_activity']['name']}</h4>
                        <span style="font-size:0.8rem; color:#94a3b8;">Type: {day['morning_activity']['type'].title()} • Rating: ⭐ {day['morning_activity']['rating']}</span>
                    </div>
                    <div>
                        <strong style="color:#34d399; font-size:0.9rem;">🌇 AFTERNOON ACTIVITY ({day['afternoon_activity']['time']})</strong>
                        <h4 style="margin:4px 0 2px 0; color:#e2e8f0;">🛍️ {day['afternoon_activity']['name']}</h4>
                        <span style="font-size:0.8rem; color:#94a3b8;">Type: {day['afternoon_activity']['type'].title()} • Rating: ⭐ {day['afternoon_activity']['rating']}</span>
                    </div>
                </div>
                
                <div style="margin-top:15px; border-top:1px dashed rgba(255,255,255,0.05); padding-top:10px;">
                    <strong style="color:#f472b6; font-size:0.9rem;">🌃 EVENING PLANS ({day['evening_recommendation']['time']})</strong>
                    <p style="margin:4px 0 0 0; color:#cbd5e1; font-size:0.95rem;">{day['evening_recommendation']['name']}</p>
                </div>
                
                <div class="advice-box">
                    🤖 <strong>AI Agent Advice:</strong> {day['agent_advice']}
                </div>
            </div>
            """)
            
    with tab_agent:
        # Stunning offline chat assistant section
        st.markdown("<h3 style='margin-top:0; color:#a78bfa;'>💬 Interactive Travel Agent Chat</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:#94a3b8; font-size:0.9rem;'>Ask questions about your selected flights, hotels, attractions, weather guidelines, or overall budget.</p>", unsafe_allow_html=True)
        
        # Chat History Container
        chat_container = st.container(height=380)
        
        with chat_container:
            for msg in st.session_state.chat_history:
                if msg["role"] == "assistant":
                    st.chat_message("assistant", avatar="🤖").markdown(msg["content"])
                else:
                    st.chat_message("user", avatar="👤").markdown(msg["content"])
                    
        # User input box
        if prompt := st.chat_input("Ask something about your itinerary..."):
            # Append user message
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Simple keyword-aware offline smart agent responses
            prompt_lower = prompt.lower()
            response = ""
            
            # Extract key variables
            flight = itin['selected_flight']
            hotel = itin['selected_hotel']
            breakdown = itin['budget_breakdown']
            
            if "hotel" in prompt_lower or "stay" in prompt_lower or "accommodation" in prompt_lower:
                response = f"🏨 **Hotel Stay:** We recommended the **{hotel['name']}** in **{hotel['city']}** ({hotel['stars']}-Star).\n\n"
                response += f"- **Price:** Rs. {hotel['price_per_night']:,} per night.\n"
                response += f"- **Amenities:** {', '.join(hotel['amenities'])}\n\n"
                response += f"💡 **Agent Reason:** {itin['hotel_reasoning']}"
                
            elif "flight" in prompt_lower or "airline" in prompt_lower or "fly" in prompt_lower or "plane" in prompt_lower:
                response = f"✈️ **Flight Details:** We found a suitable route with **{flight['airline']}** (**{flight['flight_id']}**).\n\n"
                response += f"- **From:** {flight['from']} ➡️ **To:** {flight['to']}\n"
                response += f"- **Departs:** {flight['departure_time'].replace('T', ' ')}\n"
                response += f"- **Arrives:** {flight['arrival_time'].replace('T', ' ')}\n"
                response += f"- **Ticket Price:** Rs. {flight['price']:,}\n\n"
                response += f"💡 **Agent Reason:** {itin['flight_reasoning']}"
                
            elif "budget" in prompt_lower or "cost" in prompt_lower or "expense" in prompt_lower or "price" in prompt_lower or "money" in prompt_lower:
                response = f"📊 **Detailed Budget Breakdown:**\n\n"
                response += f"- ✈️ **Flight Fare:** Rs. {breakdown['flight_cost']:,}\n"
                response += f"- 🏨 **Hotel Cost ({itin['duration_days']-1} nights):** Rs. {breakdown['accommodation_cost']:,}\n"
                response += f"- 🍔 **Food & Local Commute:** Rs. {breakdown['food_transport_cost']:,} (estimated Rs. {breakdown['food_transport_cost']//itin['duration_days']:,}/day)\n"
                response += f"- 💳 **Total Estimated Budget:** **Rs. {breakdown['total_cost']:,}**"
                
            elif "weather" in prompt_lower or "forecast" in prompt_lower or "rain" in prompt_lower or "temperature" in prompt_lower:
                response = f"☁️ **Weather Forecast Overview in {itin['destination']}:**\n\n"
                for day in itin['itinerary']:
                    response += f"- **Day {day['day']} ({day['date']}):** {day['weather']['condition']} ({day['weather']['temp_min']} to {day['weather']['temp_max']}). *Advice: {day['agent_advice']}*\n"
                    
            elif "places" in prompt_lower or "activities" in prompt_lower or "attractions" in prompt_lower or "todo" in prompt_lower or "visit" in prompt_lower:
                response = f"🗺️ **Planned Sightseeing Highlights in {itin['destination']}:**\n\n"
                for day in itin['itinerary']:
                    response += f"**Day {day['day']}:**\n"
                    response += f"- 🌅 *Morning:* Visit **{day['morning_activity']['name']}** ({day['morning_activity']['type']})\n"
                    response += f"- 🌇 *Afternoon:* Visit **{day['afternoon_activity']['name']}** ({day['afternoon_activity']['type']})\n"
                    response += f"- 🌃 *Evening:* {day['evening_recommendation']['name']}\n\n"
                    
            elif "why" in prompt_lower or "explain" in prompt_lower or "justify" in prompt_lower:
                response = f"🤔 **Decisional Justifications:**\n\n"
                response += f"1. **Flight Choice:** {itin['flight_reasoning']}\n\n"
                response += f"2. **Hotel Choice:** {itin['hotel_reasoning']}"
                
            elif "hello" in prompt_lower or "hi" in prompt_lower or "hey" in prompt_lower:
                response = f"Hello! How can I assist you with your upcoming {itin['duration_days']}-day trip to {itin['destination']}? Ask me anything about flights, hotels, weather, local sights, or costs!"
                
            else:
                response = f"I am your local Agentic Travel Planner. I have scheduled a perfect **{itin['duration_days']}-day {itin['budget_tier']}** trip to **{itin['destination']}**.\n\nCould you please clarify your question? You can ask about:\n- ✈️ **Flights** (*'what is my flight?'*)\n- 🏨 **Hotel info** (*'which hotel is selected?'*)\n- 💰 **Budget breakdown** (*'what is the cost?'*)\n- ☀️ **Weather forecasts** (*'is it going to rain?'*)\n- 🏛️ **Sightseeing plans** (*'what places are we visiting?'*)"
                
            # Append response
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            # Force refresh page
            st.rerun()
else:
    # Landing state (when no plan is draft)
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px; background: rgba(17, 24, 39, 0.6); border-radius: 16px; border: 1px solid rgba(255,255,255,0.05); backdrop-filter: blur(10px); max-width: 800px; margin: 40px auto;">
        <h2 style="color: #cbd5e1; font-weight: 600;">Welcome to Vagabond Travel Planner ✈️</h2>
        <p style="color: #94a3b8; font-size: 1.1rem; max-width: 600px; margin: 10px auto 30px auto; line-height: 1.6;">
            Your offline agent-driven travel assistant. Configure your destination, travel window, budget tier, and hotel preferences in the sidebar, and watch the agent weave a customized schedule for you instantly.
        </p>
        <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
            <div style="background: rgba(30, 41, 59, 0.4); padding: 15px 25px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.03);">
                <span style="font-size: 2rem;">🧠</span>
                <h4 style="margin: 5px 0 0 0; color: #e2e8f0;">Constraint Relaxation</h4>
            </div>
            <div style="background: rgba(30, 41, 59, 0.4); padding: 15px 25px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.03);">
                <span style="font-size: 2rem;">🌦️</span>
                <h4 style="margin: 5px 0 0 0; color: #e2e8f0;">Live Weather Aware</h4>
            </div>
            <div style="background: rgba(30, 41, 59, 0.4); padding: 15px 25px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.03);">
                <span style="font-size: 2rem;">💬</span>
                <h4 style="margin: 5px 0 0 0; color: #e2e8f0;">Interactive Chatbot</h4>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
