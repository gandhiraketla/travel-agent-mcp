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
@mcp.tool()
async def get_weather(
    destination: str,
    start_date: str,
    end_date: str = None,
    format: str = "detailed",
    units: str = "metric"
) -> str:  # Change return type to str instead of Dict
    """
    Get weather forecast for a destination.
    
    Args:
        destination: City or location name
        start_date: Start date in YYYY-MM-DD format
        end_date: Optional end date (defaults to start_date)
        format: "detailed" or "daily"
        units: "metric" or "imperial"
    
    Returns:
        JSON string with weather forecast data
    """
    try:
        weather_api = WeatherAPI()
        
        if format == "detailed":
            result = await asyncio.to_thread(
                weather_api.get_forecast,
                city=destination,
                start_date=start_date,
                end_date=end_date or start_date,
                units=units
            )
        else:  # format == "daily"
            result = await asyncio.to_thread(
                weather_api.get_daily_summary,
                city=destination,
                start_date=start_date,
                end_date=end_date or start_date,
                units=units
            )
        
        # Convert dictionary to JSON string
        return json.dumps(result, indent=2)
    
    except Exception as e:
        error_result = {
            "error": f"Failed to get weather: {str(e)}",
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date or start_date
        }
        return json.dumps(error_result, indent=2)

@mcp.tool()
async def get_local_events(city: str, interests: Optional[List[str]]) -> str:
    """Get local events in a city on a specific date."""
    # Hardcoded events data
    result = await LocalAttractionsAPI().invoke_local_attractions_search(city, interests)
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