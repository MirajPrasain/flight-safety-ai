# 🛫 AirPilot — AI Copilot for Crash Prevention

> An AI-driven system that simulates real aircraft incidents and generates life-saving advice — powered by MongoDB, LangChain, and Google Cloud.

---

## 🌍 Problem

Every year, hundreds of lives are lost due to preventable aircraft incidents. Human error, miscommunication, and slow reaction times are often contributing factors. What if AI could provide real-time, actionable pilot guidance during those moments?

---

## 💡 Solution

**AirPilot** simulates 5 real-world aviation crashes using historical data stored in MongoDB and generates AI-driven pilot advice that could have changed the outcome.

- 🧠 LangChain + LLM-generated recommendations
- 📊 MongoDB stores detailed crash data
- 🗣️ Voice Agent delivers real-time cockpit instructions
- ☁️ Designed to run on Google Cloud

---

## 🚁 Features

### Real-time AI Copilot
- **Emergency Advisor**: Provides immediate, actionable advice during critical flight situations
- **Risk Explanation**: Explains why flight situations are unsafe with detailed analysis
- **Pilot Chat Interface**: Natural language interaction with AI copilot
- **Historical Crash Reference**: References past incidents to provide context-aware advice
- **Intent Classification**: Automatically routes messages to appropriate specialized handlers

### Intent-Based Routing System
- **Emergency Intent**: Highest priority for critical situations (mayday, terrain alerts, system failures)
- **Divert Airport Intent**: Airport diversion and landing recommendations
- **Similar Crashes Intent**: Historical incident analysis and lessons learned
- **System Status Intent**: Instrument checks and system health monitoring
- **Status Update Intent**: General flight status and situational awareness

### Flight Simulations
- **KAL801**: Korean Air Flight 801 - Terrain proximity and glide slope issues
- **CRASH_KAL801**: Historical Korean Air Flight 801 (1997 Guam crash) - 229 fatalities, 25 survivors
- **TURKISH1951**: Turkish Airlines Flight 1951 - Radio altimeter and autopilot failures
- **ASIANA214**: Asiana Airlines Flight 214 - Low-speed approach and landing gear issues

### AI Capabilities
- **Flight-Specific Responses**: Tailored advice based on historical crash patterns
- **Emergency Keyword Detection**: Monitors for critical terms like "terrain", "glideslope", "autopilot"
- **Similarity Search**: Finds relevant historical incidents using vector embeddings
- **Typewriter Effect**: Smooth AI message animation in chat interface
- **Modular LangChain Chains**: Specialized prompts for different intents and flight scenarios

---

## 🛠 Tech Stack

| Layer       | Tools |
|-------------|-------|
| Frontend    | React.js with modern UI components |
| Backend     | FastAPI |
| AI Chains   | LangChain + Gemma 2B (hackathon restriction) |
| Voice Agent | ElevenLabs TTS + Web Speech API |
| Database    | MongoDB Atlas |
| Cloud       | Google Cloud (App Engine / Cloud Run) |

> **Note**: Due to hackathon restrictions, we are limited to using LangChain with Gemma 2B model. Other LLM models are not permitted for this competition.

---

## 📂 Project Structure

AirPilot/
├── backend/
│ ├── main.py # FastAPI backend entry
│ ├── models.py # Pydantic schemas
│ ├── database.py # MongoDB connection
│ ├── langchain_utils.py # LangChain chains & prompt logic
│ └── config.py # Secrets, constants
├── demo_cli.py # CLI to simulate flight scenarios
├── requirements.txt
├── .gitignore
├── .env (ignored)
├── README.md



---

## 🧪 How to Run

1. Clone the repo:
```bash
git clone https://github.com/YOUR_USERNAME/AirPilot.git
cd AirPilot
```

## 🏗️ Architecture

### Backend (FastAPI + MongoDB)
- **LangChain Integration**: Uses Ollama with "gemma:2b" model for local inference (hackathon requirement)
- **Vector Search**: Sentence transformers for semantic similarity matching
- **Real-time Processing**: 15-second timeout with fallback responses
- **CORS Support**: Configured for React frontend integration

### Frontend (React)
- **Chat Interface**: Interactive flight simulation at `/chat/:flightId`
- **Flight Selection**: Dropdown with historical crash scenarios
- **Responsive Design**: Modern UI with emergency-themed styling
- **Real-time Updates**: Live chat with AI copilot responses
- **Voice Integration**: ElevenLabs TTS with fallback to Web Speech API

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB
- Ollama with "gemma:2b" model (required for hackathon compliance)

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Store Historical Crash Data
```bash
python store_kal801_data.py
```

## 📊 Korean Air Flight 801 Integration

The system now includes comprehensive data from Korean Air Flight 801 (1997 Guam crash):

### Crash Details
- **Date**: August 6, 1997
- **Location**: Guam International Airport
- **Fatalities**: 229 passengers, 25 survivors
- **Primary Cause**: Pilot error and navigational aid failure

### Key Factors
- Non-precision approach with out-of-service glideslope
- Descent below minimum safe altitude
- Captain fatigue and inadequate crew communication
- Pilot misinterpretation of navigation signals

### AI Copilot Solutions
- Detects descent below safe altitude
- Issues immediate terrain pull-up alerts
- Prompts for missed approach when glideslope signal weak/absent
- Enforces cross-checks among crew members

### Testing
Run the integration test suite:
```bash
python test_kal801_integration.py
```

## 🔧 API Endpoints

### Chat Interface
- `POST /chat/status_update/` - AI copilot chat with flight-specific responses

### Historical Data
- `POST /store_crash_data/` - Store historical crash data with embeddings
- `GET /similar_crashes/` - Find similar historical incidents

### Flight Data
- `POST /flight_data/` - Record real-time flight data
- `GET /flight_data/{flight_id}` - Retrieve latest flight data

## 🎯 Emergency Response Features

### Flight-Specific Alerts
- **KAL801/CRASH_KAL801**: Terrain proximity, glide slope verification, crew cross-checks
- **TURKISH1951**: Radio altimeter backup, manual approach, speed control
- **ASIANA214**: Approach speed monitoring, landing gear verification

### Emergency Keywords
The AI monitors for: "warning", "alert", "system failure", "low speed", "terrain", "altimeter", "autopilot", "approach", "landing gear", "glideslope", "minimum altitude", "terrain pull-up"

### Response Format
- **System Status**: Current flight conditions
- **Urgent Recommendation**: Immediate action required
- **Next Steps**: Follow-up procedures

## 🔍 Similarity Search

The system uses vector embeddings to find relevant historical incidents:

```bash
# Search for terrain-related incidents
curl "http://localhost:8000/similar_crashes/?query=terrain%20proximity&top_k=3"
```

## 🛠️ Development

### Adding New Crash Data
1. Create JSON data with required fields
2. Use `store_crash_flight_data()` function
3. Update flight-specific prompts in `langchain_utils.py`
4. Add to frontend flight selection

### Model Configuration
- **Current Model**: "gemma:2b" (optimized for performance)
- **Timeout**: 15 seconds with fallback responses
- **Embedding Model**: "all-MiniLM-L6-v2" for similarity search

## 📈 Performance

- **Response Time**: 15-second timeout with intelligent fallbacks
- **Accuracy**: Flight-specific responses with historical context
- **Scalability**: Vector search supports thousands of historical incidents
- **Reliability**: Multiple fallback mechanisms for system stability

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.