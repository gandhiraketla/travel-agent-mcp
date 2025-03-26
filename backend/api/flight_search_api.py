import os
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Optional
from dotenv import load_dotenv

class FlightSearchAPI:
    def __init__(self, api_type='amadeus'):
        """
        Initialize Flight Search API
        
        :param api_type: Type of flight search API (default: amadeus)
        """
        # Load environment variables
        load_dotenv()
        
        # Amadeus API credentials
        self.client_id = os.getenv('AMADEUS_CLIENT_ID')
        self.client_secret = os.getenv('AMADEUS_CLIENT_SECRET')
        
        # API configuration
        self.api_type = api_type
        self.access_token = None
        self.token_expiry = None
        
        # Base URLs
        self.base_url = 'https://test.api.amadeus.com/v2'
        self.auth_url = 'https://test.api.amadeus.com/v1/security/oauth2/token'

    async def _get_access_token(self):
        """
        Obtain access token from Amadeus API
        
        :return: Access token string
        """
        # Check if current token is still valid
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token

        async with aiohttp.ClientSession() as session:
            payload = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            async with session.post(self.auth_url, data=payload) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data['access_token']
                    # Set token expiry (typically 30 minutes for Amadeus)
                    self.token_expiry = datetime.now() + timedelta(minutes=25)
                    return self.access_token
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to obtain access token: {error_text}")

    def _get_airline_name(self, airline_code: str) -> str:
        """
        Convert airline code to full airline name
        
        :param airline_code: 2-letter IATA airline code
        :return: Full airline name
        """
        airline_mapping = {
            # Most common international airlines
            '6X': 'Cape Air',
            'AA': 'American Airlines',
            'AC': 'Air Canada',
            'AF': 'Air France',
            'BA': 'British Airways',
            'DL': 'Delta Air Lines',
            'EK': 'Emirates',
            'KL': 'KLM Royal Dutch Airlines',
            'LH': 'Lufthansa',
            'QF': 'Qantas',
            'QR': 'Qatar Airways',
            'UA': 'United Airlines',
            'US': 'US Airways',
            'WN': 'Southwest Airlines',
            
            # Additional airlines
            '9W': 'Jet Airways',
            'AI': 'Air India',
            'SQ': 'Singapore Airlines',
            'CX': 'Cathay Pacific',
            'EY': 'Etihad Airways',
            'MH': 'Malaysia Airlines',
            'TK': 'Turkish Airlines',
            'AY': 'Finnair',
            'IB': 'Iberia',
            'JL': 'Japan Airlines',
            'KE': 'Korean Air',
            'PR': 'Philippine Airlines',
            'TG': 'Thai Airways',
        }
        
        # Return full airline name or default to code + 'Airlines'
        return airline_mapping.get(airline_code, f'{airline_code} Airlines')

    async def search_flights(
        self, 
        origin: str, 
        destination: str, 
        departure_date: str, 
        return_date: Optional[str] = None,
        passengers: int = 1
    ) -> Dict:
        """
        Search for flight options using Amadeus Flight Offers Search API
        
        :param origin: Airport code
        :param destination: Airport code
        :param departure_date: Date in YYYY-MM-DD format
        :param return_date: Optional return date in YYYY-MM-DD format
        :param passengers: Number of passengers
        :return: Dictionary of flight options
        """
        try:
            # Get access token
            access_token = await self._get_access_token()

            # Prepare headers and parameters
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'originLocationCode': origin,
                'destinationLocationCode': destination,
                'departureDate': departure_date,
                'adults': passengers,
                'max': 10  # Limit to 10 flight options
            }

            # Add return date if provided (round trip)
            if return_date:
                params['returnDate'] = return_date

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{self.base_url}/shopping/flight-offers', 
                    headers=headers, 
                    params=params
                ) as response:
                    if response.status == 200:
                        flight_data = await response.json()
                        
                        # Transform Amadeus API response to our desired format
                        flight_options = []
                        for offer in flight_data.get('data', []):
                            flight_option = self._transform_flight_offer(offer)
                            flight_options.append(flight_option)
                        
                        return {
                            'origin': origin,
                            'destination': destination,
                            'departure_date': departure_date,
                            'return_date': return_date,
                            'passengers': passengers,
                            'options': flight_options
                        }
                    else:
                        error_text = await response.text()
                        raise Exception(f"Flight search failed: {error_text}")

        except Exception as e:
            return {
                'error': str(e),
                'origin': origin,
                'destination': destination,
                'departure_date': departure_date,
                'return_date': return_date
            }

    def _transform_flight_offer(self, offer: Dict) -> Dict:
        """
        Transform Amadeus flight offer to our standard format
        
        :param offer: Raw Amadeus flight offer
        :return: Transformed flight option dictionary
        """
        # Extract first itinerary (simplification)
        first_itinerary = offer.get('itineraries', [{}])[0]
        
        # Determine lowest price
        price = offer.get('price', {}).get('total', 'N/A')
        
        # Get first segment details
        segments = first_itinerary.get('segments', [{}])
        first_segment = segments[0]
        
        # Get airline code and convert to name
        airline_code = first_segment.get('carrierCode', 'Unknown')
        airline_name = self._get_airline_name(airline_code)
        
        return {
            'airline': airline_name,  # Ensure airline name is used
            'flight_number': first_segment.get('number', 'N/A'),
            'departure_time': first_segment.get('departure', {}).get('at', 'N/A'),
            'arrival_time': first_segment.get('arrival', {}).get('at', 'N/A'),
            'price': f'${price}',
            'class': offer.get('class', ['Economy'])[0]
        }

    async def invoke_flight_search(
        self, 
        origin: str, 
        destination: str, 
        departure_date: str, 
        return_date: Optional[str] = None,
        passengers: int = 1
    ) -> str:
        """
        Invoke flight search and return JSON string
        
        :param origin: Origin airport code
        :param destination: Destination airport code
        :param departure_date: Departure date
        :param return_date: Optional return date
        :param passengers: Number of passengers
        :return: JSON string of flight options
        """
        try:
            # Perform flight search
            flight_results = await self.search_flights(
                origin, 
                destination, 
                departure_date, 
                return_date, 
                passengers
            )
            
            # Convert to JSON string
            return json.dumps(flight_results, indent=2)
        
        except Exception as e:
            # Return error as JSON string
            return json.dumps({
                'error': str(e),
                'origin': origin,
                'destination': destination,
                'departure_date': departure_date
            }, indent=2)

    @classmethod
    def main(cls):
        """
        Main method for local testing of flight search
        """
        async def run_test():
            # Create API instance
            api = cls()
            
            # Test flight search
            print("Testing Flight Search API...")
            
            # Define test scenarios
            test_scenarios = [
                {
                    'origin': 'DFW',
                    'destination': 'BLR',
                    'departure_date': '2025-07-15',
                    'passengers': 2
                }
            ]
            
            # Run test scenarios
            for scenario in test_scenarios:
                print("\nScenario:")
                print(json.dumps(scenario, indent=2))
                
                try:
                    # Invoke flight search
                    result = await api.invoke_flight_search(
                        scenario['origin'],
                        scenario['destination'],
                        scenario['departure_date'],
                        scenario.get('return_date'),
                        scenario.get('passengers', 1)
                    )
                    
                    # Print results
                    print("\nFlight Search Results:")
                    print(result)
                
                except Exception as e:
                    print(f"Error in scenario: {e}")

        # Run async test
        asyncio.run(run_test())

# Allow direct script execution for testing
if __name__ == '__main__':
    print("Initializing Flight Search API Local Testing...")
    FlightSearchAPI.main()