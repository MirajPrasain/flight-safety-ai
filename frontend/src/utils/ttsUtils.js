import axios from 'axios';

// ElevenLabs Configuration
const ELEVEN_API_KEY = process.env.REACT_APP_ELEVEN_API_KEY || 'sk_4b2613e45519ce186448c6005bcb577baf889521bd1c7776';
const VOICE_ID = process.env.REACT_APP_ELEVEN_VOICE_ID || 'NFG5qt843uXKj4pFvR7C';

// TTS Provider Types
export const TTS_PROVIDERS = {
  WEB_SPEECH: 'web_speech',
  ELEVENLABS: 'elevenlabs'
};

// Current TTS provider (can be changed by user)
let currentProvider = TTS_PROVIDERS.ELEVENLABS;

// Global audio reference for ElevenLabs
let currentAudio = null;

// Voice utilities for Web Speech API
let cachedVoices = [];

// Cache voices when they become available
if (typeof window !== 'undefined') {
  window.speechSynthesis.onvoiceschanged = () => {
    cachedVoices = window.speechSynthesis.getVoices();
    console.log('Web Speech voices loaded:', cachedVoices.length);
  };
}

// Get the best available voice for aviation communication (Web Speech)
function getPreferredVoice() {
  const voices = cachedVoices.length > 0 ? cachedVoices : window.speechSynthesis.getVoices();
  
  const preferredVoices = [
    'Google US English',
    'Microsoft David',
    'Microsoft Zira',
    'Daniel',
    'Samantha',
    'Alex',
    'Siri',
    'Victoria',
    'Karen',
    'Tessa',
    'Moira'
  ];
  
  for (const voiceName of preferredVoices) {
    const voice = voices.find(v => 
      v.name.includes(voiceName) || 
      v.name.toLowerCase().includes(voiceName.toLowerCase())
    );
    if (voice) {
      console.log('Selected Web Speech voice:', voice.name);
      return voice;
    }
  }
  
  const fallbackVoice = voices.find(v => 
    v.name.includes('Google') ||
    v.name.includes('Microsoft') ||
    v.name.includes('Enhanced') ||
    v.name.includes('Premium')
  );
  
  if (fallbackVoice) {
    console.log('Using fallback Web Speech voice:', fallbackVoice.name);
    return fallbackVoice;
  }
  
  console.log('Using default Web Speech voice');
  return null;
}

// Text cleaning function to remove markdown and formatting
function cleanTextForSpeech(text) {
  if (!text) return '';
  
  return text
    // Remove markdown asterisks and formatting
    .replace(/\*\*(.*?)\*\*/g, '$1')  // Remove bold **text**
    .replace(/\*(.*?)\*/g, '$1')      // Remove italic *text*
    .replace(/^#{1,6}\s+/gm, '')      // Remove markdown headers
    .replace(/[[\](){}]/g, '')       // Remove brackets and parentheses
    .replace(/\n\s*\n/g, '. ')        // Replace double line breaks with periods
    .replace(/\n/g, '. ')              // Replace single line breaks with periods
    .replace(/\.\s*\./g, '.')          // Clean up multiple periods
    .replace(/\s+/g, ' ')              // Normalize whitespace
    .trim();
}

// Enhanced Web Speech function with urgency detection and pauses
function speakWithWebSpeech(text) {
  if (!('speechSynthesis' in window)) {
    console.warn("Browser doesn't support speech synthesis");
    return Promise.reject(new Error('Web Speech not supported'));
  }
  
  return new Promise((resolve, reject) => {
    // Stop any currently speaking
    window.speechSynthesis.cancel();
    
    // Clean the text for speech
    const cleanedText = cleanTextForSpeech(text);
    console.log('Cleaned text for speech:', cleanedText);
    
    // Detect urgency keywords
    const urgencyKeywords = [
      'terrain', 'glideslope', 'emergency', 'critical', 'warning', 'alert',
      'stall', 'altitude', 'minimum', 'pull-up', 'go-around', 'immediate',
      'dangerous', 'unsafe', 'failure', 'malfunction', 'crash', 'fatal'
    ];
    
    const isUrgent = urgencyKeywords.some(keyword => 
      cleanedText.toLowerCase().includes(keyword)
    );
    
    // Split text into sentences for better pacing
    const sentences = cleanedText
      .split(/[.?!]/)
      .map(s => s.trim())
      .filter(s => s.length > 0);
    
    let index = 0;
    let completed = false;
    
    function speakNext() {
      if (index >= sentences.length) {
        if (!completed) {
          completed = true;
          resolve();
        }
        return;
      }
      
      const sentence = sentences[index];
      const utterance = new SpeechSynthesisUtterance(sentence);
      
      // Voice selection
      const preferred = getPreferredVoice();
      if (preferred) {
        utterance.voice = preferred;
      }
      
      // Enhanced settings based on urgency - slower for better comprehension
      if (isUrgent) {
        utterance.rate = 0.75;    // Even slower for urgent but clear communication
        utterance.pitch = 0.8;    // Deeper, more serious tone
        utterance.volume = 1.0;   // Full volume for alerts
      } else {
        utterance.rate = 0.7;     // Much slower for better comprehension
        utterance.pitch = 0.9;    // Lower pitch for professionalism
        utterance.volume = 0.9;   // Good volume
      }
      
      utterance.lang = 'en-US';
      
      // Add pause between sentences
      utterance.onend = () => {
        setTimeout(() => {
          index++;
          speakNext();
        }, isUrgent ? 300 : 500); // Longer pauses for better comprehension
      };
      
      utterance.onerror = (error) => {
        console.error('Web Speech error:', error);
        if (!completed) {
          completed = true;
          reject(error);
        }
      };
      
      window.speechSynthesis.speak(utterance);
    }
    
    speakNext();
  });
}

// ElevenLabs TTS function
async function speakWithElevenLabs(text) {
  try {
    if (!ELEVEN_API_KEY || ELEVEN_API_KEY === 'YOUR_API_KEY') {
      console.warn('ElevenLabs API key not configured, falling back to Web Speech');
      return await speakWithWebSpeech(text);
    }

    // Stop any ongoing Web Speech before starting ElevenLabs
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }

    // Clean the text for speech
    const cleanedText = cleanTextForSpeech(text);
    console.log('Using ElevenLabs TTS for cleaned text:', cleanedText.substring(0, 50) + '...');
    
    const response = await axios.post(
      `https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}`,
      {
        text: cleanedText,
        model_id: "eleven_monolingual_v1",
        voice_settings: {
          stability: 0.7,           // Higher stability for more consistent voice
          similarity_boost: 0.8,    // Higher similarity for better voice quality
          style: 0.0,               // Neutral style
          use_speaker_boost: true   // Enhanced speaker clarity
        }
      },
      {
        headers: {
          'xi-api-key': ELEVEN_API_KEY,
          'Content-Type': 'application/json'
        },
        responseType: 'blob',
        timeout: 30000 // 30 second timeout
      }
    );

    const audioBlob = new Blob([response.data], { type: 'audio/mpeg' });
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    
    // Store reference for stopping
    currentAudio = audio;
    
    return new Promise((resolve, reject) => {
      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
        currentAudio = null;
        resolve();
      };
      
      audio.onerror = (error) => {
        URL.revokeObjectURL(audioUrl);
        currentAudio = null;
        console.error('ElevenLabs audio playback error:', error);
        reject(error);
      };
      
      audio.play().catch(error => {
        URL.revokeObjectURL(audioUrl);
        currentAudio = null;
        console.error('ElevenLabs audio play error:', error);
        reject(error);
      });
    });
    
  } catch (error) {
    console.error('ElevenLabs TTS error:', error);
    console.log('Falling back to Web Speech API...');
    return await speakWithWebSpeech(text);
  }
}

