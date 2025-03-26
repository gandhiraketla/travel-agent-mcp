# 🌍 Globe Genie -AI-Powered Travel Companion

## Project Overview

This AI-Powered Travel Companion is an intelligent travel planning application that leverages multiple APIs and microservices to create personalized travel experiences. The project uses a microservice-based architecture with separate services for travel planning, destination information, and a user-friendly Streamlit interface.

## 🛠 Prerequisites

### Python Version
- Python 3.8 or higher recommended

### API Keys
You'll need to obtain the following API keys:

1. **Amadeus API**
   - Website: [Amadeus Developer Portal](https://developers.amadeus.com/)
   - Steps to get API key:
     1. Create an account on the Amadeus Developer Portal
     2. Navigate to the "Get Started" or "Create an App" section
     3. Generate credentials for Flight and Hotel Search APIs

2. **SerpAPI**
   - Website: [SerpAPI](https://serpapi.com/)
   - Steps to get API key:
     1. Sign up for a free account
     2. Go to the dashboard
     3. Find your API key in the credentials section

3. **Deepseek API**
   - Website: [Deepseek AI](https://platform.deepseek.com/)
   - Steps to get API key:
     1. Create an account on the Deepseek platform
     2. Navigate to API settings or developer section
     3. Generate a new API key

## 🚀 Setup and Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/travel-mcp-server.git
cd travel-mcp-server
```

### 2. Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the `backend` directory with the following content:
```
AMADEUS_CLIENT_ID=your_amadeus_client_id
AMADEUS_CLIENT_SECRET=your_amadeus_client_secret
SERPAPI_KEY=your_serpapi_key
DEEPSEEK_API_KEY=your_deepseek_api_key
```

## 🖥️ Running the Application

Open three separate terminal windows:

### Terminal 1: Travel MCP Server
```bash
cd backend/mcp
python travel_mcp_server.py
```

### Terminal 2: Destination Service MCP Server
```bash
cd backend/mcp
python destination_service_mcp.py
```

### Terminal 3: Streamlit UI
```bash
cd backend/ui
streamlit run travel_planner_streamlit.py
```

## 🔍 Project Structure
```
travel-mcp-server/
│
├── backend/
│   ├── api/
│   │   ├── flight_search_api.py
│   │   ├── hotels_api.py
│   │   └── local_attractions_api.py
│   │
│   ├── mcp/
│   │   ├── travel_mcp_server.py
│   │   └── destination_service_mcp.py
│   │
│   └── ui/
│       └── travel_planner_streamlit.py
│
├── requirements.txt
└── README.md
```

## 🤝 Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🛡️ Limitations
- API usage is subject to rate limits and pricing of respective services
- Travel recommendations are AI-generated and should be verified independently

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

## 📧 Contact
LInkedIn : https://www.linkedin.com/in/gandhi77/