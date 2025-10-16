from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from functools import lru_cache
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# ====== CONFIG ======
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")  # From .env or Render environment
# ===================

# ====== CACHING ======
@lru_cache(maxsize=10)
def fetch_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "city": data.get("name"),
                "temperature": data["main"].get("temp"),
                "humidity": data["main"].get("humidity"),
                "description": data["weather"][0].get("description")
            }
        else:
            return {"error": f"OpenWeatherMap failed for '{city}'"}
    except Exception as e:
        return {"error": f"Weather API error: {str(e)}"}

@lru_cache(maxsize=10)
def fetch_coordinates(location):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": location, "format": "json"}
    headers = {"User-Agent": "MyWeatherApp/1.0"}  # Required by Nominatim
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()
        if data:
            coords = data[0]
            return {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "display_name": coords["display_name"]
            }
        else:
            return {"error": f"No coordinates found for '{location}'"}
    except Exception as e:
        return {"error": f"Map API error: {str(e)}"}

# ====== ROUTES ======
@app.route("/weather")
def weather_route():
    city = request.args.get("city", "Lagos")
    return jsonify(fetch_weather(city))

@app.route("/map")
def map_route():
    location = request.args.get("location", "Lagos")
    return jsonify(fetch_coordinates(location))

@app.route("/weather-map")
def weather_map_route():
    location = request.args.get("location", "Lagos")
    weather = fetch_weather(location)
    coords = fetch_coordinates(location)
    return jsonify({"weather": weather, "coordinates": coords})

# ====== RUN SERVER ======
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)