// Main speak function that uses the current provider
export async function speak(text) {
  try {
    // Stop any ongoing speech before starting new speech
    stopSpeech();
    
    switch (currentProvider) {
      case TTS_PROVIDERS.ELEVENLABS:
        return await speakWithElevenLabs(text);
      case TTS_PROVIDERS.WEB_SPEECH:
      default:
        return await speakWithWebSpeech(text);
    }
  } catch (error) {
    console.error('TTS error:', error);
    // Final fallback to Web Speech if everything else fails
    if (currentProvider !== TTS_PROVIDERS.WEB_SPEECH) {
      console.log('Final fallback to Web Speech...');
      return await speakWithWebSpeech(text);
    }
    throw error;
  }
}

// Function to change TTS provider
export function setTTSProvider(provider) {
  if (Object.values(TTS_PROVIDERS).includes(provider)) {
    currentProvider = provider;
    console.log('TTS provider changed to:', provider);
  } else {
    console.error('Invalid TTS provider:', provider);
  }
}

// Function to get current TTS provider
export function getTTSProvider() {
  return currentProvider;
}

// Function to check if ElevenLabs is available
export function isElevenLabsAvailable() {
  return ELEVEN_API_KEY && ELEVEN_API_KEY !== 'YOUR_API_KEY' && ELEVEN_API_KEY.startsWith('sk_');
}

// Voice testing utility for Web Speech
export function testAllWebSpeechVoices() {
  if (typeof window === 'undefined') return;
  
  const voices = window.speechSynthesis.getVoices();
  console.log('Available Web Speech voices:', voices.map(v => v.name));
  
  voices.forEach((voice, index) => {
    setTimeout(() => {
      const utterance = new SpeechSynthesisUtterance(`Testing ${voice.name}`);
      utterance.voice = voice;
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      utterance.volume = 0.8;
      window.speechSynthesis.speak(utterance);
    }, index * 3000);
  });
}

// Stop all speech
export function stopSpeech() {
  // Stop Web Speech
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
  
  // Stop ElevenLabs audio
  if (currentAudio) {
    currentAudio.pause();
    currentAudio.currentTime = 0;
    currentAudio = null;
  }
}

// Check if speech is currently playing
export function isSpeaking() {
  const webSpeechSpeaking = typeof window !== 'undefined' && 
    'speechSynthesis' in window && 
    window.speechSynthesis.speaking;
  
  const elevenLabsPlaying = currentAudio && !currentAudio.paused && !currentAudio.ended;
  
  return webSpeechSpeaking || elevenLabsPlaying;
} 