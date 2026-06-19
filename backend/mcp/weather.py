import requests
import json
from datetime import datetime

def fetch_weather_recommendation(latitude: float = 28.61, longitude: float = 77.20) -> dict:
    """
    Weather MCP: Fetch local weather metrics and provide scaling recommendations.
    Uses Delhi (28.61, 77.20) as a default.
    """
    # Default fallback weather parameters
    weather_data = {
        "temp_c": 25.0,
        "humidity": 55.0,
        "air_quality": "Moderate",
        "description": "Clear skies",
        "source": "Mock Simulation"
    }
    
    try:
        # Try fetching from free public API (Open-Meteo) with 2 seconds timeout
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
        res = requests.get(url, timeout=2.0)
        if res.status_code == 200:
            data = res.json()
            curr = data.get("current_weather", {})
            weather_data["temp_c"] = float(curr.get("temperature", 25.0))
            weather_data["description"] = f"Code: {curr.get('weathercode', 0)}"
            weather_data["source"] = "Open-Meteo API"
    except Exception as e:
        print(f"Weather API fetch failed: {e}. Falling back to simulation.")
        # Seasonal simulation based on current calendar month
        month = datetime.now().month
        if month in [5, 6, 7]: # Hot summer
            weather_data["temp_c"] = 38.0
            weather_data["humidity"] = 45.0
            weather_data["description"] = "Hot & Sunny"
        elif month in [11, 12, 1]: # Cold winter
            weather_data["temp_c"] = 12.0
            weather_data["humidity"] = 65.0
            weather_data["description"] = "Chilly & Foggy"
        else: # Spring / Autumn
            weather_data["temp_c"] = 24.0
            weather_data["humidity"] = 50.0
            weather_data["description"] = "Pleasant"

    # Analyze metrics and provide recommendation rules
    temp = weather_data["temp_c"]
    recommendation = "Outdoor activity approved."
    warnings = []
    override_workout_type = None # None means normal, 'indoor' means recommend indoor
    warmup_extension_mins = 0
    
    if temp >= 35.0:
        recommendation = "Extreme Hot Weather: Recommend indoor workouts (Gym/Home) to prevent heat exhaustion. Limit outdoor cardio."
        warnings.append("High thermal index. Ensure hydration exceeds 3.5 Liters.")
        override_workout_type = "indoor"
    elif temp <= 13.0:
        recommendation = "Cold Weather: Recommend extending warm-up by 10 minutes to prevent muscle strains in cold joints."
        warmup_extension_mins = 10
    elif temp >= 30.0:
        recommendation = "Warm Weather: Moderate intensity outdoor workouts allowed, but schedule in early morning or late evening."
        
    return {
        "temperature_c": temp,
        "humidity": weather_data["humidity"],
        "air_quality": weather_data["air_quality"],
        "condition": weather_data["description"],
        "source": weather_data["source"],
        "recommendation": recommendation,
        "warnings": warnings,
        "override_workout_type": override_workout_type,
        "warmup_extension_mins": warmup_extension_mins
    }
