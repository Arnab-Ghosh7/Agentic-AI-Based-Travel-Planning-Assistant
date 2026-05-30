import json
import os
import requests
from datetime import datetime

DATA_DIR = r"f:\Agentic AI Travel Planner"

# City coordinates mapping
CITY_COORDINATES = {
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Goa": {"lat": 15.2993, "lon": 74.1240},
    "Bangalore": {"lat": 12.9716, "lon": 77.5946},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Jaipur": {"lat": 26.9124, "lon": 75.7873}
}

# Weather code descriptions mapping (WMO weather codes)
WEATHER_CODES = {
    0: "Sunny/Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    71: "Slight Snowfall",
    73: "Moderate Snowfall",
    75: "Heavy Snowfall",
    77: "Snow Grains",
    80: "Slight Rain Showers",
    81: "Moderate Rain Showers",
    82: "Violent Rain Showers",
    85: "Slight Snow Showers",
    86: "Heavy Snow Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Slight Hail",
    99: "Thunderstorm with Heavy Hail"
}

def load_dataset(filename):
    """Loads a JSON dataset from the workspace."""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return []

def search_flights(origin, destination, travel_date=None):
    """
    Searches and filters flights from flights.json.
    Ranks them by price (cheapest first).
    """
    flights = load_dataset("flights.json")
    results = []
    
    # Normalize strings for comparison
    origin_norm = origin.strip().lower()
    dest_norm = destination.strip().lower()
    
    for f in flights:
        if f.get("from", "").strip().lower() == origin_norm and f.get("to", "").strip().lower() == dest_norm:
            results.append(f)
            
    # Sort results by price
    results.sort(key=lambda x: x.get("price", 999999))
    return results

def recommend_hotels(city, min_stars=0, max_price=float('inf'), amenities=None):
    """
    Searches hotels from hotels.json.
    Filters by city, stars, and price limit.
    Optionally matches a list of required amenities.
    Sorts by stars (descending) and price (ascending).
    """
    hotels = load_dataset("hotels.json")
    results = []
    city_norm = city.strip().lower()
    
    if amenities is None:
        amenities = []
    
    req_amenities = [a.lower().strip() for a in amenities]
    
    for h in hotels:
        if h.get("city", "").strip().lower() != city_norm:
            continue
        if h.get("stars", 0) < min_stars:
            continue
        if h.get("price_per_night", 0) > max_price:
            continue
            
        # Check amenities
        hotel_amenities = [a.lower().strip() for a in h.get("amenities", [])]
        has_all = True
        for ra in req_amenities:
            if ra not in hotel_amenities:
                has_all = False
                break
                
        if has_all:
            results.append(h)
            
    # Sort by stars descending, then price ascending
    results.sort(key=lambda x: (-x.get("stars", 0), x.get("price_per_night", 999999)))
    return results

def discover_places(city, place_type=None, min_rating=0.0):
    """
    Searches places of interest from places.json.
    Filters by city, type, and rating.
    Sorts by rating descending.
    """
    places = load_dataset("places.json")
    results = []
    city_norm = city.strip().lower()
    
    for p in places:
        if p.get("city", "").strip().lower() != city_norm:
            continue
        if place_type and p.get("type", "").strip().lower() != place_type.strip().lower():
            continue
        if p.get("rating", 0.0) < min_rating:
            continue
            
        results.append(p)
        
    results.sort(key=lambda x: x.get("rating", 0.0), reverse=True)
    return results

