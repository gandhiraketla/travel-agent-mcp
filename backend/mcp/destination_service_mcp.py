# destination_stdio_mcp.py
import sys
import os
import site
from typing import Dict, Optional, List

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from api.local_attractions import LocalAttractionsAPI
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
async def get_weather(city: str, date: str) -> str:
    """Get weather forecast for a city on a specific date."""
    # Hardcoded weather data
    weather_data = {
        "new york": {"condition": "Sunny", "temperature": "75°F", "precipitation": "10%"},
        "london": {"condition": "Rainy", "temperature": "62°F", "precipitation": "70%"},
        "tokyo": {"condition": "Cloudy", "temperature": "70°F", "precipitation": "30%"},
        "paris": {"condition": "Partly Cloudy", "temperature": "68°F", "precipitation": "20%"},
        "rome": {"condition": "Sunny", "temperature": "80°F", "precipitation": "5%"},
        "sydney": {"condition": "Clear", "temperature": "72°F", "precipitation": "0%"}
    }
    
    city_lower = city.lower()
    if city_lower in weather_data:
        result = {
            "city": city,
            "date": date,
            "forecast": weather_data[city_lower]
        }
    else:
        result = {
            "city": city,
            "date": date,
            "forecast": {"condition": "Sunny", "temperature": "70°F", "precipitation": "20%"}
        }
    
    return json.dumps(result, indent=2)

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