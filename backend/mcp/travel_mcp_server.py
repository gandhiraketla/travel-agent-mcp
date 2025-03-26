# travel_mcp.py
import sys
import site
import os
# Get the site-packages directory dynamically
site_packages = site.getsitepackages()[0]
if site_packages not in sys.path:
    sys.path.append(site_packages)

from mcp.server.fastmcp import FastMCP
import json
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from api.flight_search_api import FlightSearchAPI
from api.hotels_api import HotelSearchAPI
# Create the MCP server
mcp = FastMCP("TravelServices")

@mcp.tool()
async def get_flights(origin: str, destination: str, departure_date: str, return_date: str = None, passengers: int = 1) -> str:
    """
    Get available flights between two cities for specified dates.
    
    This tool searches for flight options based on the provided parameters.
    
    Parameters:
    -----------
    origin : str
        The departure city or airport code (e.g., 'New York' or 'JFK')
    destination : str
        The arrival city or airport code (e.g., 'Paris' or 'CDG')
    departure_date : str
        The departure date in 'YYYY-MM-DD' format
    return_date : str, optional
        The return date in 'YYYY-MM-DD' format. If not provided, one-way flights will be returned.
    passengers : int, optional
        Number of passengers, default is 1
        
    Returns:
    --------
    str
        A JSON string containing flight options with information about airlines, 
        flight numbers, departure/arrival times, prices, and available classes.
    """
    flight_api = FlightSearchAPI()
    # Invoke flight search
    result = await flight_api.invoke_flight_search(
        origin, 
        destination, 
        departure_date, 
        return_date, 
        passengers
    )
    print(result)
    return result
    # Hardcoded flight options
    

@mcp.tool()
async def get_hotels(city: str, check_in_date: str, check_out_date: str, guests: int = 2, max_price: int = None) -> str:
    """
    Get available hotels in a city for the specified dates.
    
    This tool searches for hotel options based on the provided parameters.
    
    Parameters:
    -----------
    city : str
        The city name where you want to find accommodation (e.g., 'Paris', 'New York')
    check_in_date : str
        The check-in date in 'YYYY-MM-DD' format
    check_out_date : str
        The check-out date in 'YYYY-MM-DD' format
    guests : int, optional
        Number of guests, default is 2
    max_price : int, optional
        Maximum price per night in USD. If not provided, all price ranges will be included.
        
    Returns:
    --------
    str
        A JSON string containing hotel options with information about names,
        addresses, prices, ratings, and available amenities.
    """
    # Hardcoded hotel options
    api = HotelSearchAPI()
    result = await api.invoke_hotel_search(
            city, 
            check_in_date, 
            check_out_date
        )
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    print("Starting Travel Services MCP server on port 8000...")
    print("Available tools: get_flights, get_hotels")
    mcp.run(transport="sse")
    print("MCP server started")