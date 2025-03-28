import streamlit as st
import requests
from datetime import date, timedelta
import json

# Set page configuration FIRST - this MUST be the first Streamlit command
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide"
)

def call_travel_planner_api(origin, destination, start_date, end_date, travelers, budget, interests):
    """
    Call the Travel Planner API
    """
    url = "http://localhost:8001/generate-travel-plan"  # Update with your API endpoint
    
    payload = {
        "origin": origin,
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "travelers": travelers,
        "budget": budget,
        "interests": interests
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an exception for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling API: {e}")
        return None

def display_trip_summary(travel_plan):
    """
    Display the travel plan in a formatted manner
    """
    # Custom CSS for styling
    st.markdown("""
    <style>
    .travel-plan-section {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    h2 {
        color: #2c3e50;
        border-bottom: 2px solid #3494E6;
        padding-bottom: 10px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Trip Summary Section
    st.markdown('<div class="travel-plan-section">', unsafe_allow_html=True)
    st.subheader("✈️ Trip Summary")
    st.write(travel_plan.get('trip_summary', 'No summary available'))
    st.markdown('</div>', unsafe_allow_html=True)

    # Flights Section
    st.markdown('<div class="travel-plan-section">', unsafe_allow_html=True)
    st.subheader("🛫 Flights")
    flights = travel_plan.get('flights', [])
    for flight in flights:
        st.markdown(f"""
        **{flight.get('airline', 'Unknown Airline')}** - Flight {flight.get('flight_number', 'N/A')}
        - **Departure:** {flight.get('departure_time', 'N/A')}
        - **Arrival:** {flight.get('arrival_time', 'N/A')}
        - **Price:** {flight.get('price', 'N/A')}
        """)
    st.markdown('</div>', unsafe_allow_html=True)

    # Accommodations Section
    st.markdown('<div class="travel-plan-section">', unsafe_allow_html=True)
    st.subheader("🏨 Accommodations")
    accommodations = travel_plan.get('accommodations', [])
    for accommodation in accommodations:
        st.markdown(f"""
        **{accommodation.get('name', 'Unknown Hotel')}**
        - **Address:** {accommodation.get('address', 'N/A')}
        - **Price per Night:** {accommodation.get('price_per_night', 'N/A')}
        - **Rating:** {accommodation.get('rating', 'N/A')}
        """)
    st.markdown('</div>', unsafe_allow_html=True)

    # Weather Section
    st.markdown('<div class="travel-plan-section">', unsafe_allow_html=True)
    st.subheader("☀️ Weather Forecast")
    weather = travel_plan.get('weather', {})
    st.markdown(f"""
    - **Forecast:** {weather.get('forecast', 'N/A')}
    - **Temperature:** {weather.get('temperature', 'N/A')}
    - **Precipitation:** {weather.get('precipitation', 'N/A')}
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    # Local Events Section
    st.markdown('<div class="travel-plan-section">', unsafe_allow_html=True)
    st.subheader("🎉 Local Events")
    local_events = travel_plan.get('local_events', [])
    for event in local_events:
        st.markdown(f"""
        **{event.get('name', 'Unknown Event')}**
        - **Time:** {event.get('time', 'N/A')}
        - **Category:** {event.get('category', 'N/A')}
        - **Price:** {event.get('price', 'N/A')}
        """)
    st.markdown('</div>', unsafe_allow_html=True)

    # Detailed Itinerary Section
    st.markdown('<div class="travel-plan-section">', unsafe_allow_html=True)
    st.subheader("📅 Detailed Itinerary")
    itinerary = travel_plan.get('itinerary', [])
    for day in itinerary:
        st.markdown(f"**Day {day.get('day', 'N/A')} - {day.get('date', 'N/A')}**")
        activities = day.get('activities', [])
        for activity in activities:
            st.markdown(f"- **{activity.get('time', 'N/A')}:** {activity.get('description', 'N/A')} at {activity.get('location', 'N/A')}")
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Custom CSS for overall styling
    st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    h1 {
        color: #2c3e50;
        text-align: center;
        font-weight: 700;
        margin-bottom: 30px;
        background: linear-gradient(90deg, #3494E6, #2c3e50);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stTextInput > div > div > input, 
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div > select {
        background-color: white;
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: border-color 0.3s ease;
    }
    
    .stButton > button {
        background-color: #3494E6;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #2c3e50;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

    # Title with gradient
    st.markdown("<h1>🌍 GlobeGenie</h1>", unsafe_allow_html=True)
    
    # Subtitle
    st.markdown(
        "<p style='text-align: center; color: #7f8c8d;'>"
        "Craft your perfect journey with intelligent, personalized travel planning"
        "</p>", 
        unsafe_allow_html=True
    )
    
    # Main content area with card-like styling
    st.markdown('<div class="travel-plan-section">', unsafe_allow_html=True)
    
    # Create columns for input
    col1, col2 = st.columns(2)
    
    with col1:
        # Origin input
        origin = st.text_input("Origin", placeholder="e.g., Dallas")
        
        # Start Date input
        start_date = st.date_input("Start Date", min_value=date.today())
        
        # Number of Travelers
        travelers = st.number_input("Number of Travelers", min_value=1, max_value=10, value=2)
    
    with col2:
        # Destination input
        destination = st.text_input("Destination", placeholder="e.g., Bangalore")
        
        # End Date input
        end_date = st.date_input("End Date", min_value=start_date + timedelta(days=1))
        
        # Budget selection
        budget = st.selectbox("Budget", ["Low", "Medium", "High"])
    
    # Interests multi-select
    interests = st.multiselect(
        "Interests",
        ["Art", "History", "Food", "Shopping", "Nature", "Culture", "Adventure", "Relaxation"]
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Generate Plan button
    col_button = st.columns(3)
    with col_button[1]:
        if st.button("Generate Travel Plan", use_container_width=True):
            # Validate inputs
            if not origin or not destination:
                st.error("Please enter both Origin and Destination")
                return
            
            # Show loading spinner
            with st.spinner("Crafting your personalized travel experience..."):
                # Call API
                travel_plan = call_travel_planner_api(
                    origin, 
                    destination, 
                    start_date.strftime("%Y-%m-%d"), 
                    end_date.strftime("%Y-%m-%d"), 
                    travelers, 
                    budget, 
                    interests
                )
            
            # Display results
            if travel_plan:
                # Check for error in response
                if 'error' in travel_plan:
                    st.error(f"Error: {travel_plan.get('error', 'Unknown error')}")
                else:
                    # Display formatted travel plan
                    display_trip_summary(travel_plan)
            else:
                st.error("Failed to generate travel plan. Please try again.")

if __name__ == "__main__":
    main()