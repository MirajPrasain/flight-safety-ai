# ElevenLabs TTS Setup

## Premium Voice Quality

The FlightStatusPage now supports ElevenLabs for premium voice quality. Here's how to set it up:

### 1. Get ElevenLabs API Key

1. Go to [ElevenLabs](https://elevenlabs.io/)
2. Sign up for a free account
3. Go to your profile settings
4. Copy your API key

### 2. Add API Key to Environment

Create a `.env` file in the `frontend` directory:

```bash
# frontend/.env
REACT_APP_ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

### 3. Restart the Frontend

After adding the API key, restart your React development server:

```bash
cd frontend
npm start
```

### 4. Select Voice Quality

In the FlightStatusPage:
1. Look for the "Voice Quality" dropdown in the header
2. Select "🎤 ElevenLabs (Premium)" for high-quality voice
3. Select "🔊 Web Speech (Free)" for basic voice

### Features

- **ElevenLabs**: High-quality, natural-sounding voice
- **Web Speech**: Free, built-in browser voice
- **Auto-fallback**: If ElevenLabs fails, automatically uses Web Speech
- **Visual indicators**: Shows which voice provider is active

### Troubleshooting

- If you see "API Key Required", make sure your `.env` file is in the correct location
- If ElevenLabs doesn't work, it will automatically fall back to Web Speech
- Check the browser console for any error messages 