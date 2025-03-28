import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class WeatherAPI:
    """
    A class to fetch weather forecasts for a city within a date range.
    Uses OpenWeatherMap API by default.
    """
    
    def __init__(self):
        """
        Initialize the WeatherAPI with the API key from environment variables.
        Reads from WEATHER_API_KEY environment variable (can be set in .env file).
        """
        self.api_key = os.getenv("WEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set WEATHER_API_KEY environment variable in your .env file.")
        
        self.api_url = "https://api.openweathermap.org/data/2.5/forecast"
        self.max_forecast_days = 5  # OpenWeatherMap free tier is limited to 5 days
    
    def get_forecast(self, 
                     city: str, 
                     start_date: Optional[Union[str, datetime]] = None, 
                     end_date: Optional[Union[str, datetime]] = None, 
                     units: str = "metric") -> Dict[str, Any]:
        """
        Get weather forecast for a city within a date range.
        
        Args:
            city: Name of the city
            start_date: Start date (YYYY-MM-DD string or datetime object)
            end_date: End date (YYYY-MM-DD string or datetime object)
            units: Units of measurement ('metric' for Celsius, 'imperial' for Fahrenheit)
            
        Returns:
            Dict containing forecast data organized by date
            
        Raises:
            ValueError: If dates are invalid or range exceeds maximum
            requests.RequestException: If there's an error with the API request
        """
        # Process start date
        if start_date is None:
            start_date = datetime.now()
        elif isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        
        # Process end date
        if end_date is None:
            end_date = start_date
        elif isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Validate date range
        if end_date < start_date:
            raise ValueError("End date cannot be before start date")
        
        date_diff = (end_date - start_date).days + 1
        if date_diff > self.max_forecast_days:
            suggested_end = start_date + timedelta(days=self.max_forecast_days-1)
            raise ValueError(
                f"Date range exceeds maximum of {self.max_forecast_days} days. "
                f"OpenWeatherMap free tier is limited to 5-day forecast. "
                f"Suggested end date: {suggested_end.strftime('%Y-%m-%d')}"
            )
            
        # Format dates as strings for response
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
            
        # Make request to weather API
        params = {
            'q': city,
            'appid': self.api_key,
            'units': units
        }
        
        response = requests.get(self.api_url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        weather_data = response.json()
        
        # Extract forecast for the date range
        forecasts_by_date = {}
        
        for item in weather_data.get('list', []):
            forecast_date = datetime.fromtimestamp(item['dt'])
            forecast_date_str = forecast_date.strftime("%Y-%m-%d")
            
            # Check if the forecast date is within our requested range
            if (start_date.replace(hour=0, minute=0, second=0, microsecond=0) <= 
                forecast_date.replace(hour=0, minute=0, second=0, microsecond=0) <= 
                end_date.replace(hour=23, minute=59, second=59, microsecond=999)):
                
                # Initialize the list for this date if it doesn't exist
                if forecast_date_str not in forecasts_by_date:
                    forecasts_by_date[forecast_date_str] = []
                
                # Add the forecast for this time
                forecasts_by_date[forecast_date_str].append({
                    'time': forecast_date.strftime("%H:%M"),
                    'temperature': item['main']['temp'],
                    'feels_like': item['main']['feels_like'],
                    'humidity': item['main']['humidity'],
                    'description': item['weather'][0]['description'],
                    'wind_speed': item['wind']['speed'],
                    'icon': item['weather'][0]['icon']
                })
        
        # Prepare response
        result = {
            'city': city,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'forecasts': forecasts_by_date
        }
        
        return result
    
    def get_daily_summary(self, 
                          city: str, 
                          start_date: Optional[Union[str, datetime]] = None, 
                          end_date: Optional[Union[str, datetime]] = None, 
                          units: str = "metric") -> Dict[str, Any]:
        """
        Get a daily summary of weather forecasts instead of hourly forecasts.
        
        This method calls get_forecast() but then summarizes the data by day
        with min/max temperatures and aggregated weather conditions.
        
        Args:
            city: Name of the city
            start_date: Start date (YYYY-MM-DD string or datetime object)
            end_date: End date (YYYY-MM-DD string or datetime object)
            units: Units of measurement ('metric' for Celsius, 'imperial' for Fahrenheit)
            
        Returns:
            Dict containing summarized daily forecast data
        """
        # Get detailed forecast first
        detailed_forecast = self.get_forecast(city, start_date, end_date, units)
        
        # Prepare daily summary
        daily_summary = {
            'city': detailed_forecast['city'],
            'start_date': detailed_forecast['start_date'],
            'end_date': detailed_forecast['end_date'],
            'daily_forecasts': {}
        }
        
        for date, forecasts in detailed_forecast['forecasts'].items():
            if not forecasts:
                continue
                
            # Calculate daily statistics
            temperatures = [f['temperature'] for f in forecasts]
            descriptions = [f['description'] for f in forecasts]
            
            # Find most common weather description
            from collections import Counter
            most_common_description = Counter(descriptions).most_common(1)[0][0]
            
            # Find most representative weather icon (midday if available)
            midday_forecast = None
            for f in forecasts:
                if '12:' in f['time']:
                    midday_forecast = f
                    break
            
            # If no midday forecast, take the first one
            representative_icon = midday_forecast['icon'] if midday_forecast else forecasts[0]['icon']
            
            # Create daily summary
            daily_summary['daily_forecasts'][date] = {
                'min_temp': min(temperatures),
                'max_temp': max(temperatures),
                'avg_temp': sum(temperatures) / len(temperatures),
                'description': most_common_description,
                'icon': representative_icon,
                'forecast_count': len(forecasts)
            }
        
        return daily_summary


# Example usage
if __name__ == "__main__":
    # Create a WeatherAPI instance (uses API key from environment)
    weather_api = WeatherAPI()
    
    try:
        # Get hourly forecast for London for the next 3 days
        forecast = weather_api.get_forecast(
            city="London",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=2)
        )
        
        print(f"Weather forecast for {forecast['city']}")
        print(f"From {forecast['start_date']} to {forecast['end_date']}")
        
        for date, day_forecasts in forecast['forecasts'].items():
            print(f"\nDate: {date}")
            for f in day_forecasts:
                print(f"  {f['time']} - {f['temperature']}°C, {f['description']}")
        
        # Get daily summary
        daily = weather_api.get_daily_summary(
            city="London",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=2)
        )
        
        print("\n--- Daily Summary ---")
        for date, summary in daily['daily_forecasts'].items():
            print(f"\nDate: {date}")
            print(f"  Min/Max Temp: {summary['min_temp']}°C / {summary['max_temp']}°C")
            print(f"  Weather: {summary['description']}")
            
    except ValueError as e:
        print(f"Error: {e}")
    except requests.RequestException as e:
        print(f"API Request Error: {e}")