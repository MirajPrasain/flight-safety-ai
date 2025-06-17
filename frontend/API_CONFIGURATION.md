# API Configuration

## Overview
The frontend has been updated to use the deployed FastAPI backend at `https://flight-safety-ai.onrender.com` instead of localhost.

## Changes Made

### 1. API Configuration File
Created `src/config/api.js`:
```javascript
const BASE_URL = process.env.REACT_APP_API_BASE || "https://flight-safety-ai.onrender.com";
export default BASE_URL;
```

### 2. Updated Components
- **ChatPage.jsx**: Updated all fetch calls to use `${BASE_URL}/...`
- **FlightStatusPage.jsx**: Updated all fetch calls to use `${BASE_URL}/...`

### 3. Package.json Proxy
Added proxy configuration:
```json
{
  "proxy": "https://flight-safety-ai.onrender.com"
}
```

## Environment Variables
You can override the API base URL by setting the environment variable:
```bash
REACT_APP_API_BASE=https://your-custom-backend-url.com
```

## API Endpoints Used
The following endpoints are now pointing to the deployed backend:
- `/chat/status_update/` - Main chat interface
- `/copilot_chat/` - Flight phase guidance
- `/advise_pilot/` - Emergency advice
- `/chat/system_status/` - System status checks
- `/similar_crashes/` - Historical incident search
- `/` - Health check endpoint

## External APIs (Unchanged)
The following external APIs remain unchanged:
- ElevenLabs TTS API (`https://api.elevenlabs.io/`)
- OpenSky Network API (`https://opensky-network.org/api/`)

## Deployment
When deploying the frontend, ensure the backend is accessible at the configured URL. The app will automatically fall back to the deployed URL if no environment variable is set. 