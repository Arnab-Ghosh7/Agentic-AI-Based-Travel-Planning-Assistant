import unittest
import tools
import planner

class TestTravelPlannerTools(unittest.TestCase):
    
    def test_flight_search(self):
        # Hyderabad -> Delhi is in dataset
        flights = tools.search_flights("Hyderabad", "Delhi")
        self.assertGreater(len(flights), 0)
        self.assertEqual(flights[0]["from"], "Hyderabad")
        self.assertEqual(flights[0]["to"], "Delhi")
        
    def test_hotel_recommendation(self):
        # Delhi hotels in dataset
        hotels = tools.recommend_hotels("Delhi", min_stars=4, amenities=["wifi"])
        self.assertGreater(len(hotels), 0)
        for h in hotels:
            self.assertEqual(h["city"], "Delhi")
            self.assertGreaterEqual(h["stars"], 4)
            self.assertIn("wifi", h["amenities"])
            
    def test_places_discovery(self):
        # Delhi places in dataset
        places = tools.discover_places("Delhi", min_rating=4.0)
        self.assertGreater(len(places), 0)
        for p in places:
            self.assertEqual(p["city"], "Delhi")
            self.assertGreaterEqual(p["rating"], 4.0)
            
    def test_weather_lookup(self):
        # Weather lookup for Delhi
        weather = tools.lookup_weather("Delhi", start_date="2025-01-04", end_date="2025-01-05")
        self.assertGreater(len(weather), 0)
        self.assertIn("condition", weather[0])
        self.assertIn("temp_max", weather[0])
        
    def test_budget_estimation(self):
        budget = tools.estimate_budget(flight_price=3000, hotel_price_per_night=4000, num_nights=2, daily_expenses=2000)
        self.assertEqual(budget["flight_cost"], 3000)
        self.assertEqual(budget["accommodation_cost"], 8000)
        self.assertEqual(budget["food_transport_cost"], 6000)
        self.assertEqual(budget["total_cost"], 17000)

class TestPlanningEngine(unittest.TestCase):
    
    def test_itinerary_generation(self):
        itin = planner.generate_itinerary(
            origin="Hyderabad",
            destination="Delhi",
            start_date_str="2025-01-04",
            end_date_str="2025-01-06",
            budget_tier="mid-range",
            min_stars=4,
            amenities=["wifi"]
        )
        self.assertEqual(itin["origin"], "Hyderabad")
        self.assertEqual(itin["destination"], "Delhi")
        self.assertEqual(itin["duration_days"], 3)
        self.assertIn("selected_flight", itin)
        self.assertIn("selected_hotel", itin)
        self.assertEqual(len(itin["itinerary"]), 3)
        self.assertGreater(itin["budget_breakdown"]["total_cost"], 0)

if __name__ == "__main__":
    unittest.main()
