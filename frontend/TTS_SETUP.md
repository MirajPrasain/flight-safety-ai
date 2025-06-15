# TTS (Text-to-Speech) Setup Guide

## Overview
The AI Copilot now supports two TTS providers:
- **Web Speech API** (Free, built-in browser support)
- **ElevenLabs** (Premium quality, requires API key)

## Setup Instructions

### 1. Web Speech API (Default)
- **No setup required** - works immediately
- Uses your system's available voices
- Automatically selects the best available voice

### 2. ElevenLabs (Premium Quality)

#### Step 1: Get API Key
1. Visit [ElevenLabs.io](https://elevenlabs.io/)
2. Create a free account
3. Go to your profile settings
4. Copy your API key

#### Step 2: Configure Environment
1. Create a `.env` file in the `frontend` directory
2. Add your API key:
```bash
REACT_APP_ELEVEN_API_KEY=your_actual_api_key_here
```

#### Step 3: Restart Development Server
```bash
npm start
```

## Usage

### Voice Quality Toggle
- Located in the chat header
- Switch between "Web Speech" and "ElevenLabs (Premium)"
- Changes apply immediately

### Auto-Speak
- AI responses are automatically spoken
- Uses the currently selected TTS provider
- Respects urgency detection for emergency alerts

### Manual Speak Button
- Click the speak button on any AI message
- Icon changes based on selected provider:
  - Speaker Icon = Web Speech
  - Microphone Icon = ElevenLabs

## Cost Information

### ElevenLabs Pricing (as of 2025):
- **Free Tier**: ~10,000 characters/month
- **Starter**: ~$5/month for 30,000+ characters
- **Creator**: ~$22/month for 100,000+ characters

### Web Speech API:
- **Completely free**
- No character limits
- Uses your system's voices

## Fallback System
- If ElevenLabs fails, automatically falls back to Web Speech
- If no API key is configured, uses Web Speech by default
- Graceful error handling for all scenarios

## Testing Voices

### Web Speech Testing:
```javascript
// In browser console
testAllWebSpeechVoices()
```

### ElevenLabs Testing:
1. Set up API key
2. Select ElevenLabs in the toggle
3. Send a test message
4. Click the microphone button on AI response

## Voice Quality Comparison

### Web Speech API:
- **Pros**: Free, immediate, no setup
- **Cons**: Robotic, limited voice options
- **Best for**: Testing, development, basic functionality

### ElevenLabs:
- **Pros**: Natural, human-like, multiple voices
- **Cons**: Requires API key, usage limits
- **Best for**: Production, professional use

## Emergency Alerts
- System detects urgency keywords
- Adjusts speech rate and pitch for alerts
- Provides clear, immediate communication

## Troubleshooting

### Common Issues:
1. **No sound**: Check browser permissions
2. **ElevenLabs not working**: Verify API key
3. **Voice quality poor**: Try different Web Speech voices

### Browser Support:
- **Chrome**: Full support
- **Firefox**: Full support
- **Safari**: Limited Web Speech support
- **Edge**: Full support 