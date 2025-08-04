from google.adk.mcp import Model, Context, Protocol
from google.adk.agents import Agent
from datetime import datetime, UTC
from typing import Dict, Optional, Union
import requests
import os
from dotenv import load_dotenv
load_dotenv()

class WeatherTimeModel(Model):
    """Model layer handling business logic"""
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        
    async def get_weather(self, city: str) -> Dict:
        """Get weather data for a city"""
        response = await self._make_request("weather", {"city": city})
        return response
        
    async def get_time(self, city: str) -> Dict:
        """Get time data for a city"""
        response = await self._make_request("time", {"city": city})
        return response

class WeatherTimeAgent(Agent):
    def __init__(self):
        super().__init__(
            name="weather_time_agent",
            description="Get current weather and time information for a city"
        )
        self.model = WeatherTimeModel()
        self.context = Context()
        self.protocol = Protocol()

    async def process(self, request: Dict) -> Dict:
        """Process incoming requests using MCP pattern"""
        city = request.get('city')
        
        # Store city in context
        self.context.set('last_city', city)
        
        # Get data through model
        weather_data = await self.model.get_weather(city)
        time_data = await self.model.get_time(city)
        
        # Format response using protocol
        return self.protocol.format_response({
            'weather': weather_data,
            'time': time_data,
            'city': city
        })

    def validate_city(self, city: str) -> Optional[str]:
        """Validate city input"""
        if not city or not city.strip():
            return "Error: City name cannot be empty"
        return None

if __name__ == "__main__":
    agent = WeatherTimeAgent()
    
    print("\nWeather & Time Information Agent (MCP Version)")
    print("----------------------------------------")
    
    
    while True:
        city = input("\nEnter a city name (or 'exit' to quit): ")
        if city.lower() == 'exit':
            break
            
        result = agent.process({'city': city})
        print(result)