import sys
import os
from datetime import datetime
import tools

def generate_itinerary(origin, destination, start_date_str, end_date_str, budget_tier="mid-range", min_stars=0, amenities=None):
    """
    Intelligent Offline Planning Engine that generates premium itineraries,
    customized reasoning justifications, and constraint-relaxed selections.
    """
    if not amenities:
        amenities = []
        
    # 1. Parse dates and calculate duration
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    except Exception:
        start_date = datetime.now()
        end_date = datetime.now()
        
    num_days = max(1, (end_date - start_date).days + 1)
    
    # 2. Select Flight
    flights = tools.search_flights(origin, destination)
    selected_flight = None
    flight_reasoning = ""
    
    if flights:
        if budget_tier == "budget":
            selected_flight = flights[0] # Cheapest
            flight_reasoning = f"We selected {selected_flight['airline']} ({selected_flight['flight_id']}) because it is the absolute cheapest flight option available from {origin} to {destination}, maximizing your savings."
        elif budget_tier == "luxury":
            # Try to find a premium flight or just the highest priced / most convenient
            selected_flight = flights[-1] # Most premium/expensive
            flight_reasoning = f"We selected {selected_flight['airline']} ({selected_flight['flight_id']}) which is a highly rated flight for maximum comfort and convenient timing on your route from {origin} to {destination}."
        else: # Mid-range
            # Median or first good option
            idx = len(flights) // 2
            selected_flight = flights[idx]
            flight_reasoning = f"We selected {selected_flight['airline']} ({selected_flight['flight_id']}) as it represents the optimal balance of scheduling convenience and value on the {origin} to {destination} route."
    else:
        # Mock flight if none exist in dataset (to prevent blank results)
        estimated_price = 3200 if budget_tier == "budget" else (7800 if budget_tier == "luxury" else 4800)
        selected_flight = {
            "flight_id": "FL-SIMULATED",
            "airline": "IndiGo (Simulated)",
            "from": origin,
            "to": destination,
            "departure_time": f"{start_date_str}T08:30:00",
            "arrival_time": f"{start_date_str}T11:00:00",
            "price": estimated_price,
            "simulated": True
        }
        flight_reasoning = f"No exact flight was found in our offline database for this specific route. We simulated a highly reliable direct Indigo morning flight at a standard rate of Rs. {estimated_price} to complete your itinerary."

    # 3. Select Hotel (with Constraint Relaxation)
    hotels = tools.recommend_hotels(destination, min_stars=min_stars, amenities=amenities)
    hotel_reasoning = ""
    relaxed = False
    
    # If no hotels matching, perform constraint relaxation
    if not hotels and amenities:
        # Relax amenities first
        hotels = tools.recommend_hotels(destination, min_stars=min_stars)
        relaxed = True
        hotel_reasoning += "Note: We relaxed your amenities preferences to ensure hotel availability. "
        
    if not hotels:
        # Relax stars rating
        hotels = tools.recommend_hotels(destination, min_stars=0)
        relaxed = True
        hotel_reasoning += "Note: We relaxed your star-rating filter to secure an accommodation in the destination. "
        
    if not hotels:
        # Mock hotel fallback
        estimated_rate = 1800 if budget_tier == "budget" else (6500 if budget_tier == "luxury" else 3500)
        selected_hotel = {
            "hotel_id": "HOT-SIMULATED",
            "name": f"Royal {destination} Heritage Lodge (Simulated)",
            "city": destination,
            "stars": 4 if budget_tier == "luxury" else 3,
            "price_per_night": estimated_rate,
            "amenities": ["wifi", "breakfast"],
            "simulated": True
        }
        hotel_reasoning = f"No direct hotel properties were available in our static data folder. We simulated a gorgeous {selected_hotel['stars']}-star property located in the city center at Rs. {estimated_rate}/night."
    else:
        if budget_tier == "budget":
            # Cheapest hotel matching
            hotels.sort(key=lambda x: x.get("price_per_night", 999999))
            selected_hotel = hotels[0]
            hotel_reasoning += f"We selected {selected_hotel['name']} ({selected_hotel['stars']}-Star) as it is the most cost-efficient option at Rs. {selected_hotel['price_per_night']}/night, keeping your accommodation expenses minimal."
        elif budget_tier == "luxury":
            # Highest rating, then highest price
            hotels.sort(key=lambda x: (-x.get("stars", 0), -x.get("price_per_night", 0)))
            selected_hotel = hotels[0]
            hotel_reasoning += f"We chose the prestigious {selected_hotel['name']} ({selected_hotel['stars']}-Star) to provide you with the ultimate luxury experience, complete with premium amenities including: {', '.join(selected_hotel.get('amenities', []))}."
        else: # Mid-range
            # Sort by stars desc, then price asc
            hotels.sort(key=lambda x: (-x.get("stars", 0), x.get("price_per_night", 0)))
            # Pick a middle one or high-rated reasonable price
            idx = min(len(hotels) - 1, 1)
            selected_hotel = hotels[idx]
            hotel_reasoning += f"We selected {selected_hotel['name']} ({selected_hotel['stars']}-Star) which is rated exceptionally high for comfort and service while representing stellar value at Rs. {selected_hotel['price_per_night']}/night."

    # 4. Get Weather Forecast
    weather_forecast = tools.lookup_weather(destination, start_date_str, end_date_str)
    
    # 5. Select Places & Schedule Daily POIs
    all_places = tools.discover_places(destination, min_rating=3.0)
    
    # Make sure we have enough places to plan 2 sights a day
    places_needed = num_days * 2
    itinerary_days = []
    
    # If the database has fewer sights than needed, let's inject realistic points of interest
    default_sights = {
        "Delhi": ["India Gate", "Red Fort", "Qutub Minar", "Humayun's Tomb", "Lotus Temple", "Akshardham Temple", "Chandni Chowk"],
        "Mumbai": ["Gateway of India", "Marine Drive", "Elephanta Caves", "Chhatrapati Shivaji Terminus", "Haji Ali Dargah", "Colaba Causeway"],
        "Goa": ["Baga Beach", "Calangute Beach", "Basilica of Bom Jesus", "Fort Aguada", "Dudhsagar Falls", "Anjuna Flea Market"],
        "Bangalore": ["Lalbagh Botanical Garden", "Bangalore Palace", "Cubbon Park", "Wonderla", "Bannerghatta National Park", "Nandi Hills"],
        "Chennai": ["Marina Beach", "Kapaleeshwarar Temple", "Fort St. George", "Santhome Cathedral", "VGP Golden Beach", "DakshinaChitra"],
        "Hyderabad": ["Charminar", "Golconda Fort", "Hussain Sagar Lake", "Ramoji Film City", "Salargung Museum", "Chowmahalla Palace"],
        "Kolkata": ["Victoria Memorial", "Howrah Bridge", "Dakshineswar Kali Temple", "Indian Museum", "Science City", "Park Street"],
        "Jaipur": ["Hawa Mahal", "Amer Fort", "City Palace", "Jantar Mantar", "Chokhi Dhani", "Nahargarh Fort", "Jaigarh Fort"]
    }
    
    city_defaults = default_sights.get(destination, ["Local Market", "Historic Center", "City Park", "Local Temple", "Cultural Museum"])
    
    # Merge database places with defaults to guarantee rich detailed list
    available_sights = []
    seen_names = set()
    
    for p in all_places:
        name = p.get("name", "")
        if name not in seen_names:
            available_sights.append({
                "name": name,
                "type": p.get("type", "sightseeing"),
                "rating": p.get("rating", 4.0),
                "simulated": False
            })
            seen_names.add(name)
            
    for ds in city_defaults:
        if ds not in seen_names:
            available_sights.append({
                "name": ds,
                "type": "landmark",
                "rating": 4.5,
                "simulated": True
            })
            seen_names.add(ds)
            
    # Plan day-by-day sights
    for day_idx in range(num_days):
        day_num = day_idx + 1
        
        # Get weather for this day
        day_weather = {"condition": "Clear Sky", "temp_max": "30 C", "temp_min": "20 C"}
        if day_idx < len(weather_forecast):
            day_weather = weather_forecast[day_idx]
            
        # Select 2 unique sights for this day
        sight_1 = available_sights[(day_idx * 2) % len(available_sights)]
        sight_2 = available_sights[(day_idx * 2 + 1) % len(available_sights)]
        
        # Generate weather-aware advice
        advice = "A perfect day for sightseeing! Keep a water bottle handy."
        cond = day_weather.get("condition", "").lower()
        if "rain" in cond or "drizzle" in cond or "thunder" in cond or "shower" in cond:
            advice = "Rain expected! We highly suggest carrying an umbrella or visiting indoor sights like museums or covered palaces."
        elif "hot" in cond or "scorching" in cond:
            advice = "Very high temperatures expected today. Try to visit outdoor sights early in the morning and stay hydrated!"
        elif "cool" in cond or "winter" in cond or "chilly" in cond:
            advice = "Cool weather expected, perfect for walking tours! Carry a light jacket for the evening."
            
        itinerary_days.append({
            "day": day_num,
            "date": day_weather.get("date", f"Day {day_num}"),
            "weather": day_weather,
            "morning_activity": {
                "name": sight_1["name"],
                "type": sight_1["type"],
                "rating": sight_1["rating"],
                "time": "09:30 AM"
            },
            "afternoon_activity": {
                "name": sight_2["name"],
                "type": sight_2["type"],
                "rating": sight_2["rating"],
                "time": "02:30 PM"
            },
            "evening_recommendation": {
                "name": "Relax at a local cafe and explore local street food markets",
                "time": "06:30 PM"
            },
            "agent_advice": advice
        })

    # 6. Budget Breakdown
    flight_cost = selected_flight.get("price", 0)
    hotel_cost_per_night = selected_hotel.get("price_per_night", 0)
    
    # Calculate daily expenses based on budget tier
    daily_expense_rates = {
        "budget": 1000,
        "mid-range": 2000,
        "luxury": 4500
    }
    daily_rate = daily_expense_rates.get(budget_tier, 2000)
    
    budget_breakdown = tools.estimate_budget(
        flight_price=flight_cost,
        hotel_price_per_night=hotel_cost_per_night,
        num_nights=num_days - 1, # Nights is Days - 1
        daily_expenses=daily_rate
    )

    # 7. Final Combined Itinerary Object
    return {
        "destination": destination,
        "origin": origin,
        "duration_days": num_days,
        "start_date": start_date_str,
        "end_date": end_date_str,
        "budget_tier": budget_tier.capitalize(),
        "selected_flight": selected_flight,
        "selected_hotel": selected_hotel,
        "flight_reasoning": flight_reasoning,
        "hotel_reasoning": hotel_reasoning,
        "itinerary": itinerary_days,
        "budget_breakdown": budget_breakdown,
        "weather_summary": weather_forecast
    }
