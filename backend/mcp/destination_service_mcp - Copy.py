# destination_stdio_mcp.py
import sys
import os
import site
import asyncio
from typing import Dict, Optional, Any, Union,List
from datetime import datetime, timedelta
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from api.local_attractions import LocalAttractionsAPI
from api.weather_api import WeatherAPI
# Add site-packages to path - use a more robust approach
try:
    # First attempt: Use site module
    site_packages = site.getsitepackages()[0]
    if site_packages not in sys.path:
        sys.path.append(site_packages)
except:
    # Fallback: Use hardcoded path if needed
    fallback_path = r'C:\travel-agent-mcp\venv\lib\site-packages'
    if os.path.exists(fallback_path) and fallback_path not in sys.path:
        sys.path.append(fallback_path)

# Add more explicit debugging
#print("Python executable:", sys.executable)
#print("Python path:", sys.path)

try:
    from mcp.server.fastmcp import FastMCP
    import json
    #print("Successfully imported FastMCP")
except ImportError as e:
    #print(f"Error importing FastMCP: {e}")
    # Try alternate import
    try:
        from fastmcp import FastMCP
        #print("Successfully imported from alternate path")
    except ImportError as e:
        #print(f"Alternate import also failed: {e}")
        sys.exit(1)

# Create the MCP server
mcp = FastMCP(name="DestinationServices",host="127.0.0.1",port=5000,timeout=30)

@mcp.tool()
async def get_weather(
    destination: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    format: str = "detailed",
    units: str = "metric"
) -> Dict[str, Any]:
    """
    Get weather forecast information for a specific city or destination and date range.
    
    This function provides weather forecast data for a specified location and time period.
    It can return either detailed hourly forecasts or simplified daily summaries.
    
    Args:
        destination (str): The name of the city or destination for which to get weather data.
                    Examples: "London", "New York", "Tokyo", "Paris, FR"
        
        start_date (str, optional): The start date for the forecast in YYYY-MM-DD format.
                                   If not provided, defaults to today's date.
                                   Example: "2025-03-28"
        
        end_date (str, optional): The end date for the forecast in YYYY-MM-DD format.
                                 If not provided, defaults to start_date.
                                 Must not be earlier than start_date.
                                 Maximum range is 5 days due to API limitations.
                                 Example: "2025-03-30"
        
        format (str, optional): The format of the forecast data.
                               Options:
                               - "detailed": Provides hourly forecasts for each day (default)
                               - "daily": Provides a summary for each day with min/max temperatures
        
        units (str, optional): The unit system for temperature and measurements.
                              Options:
                              - "metric": Temperature in Celsius, wind speed in meters/sec (default)
                              - "imperial": Temperature in Fahrenheit, wind speed in miles/hour
    
    Returns:
        Dict[str, Any]: A dictionary containing weather forecast data with the following structure:
            
            For format="detailed":
            {
                "destination": "London",
                "start_date": "2025-03-28",
                "end_date": "2025-03-30",
                "forecasts": {
                    "2025-03-28": [
                        {
                            "time": "12:00",
                            "temperature": 15.2,
                            "feels_like": 14.6,
                            "humidity": 76,
                            "description": "scattered clouds",
                            "wind_speed": 3.1,
                            "icon": "03d"
                        },
                        // Additional hourly forecasts...
                    ],
                    // Additional days...
                }
            }
            
            For format="daily":
            {
                "destination": "London",
                "start_date": "2025-03-28",
                "end_date": "2025-03-30",
                "daily_forecasts": {
                    "2025-03-28": {
                        "min_temp": 10.5,
                        "max_temp": 17.8,
                        "avg_temp": 14.2,
                        "description": "scattered clouds",
                        "icon": "03d",
                        "forecast_count": 8
                    },
                    // Additional days...
                }
            }
    
    Examples:
        # Get today's weather for London
        weather = await get_weather("London")
        
        # Get weather for New York for a specific date range
        weather = await get_weather("New York", "2025-03-28", "2025-03-30")
        
        # Get daily summary for Tokyo for the next 3 days
        today = datetime.now().strftime("%Y-%m-%d")
        end = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        weather = await get_weather("Tokyo", today, end, format="daily")
    """
    # Run the potentially blocking API call in a thread pool
    try:
        weather_api = WeatherAPI()
        
        # Use the appropriate method based on the requested format
        if format == "detailed":
            # Run in thread pool to avoid blocking the event loop
            result = await asyncio.to_thread(
                weather_api.get_forecast,
                city=destination,
                start_date=start_date,
                end_date=end_date,
                units=units
            )
        else:  # format == "daily"
            # Run in thread pool to avoid blocking the event loop
            result = await asyncio.to_thread(
                weather_api.get_daily_summary,
                city=destination,
                start_date=start_date,
                end_date=end_date,
                units=units
            )
        
        return result
    
    except ValueError as e:
        # Re-raise validation errors
        raise ValueError(str(e))
    
    except Exception as e:
        # Convert any other errors to a RuntimeError with descriptive message
        raise RuntimeError(f"Error retrieving weather data: {str(e)}")

@mcp.tool()
async def get_local_events(destination: str, interests: Optional[List[str]]) -> str:
    """
    Get information about local events and attractions in a specified destination based on interests.
    
    This function retrieves a list of events, attractions, and activities in the requested city,
    filtered by the user's specified interests if provided.
    
    Args:
        destination (str): The name of the city or location for which to get local events.
                    Examples: "London", "New York", "Tokyo", "Paris"
        
        interests (List[str], optional): A list of interest categories to filter events by.
                                         If not provided, returns events across all categories.
                                         Examples: ["music", "food", "sports", "art", "family"]
    
    Returns:
        str: A JSON string containing event information with the following structure:
            {
                "destination": "London",
                "events": [
                    {
                        "name": "Summer Festival",
                        "type": "music",
                        "description": "Annual music festival featuring local and international artists",
                        "date": "2025-07-15",
                        "location": "Hyde Park",
                        "price_range": "£30-75",
                        "booking_url": "https://example.com/tickets"
                    },
                    // Additional events...
                ],
                "attractions": [
                    {
                        "name": "British Museum",
                        "type": "art",
                        "description": "World-famous museum of art and antiquities",
                        "address": "Great Russell St, London WC1B 3DG",
                        "opening_hours": "10:00-17:00",
                        "admission": "Free"
                    },
                    // Additional attractions...
                ]
            }
    
    
    
    Examples:
        # Get all events in London
        events = await get_local_events("London", None)
        
        # Get only music and food events in New York
        events = await get_local_events("New York", ["music", "food"])
    """
    # Hardcoded events data
    result = await LocalAttractionsAPI().invoke_local_attractions_search(destination, interests)
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    print("Starting Destination Services MCP server with sse transport...")
    print("Available tools: get_weather, get_local_events")
    try:
        mcp.run(transport="sse")
        print("MCP server started")
    except Exception as e:
        #print(f"Error running MCP server: {e}",file=sys.stderr))
        import traceback
        print(traceback.format_exc())