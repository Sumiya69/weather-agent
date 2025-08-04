from fastapi import FastAPI, HTTPException
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, UTC
from typing import Optional

# Load environment variables
load_dotenv()

app = FastAPI(title="Weather & Time MCP Server") 

# Get API key from environment variable
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == 'YOUR_API_KEY':
    print("Warning: Valid OPENWEATHER_API_KEY not found in environment variables!")
    print("Please add your OpenWeatherMap API key to the .env file.")

@app.get("/weather")
async def get_weather(city: str):
    """Get weather information for a given city using OpenWeatherMap API."""
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == 'YOUR_API_KEY':
        raise HTTPException(
            status_code=500,
            detail="OpenWeatherMap API key not configured. Please add a valid API key to the .env file."
        )
        
    try:
        response = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        )
        
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"City '{city}' not found")
            
        response.raise_for_status()
        data = response.json()
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        feels_like = data['main']['feels_like']
        
        return {
            "result": f"In {city}, it's {weather} with {temp}°C (feels like {feels_like}°C) and {humidity}% humidity.",
            "data": {
                "city": city,
                "weather": weather,
                "temperature": temp,
                "feels_like": feels_like,
                "humidity": humidity
            }
        }
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Could not fetch weather: {str(e)}")

@app.get("/time")
async def get_time(city: str):
    """Get current time information for a city."""
    try:
        # For now, we'll use UTC time and add timezone support later
        current_time = datetime.now(UTC)
        
        # Get city coordinates for future timezone support
        geo_response = requests.get(
            f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={OPENWEATHER_API_KEY}"
        )
        
        geo_data = geo_response.json()
        if not geo_data:
            raise HTTPException(status_code=404, detail=f"City '{city}' not found")
            
        location = geo_data[0]
        lat, lon = location['lat'], location['lon']
        
        return {
            "result": f"The current time in {city} is: {current_time.isoformat()} (UTC)",
            "data": {
                "city": city,
                "datetime": current_time.isoformat(),
                "timezone": "UTC",
                "coordinates": {
                    "latitude": lat,
                    "longitude": lon
                }
            }
        }
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Could not fetch city information: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint that describes the API."""
    return {
        "name": "Weather & Time MCP Server",
        "version": "1.0.0",
        "description": "An MCP server providing weather and time information for cities worldwide",
        "endpoints": [
            {
                "path": "/weather",
                "params": ["city"],
                "description": "Get current weather information for a city"
            },
            {
                "path": "/time",
                "params": ["city"],
                "description": "Get current time information for a city (currently UTC)"
            }
        ],
        "status": "running"
    }
