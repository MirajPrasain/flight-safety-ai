# ElevenLabs TTS Setup Guide

## ElevenLabs Integration Complete!

### Current Configuration:
- **API Key**: `sk_4b2613e45519ce186448c6005bcb577baf889521bd1c7776`
- **Voice ID**: `NFG5qt843uXKj4pFvR7C`
- **Model**: `eleven_monolingual_v1`
- **Voice Settings**: Optimized for aviation communication

### How to Use:

#### Immediate Use (Current Setup)
The system is already configured with your credentials and ready to use:
1. **Visit**: http://localhost:3000
2. **Select a flight simulation** (KAL801, CRASH_KAL801, etc.)
3. **Send a message** to the AI copilot
4. **Toggle to "ElevenLabs (Premium)"** in the voice quality dropdown
5. **Click the Microphone Speak button** on any AI response

#### Environment Variables (Recommended for Production)
For better security, create a `.env` file in the `frontend/` directory:

```bash
# Create .env file in frontend directory
REACT_APP_ELEVEN_API_KEY=sk_4b2613e45519ce186448c6005bcb577baf889521bd1c7776
REACT_APP_ELEVEN_VOICE_ID=NFG5qt843uXKj4pFvR7C
```

Then restart the frontend:
```bash
cd frontend
npm start
```

### Voice Quality Features:

#### ElevenLabs Settings:
- **Stability**: 0.6 (higher for consistent voice)
- **Similarity Boost**: 0.8 (higher for better quality)
- **Speaker Boost**: Enabled (enhanced clarity)
- **Style**: Neutral (professional tone)

#### Fallback System:
- **Primary**: ElevenLabs (high-quality)
- **Fallback**: Web Speech API (if ElevenLabs fails)
- **Error Handling**: Graceful degradation

### Testing the Integration:

#### Test 1: Basic Functionality
1. Go to http://localhost:3000
2. Select "KAL801" flight simulation
3. Send: "What's the current flight status?"
4. Toggle to "ElevenLabs (Premium)"
5. Click the Microphone button on the AI response

#### Test 2: Emergency Alerts
1. Send: "Terrain alert detected"
2. Listen for urgency detection
3. Notice faster speech rate and deeper pitch

#### Test 3: Fallback System
1. Temporarily break API key
2. Send a message
3. Verify automatic fallback to Web Speech

### Security Notes:
- Current setup uses hardcoded credentials for demo
- For production use, move to environment variables
- API key has usage limits and should be protected

### Status Indicators:
- Microphone Icon = ElevenLabs Active
- Speaker Icon = Web Speech Active
- API key is configured and working
- Voice ID is set correctly
- Fallback to Web Speech if API fails
- **For production**: Move credentials to environment variables

### Cost Management:
- **Free Tier**: ~10,000 characters/month
- **Monitor Usage**: Check ElevenLabs dashboard
- **Upgrade**: When approaching limits
- **Budget**: Set spending limits in account

### Troubleshooting:
1. **No Sound**: Check browser permissions
2. **API Errors**: Verify API key is valid
3. **Fallback Issues**: Check Web Speech support
4. **Voice Quality**: Adjust stability settings

### Next Steps:
1. Test all flight simulations
2. Monitor API usage
3. Consider production deployment
4. Set up monitoring and alerts

### Support:
- **ElevenLabs Docs**: https://elevenlabs.io/docs
- **API Reference**: https://elevenlabs.io/docs/api-reference
- **Voice Library**: https://elevenlabs.io/voice-library

---

**🎉 Your AI Copilot now has premium voice synthesis!** 