# travel_planner_agent.py
import sys
import os
import json
import asyncio
from typing import List, Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import AgentType, initialize_agent
from langchain_deepseek import ChatDeepSeek  # Correct import for Deepseek

# Get the path to the backend directory (parent directory)
backend_dir = Path(__file__).parent.parent.absolute()
env_path = backend_dir / '.env'

# Load environment variables from .env file in the backend directory
load_dotenv(dotenv_path=env_path)

# Disable LangSmith logging via environment variables
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_API_KEY"] = ""

def initialize_llm():
    """Initialize Deepseek LLM"""
    try:
        # Get API key from environment variables
        DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
        if not DEEPSEEK_API_KEY:
            print("⚠️ Warning: DEEPSEEK_API_KEY not found in environment variables.")
            return None
            
        # Set the API key in environment variable as expected by Deepseek
        os.environ["DEEPSEEK_API_KEY"] = DEEPSEEK_API_KEY
        
        llm = ChatDeepSeek(
            model="deepseek-chat",
            api_key=DEEPSEEK_API_KEY,  # Pass API key directly
            temperature=0.1
        )
        
        # Quick test
        print("Testing Deepseek connection...")
        response = llm.invoke("Reply with 'Deepseek Connection Successful!' if you can read this.")
        print(f"Deepseek test response: {response.content}")
        return llm
    except Exception as e:
        print(f"Failed to initialize Deepseek LLM: {str(e)}")
        return None

async def generate_travel_plan(
    origin: str,
    destination: str,
    start_date: str,
    end_date: str,
    travelers: int,
    budget: str,
    interests: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Generate a travel plan with the specified parameters, returning JSON output"""
    try:
        print("🔌 Connecting to MCP servers and loading tools...")
        print(f"Using .env file from: {env_path}")
        
        # Initialize the Deepseek LLM
        llm = initialize_llm()
        if not llm:
            return {"error": "Failed to initialize Deepseek LLM. Check your API key and connection."}
        
        # Get MCP server URLs from environment variables with fallbacks
        travel_server_url = os.getenv("TRAVEL_MCP_URL", "http://localhost:8000/sse")
        destination_server_url = os.getenv("DESTINATION_MCP_URL", "http://localhost:5000/sse")
        
        print(f"Travel server URL: {travel_server_url}")
        print(f"Destination server URL: {destination_server_url}")
        
        # Connect to both MCP servers
        async with MultiServerMCPClient(
            {
                "travel": {
                    "url": travel_server_url,
                    "transport": "sse",
                },
                "destination": {
                    "url": destination_server_url,
                    "transport": "sse",
                }
            }
        ) as client:
            # Get tools from both servers
            tools = client.get_tools()
            print(f"🧰 Loaded tools: {[tool.name for tool in tools]}")
            
            if not tools:
                return {"error": "Failed to load any tools from the MCP servers. Please check if servers are running properly."}
            
            # Create the agent using the STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION agent type
            agent_executor = initialize_agent(
                tools=tools,
                llm=llm,
                agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True
            )
            
            # Format interests as a string
            interests_str = ", ".join(interests) if interests else "general tourism"
            
            # Create the task for the agent, requesting JSON output
            user_input = f"""Create a comprehensive travel plan for a trip from {origin} to {destination}.
Travel dates: {start_date} to {end_date}
Number of travelers: {travelers}
Budget: {budget}
Interests: {interests_str}

Important instructions:
1. Use ALL available tools to gather complete information.
2. You MUST use only the tools provided by the MCP servers.
3. Return your final answer as a STRICT JSON format with these EXACT sections:
{json.dumps({
    "trip_summary": "A concise overview of the trip",
    "flights": [{"airline": "Airline Name", "flight_number": "ABC123", "departure_time": "2023-06-15T10:00:00", "arrival_time": "2023-06-15T14:30:00", "price": "$500"}],
    "accommodations": [{"name": "Hotel Name", "address": "123 Street, City", "price_per_night": "$200", "rating": "4.5/5"}],
    "weather": {"forecast": "Sunny with occasional clouds", "temperature": "25°C", "precipitation": "10%"},
    "local_events": [{"name": "Local Festival", "time": "2023-06-16T19:00:00", "category": "Cultural", "price": "Free"}],
    "itinerary": [{"day": 1, "date": "2023-06-15", "activities": [{"time": "10:00", "description": "Arrive and check into hotel", "location": "Airport/Hotel"}]}]
}, indent=2)}

Ensure the JSON is valid and matches the exact structure above. Do NOT use placeholders like "..." in the actual JSON.
"""
            
            print("📝 Preparing agent input...")
            print("🚀 Invoking agent with user request...")
            
            # Invoke the agent executor
            response = await agent_executor.ainvoke({"input": user_input})
            print("✅ Agent completed execution.")
            
            # Extract the output from the response
            if isinstance(response, dict):
                # If the response is already a dictionary, check for output or return directly
                output = response.get("output", response)
            else:
                output = str(response)
            
            # Try to parse the output as JSON
            try:
                # Check if the output is already a valid JSON dictionary
                if isinstance(output, dict):
                    travel_plan = output
                else:
                    # Try to find JSON in the output string
                    import re
                    json_match = re.search(r'```(?:json)?\s*([\s\S]+?)\s*```', output)
                    if json_match:
                        # JSON found in code block
                        json_str = json_match.group(1).strip()
                        travel_plan = json.loads(json_str)
                    else:
                        # Try to parse the entire output as JSON
                        travel_plan = json.loads(output)
                
                # Validate the travel plan structure
                required_keys = ["trip_summary", "flights", "accommodations", "weather", "local_events", "itinerary"]
                if not all(key in travel_plan for key in required_keys):
                    raise ValueError("Travel plan is missing required keys")
                
                print("📋 Travel plan JSON successfully extracted!")
                return travel_plan
            except (json.JSONDecodeError, ValueError) as e:
                # If JSON parsing fails, return the raw output in a structured format
                return {
                    "error": f"Failed to parse JSON output: {str(e)}",
                    "raw_output": output
                }
    
    except Exception as e:
        print(f"❌ Error generating travel plan: {e}")
        import traceback
        print(traceback.format_exc())
        return {
            "error": f"Failed to generate travel plan: {str(e)}",
            "status": "error"
        }

async def main():
    # Example usage - generate a travel plan
    travel_plan = await generate_travel_plan(
        origin="Dallas",
        destination="Bangalore",
        start_date="2025-06-15",
        end_date="2025-06-20",
        travelers=2,
        budget="Medium (around $3000 total)",
        interests=["Art", "History", "Food"]
    )
    
    # Print the result as formatted JSON
    print("\n===== TRAVEL PLAN JSON =====")
    print(json.dumps(travel_plan, indent=2))

if __name__ == "__main__":
    asyncio.run(main())