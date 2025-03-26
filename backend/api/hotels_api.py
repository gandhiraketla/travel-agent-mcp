import os
import json
import asyncio
import aiohttp
from typing import Dict, Optional
from dotenv import load_dotenv

class HotelSearchAPI:
    def __init__(self):
        """Initialize SerpAPI Google Hotels Search"""
        load_dotenv()
        self.api_key = os.getenv('SERPAPI_KEY')
        self.base_url = 'https://serpapi.com/search'

    async def search_hotels(
        self, 
        city: str, 
        check_in_date: str, 
        check_out_date: str, 
        guests: int = 2, 
        max_price: Optional[int] = None
    ) -> Dict:
        """Search for hotels using SerpAPI Google Hotels"""
        try:
            # Prepare query parameters
            params = {
                'engine': 'google_hotels',
                'q': f'{city} Resorts',
                'check_in_date': check_in_date,
                'check_out_date': check_out_date,
                'adults': guests,
                'currency': 'USD',
                'gl': 'us',
                'hl': 'en',
                'api_key': self.api_key
            }

            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status != 200:
                        return {
                            'error': 'Hotel search failed',
                            'status_code': response.status
                        }

                    # Parse response
                    data = await response.json()
                    
                    # Transform hotel data
                    hotel_options = []
                    for property_data in data.get('properties', []):
                        hotel_option = {
                            'name': property_data.get('name', 'Unknown Hotel'),
                            'description': property_data.get('description', 'No description available'),
                            'price_per_night': property_data.get('rate_per_night', {}).get('lowest', 'N/A'),
                            'rating': property_data.get('overall_rating', 0),
                            'amenities': property_data.get('amenities', [])[:5],
                            'hotel_class': property_data.get('hotel_class', 'Unrated')
                        }
                        hotel_options.append(hotel_option)
                    
                    return {
                        'city': city,
                        'check_in_date': check_in_date,
                        'check_out_date': check_out_date,
                        'guests': guests,
                        'options': hotel_options
                    }

        except Exception as e:
            return {
                'error': str(e),
                'city': city,
                'check_in_date': check_in_date,
                'check_out_date': check_out_date
            }

    async def invoke_hotel_search(
        self, 
        city: str, 
        check_in_date: str, 
        check_out_date: str, 
        guests: int = 2, 
        max_price: Optional[int] = None
    ) -> str:
        """Invoke hotel search and return JSON string"""
        try:
            # Perform hotel search
            hotel_results = await self.search_hotels(
                city, 
                check_in_date, 
                check_out_date, 
                guests, 
                max_price
            )
            
            # Convert to JSON string
            return json.dumps(hotel_results, indent=2)
        
        except Exception as e:
            # Return error as JSON string
            return json.dumps({
                'error': str(e),
                'city': city,
                'check_in_date': check_in_date,
                'check_out_date': check_out_date
            }, indent=2)

# Allow direct script execution for testing
if __name__ == '__main__':
    async def main():
        api = HotelSearchAPI()
        result = await api.invoke_hotel_search(
            'Bangalore', 
            '2025-03-27', 
            '2025-03-28'
        )
        print(result)

    asyncio.run(main())