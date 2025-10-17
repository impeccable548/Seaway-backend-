from flask import Flask, jsonify, request
import requests
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# ====== CONFIG ======
OPENWEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# ====== HELPERS ======
def fetch_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        print(f"🔍 Fetching weather from: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        print("✅ Weather data received.")
        return {
            "city": data.get("name", city),
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"]
        }
    except Exception as e:
        print(f"❌ Weather API error: {e}")
        return {"error": str(e)}


def fetch_coordinates(location):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=1"
        print(f"🌍 Fetching coordinates from: {url}")
        response = requests.get(url, headers={"User-Agent": "SeawayApp/1.0"}, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data:
            raise ValueError("Location not found.")
        print("✅ Coordinates data received.")
        return {
            "display_name": data[0]["display_name"],
            "latitude": data[0]["lat"],
            "longitude": data[0]["lon"]
        }
    except Exception as e:
        print(f"❌ Coordinates API error: {e}")
        return {"error": str(e)}

# ====== ROUTES ======
@app.route("/")
def home():
    return jsonify({"message": "Seaway API is live 🌊"})


@app.route("/weather-map")
def weather_map():
    location = request.args.get("location", "")
    if not location:
        return jsonify({"error": "Missing location parameter"}), 400
    
    print(f"📍 Handling request for location: {location}")

    coords = fetch_coordinates(location)
    if "error" in coords:
        return jsonify({"error": f"Coordinates fetch failed: {coords['error']}"}), 500
    
    weather = fetch_weather(location)
    if "error" in weather:
        return jsonify({"error": f"Weather fetch failed: {weather['error']}"}), 500
    
    print("🚀 Successfully combined data.")
    return jsonify({
        "coordinates": coords,
        "weather": weather
    })


# ====== RUN SERVER ======
if __name__ == "__main__":
    # ✅ Important for Render to detect and bind to the right port
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)