def lookup_weather(city, start_date=None, end_date=None):
    """
    Calls the free Open-Meteo API to get real-time/forecast weather for a city.
    If the API fails, it falls back to realistic seasonal weather based on month.
    """
    coords = CITY_COORDINATES.get(city)
    if not coords:
        # Generic fallback
        return [{"day": 1, "temp": "28 C", "condition": "Partly Cloudy"}]
        
    lat = coords["lat"]
    lon = coords["lon"]
    
    # Estimate range of days
    num_days = 3
    month = 5 # default to May
    if start_date:
        try:
            if isinstance(start_date, str):
                dt_start = datetime.strptime(start_date.split("T")[0], "%Y-%m-%d")
            else:
                dt_start = start_date
            month = dt_start.month
            
            if end_date:
                if isinstance(end_date, str):
                    dt_end = datetime.strptime(end_date.split("T")[0], "%Y-%m-%d")
                else:
                    dt_end = end_date
                num_days = max(1, (dt_end - dt_start).days + 1)
        except Exception:
            pass
            
    num_days = min(num_days, 7) # Cap forecast days at 7
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto"
    
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            daily_data = data.get("daily", {})
            times = daily_data.get("time", [])
            max_temps = daily_data.get("temperature_2m_max", [])
            min_temps = daily_data.get("temperature_2m_min", [])
            codes = daily_data.get("weathercode", [])
            
            forecast = []
            for i in range(min(num_days, len(times))):
                code = codes[i] if i < len(codes) else 0
                condition = WEATHER_CODES.get(code, "Clear")
                max_t = max_temps[i] if i < len(max_temps) else 25.0
                min_t = min_temps[i] if i < len(min_temps) else 15.0
                
                forecast.append({
                    "day": i + 1,
                    "date": times[i],
                    "temp_max": f"{max_t} C",
                    "temp_min": f"{min_t} C",
                    "condition": condition
                })
            return forecast
    except Exception as e:
        print(f"Weather API fetch failed: {e}. Using seasonal fallback.")
        
    # Seasonal Fallback Weather based on month
    forecast = []
    seasons = {
        "winter": (12, 1, 2), # cold & clear
        "summer": (3, 4, 5, 6), # hot
        "monsoon": (7, 8, 9), # rainy
        "post_monsoon": (10, 11) # moderate
    }
    
    season = "winter"
    for s_name, months in seasons.items():
        if month in months:
            season = s_name
            break
            
    base_temps = {
        "Delhi": {"winter": (21, 8, "Sunny but Cool"), "summer": (40, 28, "Scorching Hot"), "monsoon": (33, 26, "Thundery Showers"), "post_monsoon": (29, 16, "Pleasant & Clear")},
        "Mumbai": {"winter": (30, 19, "Warm & Clear"), "summer": (34, 26, "Humid & Sunny"), "monsoon": (29, 24, "Heavy Monsoon Rain"), "post_monsoon": (32, 22, "Warm & Clear")},
        "Goa": {"winter": (32, 20, "Pleasant Beach Weather"), "summer": (34, 26, "Sunny & Warm"), "monsoon": (29, 24, "Heavy Showers"), "post_monsoon": (31, 23, "Sunny & Breezy")},
        "Bangalore": {"winter": (27, 15, "Beautiful & Cool"), "summer": (33, 21, "Warm & Breeze"), "monsoon": (28, 19, "Mild Drizzles"), "post_monsoon": (28, 18, "Pleasant")},
        "Chennai": {"winter": (29, 21, "Pleasant"), "summer": (38, 28, "Hot & Humid"), "monsoon": (32, 25, "Rainy"), "post_monsoon": (30, 23, "Thunderstorms")},
        "Hyderabad": {"winter": (29, 15, "Sunny & Dry"), "summer": (39, 26, "Hot & Sunny"), "monsoon": (31, 22, "Rainy"), "post_monsoon": (30, 18, "Clear & Cool")},
        "Kolkata": {"winter": (26, 14, "Pleasant & Cool"), "summer": (37, 26, "Hot & Humid"), "monsoon": (31, 25, "Tropical Rain"), "post_monsoon": (30, 20, "Clear Skies")},
        "Jaipur": {"winter": (23, 9, "Chilly Nights, Warm Days"), "summer": (41, 27, "Scorching & Dry"), "monsoon": (33, 25, "Rain Showers"), "post_monsoon": (31, 16, "Pleasant & Clear")}
    }
    
    city_weather = base_temps.get(city, base_temps["Delhi"])
    max_t, min_t, desc = city_weather.get(season, (30, 20, "Partly Cloudy"))
    
    for i in range(num_days):
        forecast.append({
            "day": i + 1,
            "date": f"Day {i+1}",
            "temp_max": f"{max_t + (i % 2) - 1} C",
            "temp_min": f"{min_t + (i % 2) - 1} C",
            "condition": desc
        })
        
    return forecast

def estimate_budget(flight_price, hotel_price_per_night, num_nights, daily_expenses=1500):
    """
    Calculates detailed budget breakdown.
    """
    accommodation_cost = hotel_price_per_night * num_nights
    food_transport_cost = daily_expenses * (num_nights + 1)
    total_cost = flight_price + accommodation_cost + food_transport_cost
    
    return {
        "flight_cost": flight_price,
        "accommodation_cost": accommodation_cost,
        "food_transport_cost": food_transport_cost,
        "total_cost": total_cost
    }
