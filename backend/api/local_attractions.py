import os
import json
import sys
import asyncio
import aiohttp
from typing import Dict, Optional, List
from dotenv import load_dotenv
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from api.flight_search_api import FlightSearchAPI
from api.hotels_api import HotelSearchAPI
class LocalAttractionsAPI:
    def __init__(self):
        """Initialize Local Attractions Search API"""
        load_dotenv()
        self.api_key = os.getenv('SERPAPI_KEY')
        self.base_url = 'https://serpapi.com/search'
        print(f"Initializing with API Key: {self.api_key[:4]}****")

    async def search_local_attractions(
        self, 
        city: str, 
        interests: Optional[List[str]] = None,
        max_results: int = 10
    ) -> Dict:
        """
        Search for local attractions using SerpAPI Google Search
        
        :param city: City to search for attractions
        :param interests: List of interests to filter attractions
        :param max_results: Maximum number of attractions to return
        :return: Dictionary of local attractions
        """
        try:
            # Prepare query parameters
            query = f"{city} top attractions"
            if interests:
                query += f" {' '.join(interests)}"

            params = {
                'engine': 'google',
                'q': query,
                'api_key': self.api_key,
                'num': max_results
            }

            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    # Read full response text
                    response_text = await response.text()
                    print(f"API Response Status: {response.status}")
                    
                    # Check response status
                    if response.status != 200:
                        return {
                            'error': 'Attractions search failed',
                            'status_code': response.status,
                            'response_text': response_text
                        }

                    # Parse response
                    try:
                        data = json.loads(response_text)
                    except json.JSONDecodeError:
                        return {
                            'error': 'Failed to parse JSON response',
                            'response_text': response_text
                        }

                    # Print available keys for debugging
                    print("Available keys in response:")
                    print(list(data.keys()))

                    # Extract attractions
                    attractions = []
                    
                    # Try different possible sources of attractions
                    organic_results = data.get('organic_results', [])
                    
                    for result in organic_results[:max_results]:
                        attraction = {
                            'name': result.get('title', 'Unknown Attraction'),
                            'description': result.get('snippet', 'No description available'),
                            'link': result.get('link', ''),
                        }
                        attractions.append(attraction)

                    # If no attractions found, return informative message
                    if not attractions:
                        return {
                            'error': 'No attractions found',
                            'city': city,
                            'interests': interests,
                            'response_keys': list(data.keys())
                        }

                    return {
                        'city': city,
                        'interests': interests,
                        'total_attractions': len(attractions),
                        'attractions': attractions
                    }

        except Exception as e:
            return {
                'error': str(e),
                'city': city,
                'interests': interests
            }

    async def invoke_local_attractions_search(
        self, 
        city: str, 
        interests: Optional[List[str]] = None,
        max_results: int = 10
    ) -> str:
        """
        Invoke local attractions search and return JSON string
        """
        try:
            # Perform attractions search
            attractions_results = await self.search_local_attractions(
                city, 
                interests, 
                max_results
            )
            
            # Convert to JSON string
            return json.dumps(attractions_results, indent=2)
        
        except Exception as e:
            # Return error as JSON string
            return json.dumps({
                'error': str(e),
                'city': city,
                'interests': interests
            }, indent=2)

# Allow direct script execution for testing
if __name__ == '__main__':
    async def main():
        api = LocalAttractionsAPI()
        
        # Test scenarios
        test_scenarios = [
            {
                'city': 'Paris',
                'interests': ['shopping', 'museums']
            },
            {
                'city': 'New York',
                'interests': ['art', 'food']
            }
        ]
        
        # Run test scenarios
        for scenario in test_scenarios:
            print("\nScenario:")
            print(json.dumps(scenario, indent=2))
            
            result = await api.invoke_local_attractions_search(
                scenario['city'],
                scenario.get('interests')
            )
            
            print("\nLocal Attractions Results:")
            print(result)

    asyncio.run(main())