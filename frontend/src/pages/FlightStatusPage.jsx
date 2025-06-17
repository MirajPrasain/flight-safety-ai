import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { BackArrowIcon, SpeakerIcon, StopIcon, MicrophoneIcon, PlaneIcon } from '../components/Icons';
import BASE_URL from '../config/api';
import './FlightStatusPage.css';

// TTS Providers
const TTS_PROVIDERS = {
  WEB_SPEECH: 'web_speech',
  ELEVENLABS: 'elevenlabs'
};

// TTS Function
async function speak(text, provider = TTS_PROVIDERS.WEB_SPEECH, audioRef = null) {
  if (provider === TTS_PROVIDERS.ELEVENLABS) {
    // ElevenLabs TTS implementation
    try {
      const apiKey = process.env.REACT_APP_ELEVENLABS_API_KEY;
      if (!apiKey || apiKey.trim() === '') {
        console.warn('ElevenLabs API key not found, falling back to Web Speech');
        return speak(text, TTS_PROVIDERS.WEB_SPEECH, audioRef);
      }

      console.log('Starting ElevenLabs TTS...');
      
      const response = await fetch('https://api.elevenlabs.io/v1/text-to-speech/NFG5qt843uXKj4pFvR7C', {
        method: 'POST',
        headers: {
          'Accept': 'audio/mpeg',
          'Content-Type': 'application/json',
          'xi-api-key': apiKey
        },
        body: JSON.stringify({
          text: text,
          model_id: 'eleven_monolingual_v1',
          voice_settings: {
            stability: 0.5,
            similarity_boost: 0.5
          }
        })
      });

      if (response.ok) {
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        console.log('ElevenLabs audio created, storing reference...');
        
        // Store the audio instance for stopping
        if (audioRef) {
          // Clear any existing audio first
          if (audioRef.current) {
            console.log('Clearing existing audio reference...');
            try {
              audioRef.current.pause();
              audioRef.current.currentTime = 0;
              if (audioRef.current.src) {
                URL.revokeObjectURL(audioRef.current.src);
              }
            } catch (error) {
              console.error('Error clearing existing audio:', error);
            }
          }
          audioRef.current = audio;
          console.log('Audio reference stored:', audioRef.current);
        }
        
        // Set up event listeners
        audio.onended = () => {
          console.log('ElevenLabs audio ended naturally');
          if (audioRef && audioRef.current === audio) {
            audioRef.current = null;
          }
        };
        
        audio.onerror = (error) => {
          console.error('ElevenLabs audio error:', error);
          if (audioRef && audioRef.current === audio) {
            audioRef.current = null;
          }
        };
        
        audio.onpause = () => {
          console.log('ElevenLabs audio paused');
        };
        
        // Start playing
        console.log('Starting ElevenLabs audio playback...');
        await audio.play();
        
        return new Promise((resolve) => {
          audio.onended = () => {
            console.log('ElevenLabs audio playback completed');
            if (audioRef && audioRef.current === audio) {
              audioRef.current = null;
            }
            resolve();
          };
          audio.onerror = () => {
            console.error('ElevenLabs audio playback error');
            if (audioRef && audioRef.current === audio) {
              audioRef.current = null;
            }
            resolve();
          };
        });
      } else {
        console.error('ElevenLabs API error:', response.status, response.statusText);
        // Fallback to Web Speech
        return speak(text, TTS_PROVIDERS.WEB_SPEECH, audioRef);
      }
    } catch (error) {
      console.error('ElevenLabs TTS error:', error);
      // Fallback to Web Speech
      return speak(text, TTS_PROVIDERS.WEB_SPEECH, audioRef);
    }
  } else {
    // Web Speech API
    if ('speechSynthesis' in window) {
      return new Promise((resolve) => {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1;
        utterance.volume = 0.8;
        utterance.onend = resolve;
        utterance.onerror = resolve;
        speechSynthesis.speak(utterance);
      });
    }
  }
}

// Stop speech function
function stopSpeech(audioRef = null) {
  console.log('Stopping speech...', { audioRef: audioRef?.current });
  
  // Stop Web Speech
  if ('speechSynthesis' in window) {
    speechSynthesis.cancel();
    console.log('Web Speech stopped');
  }
  
  // Stop ElevenLabs audio
  if (audioRef && audioRef.current) {
    try {
      console.log('Stopping ElevenLabs audio...');
      const audio = audioRef.current;
      
      // Pause and reset the audio
      audio.pause();
      audio.currentTime = 0;
      
      // Remove event listeners to prevent memory leaks
      audio.onended = null;
      audio.onerror = null;
      audio.onpause = null;
      
      // Clear the audio source
      if (audio.src) {
        URL.revokeObjectURL(audio.src);
        audio.src = '';
      }
      
      // Clear the reference
      audioRef.current = null;
      console.log('ElevenLabs audio stopped successfully');
    } catch (error) {
      console.error('Error stopping ElevenLabs audio:', error);
      // Force clear the reference even if there's an error
      if (audioRef) {
        audioRef.current = null;
      }
    }
  } else {
    console.log('No ElevenLabs audio reference found to stop');
  }
}

// Check if ElevenLabs is available
function isElevenLabsAvailable() {
  const apiKey = process.env.REACT_APP_ELEVENLABS_API_KEY;
  return !!apiKey && apiKey.trim() !== '';
}

const FlightStatusPage = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [isConnected, setIsConnected] = useState(true);
  const [ttsProvider, setTTSProvider] = useState(TTS_PROVIDERS.WEB_SPEECH);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [currentFlightPhase, setCurrentFlightPhase] = useState('preflight');
  const lastSpokenRef = useRef(null);
  const currentAudioRef = useRef(null);

  // Flight phases and their corresponding actions
  const flightPhases = [
    { id: 'preflight', label: 'Preflight', icon: '🛫', color: '#00b4ff', endpoint: 'copilot_chat' },
    { id: 'takeoff', label: 'Takeoff', icon: '✈️', color: '#ff6b35', endpoint: 'copilot_chat' },
    { id: 'climb', label: 'Climb', icon: '📈', color: '#4ecdc4', endpoint: 'copilot_chat' },
    { id: 'cruise', label: 'Cruise', icon: '☁️', color: '#45b7d1', endpoint: 'copilot_chat' },
    { id: 'descent', label: 'Descent', icon: '📉', color: '#96ceb4', endpoint: 'copilot_chat' },
    { id: 'approach', label: 'Approach', icon: '🎯', color: '#feca57', endpoint: 'copilot_chat' },
    { id: 'landing', label: 'Landing', icon: '🛬', color: '#ff9ff3', endpoint: 'copilot_chat' },
    { id: 'taxi', label: 'Taxi', icon: '🚗', color: '#54a0ff', endpoint: 'copilot_chat' }
  ];

  // Quick action buttons for different scenarios
  const quickActions = [
    { 
      id: 'system_status', 
      label: 'System Status', 
      icon: '🔧', 
      color: '#3742fa',
      endpoint: 'chat/system_status',
      description: 'Check aircraft systems and instruments'
    },
    { 
      id: 'similar_crashes', 
      label: 'Similar Incidents', 
      icon: '📚', 
      color: '#ffa502',
      endpoint: 'similar_crashes',
      description: 'Find similar historical incidents'
    }
  ];

  // Utility function to clean up markdown formatting for TTS
  const cleanMarkdown = (text) => {
    return text
      // Remove all emojis and special characters more comprehensively
      .replace(/[\u{1F600}-\u{1F64F}]/gu, '') // Emoticons
      .replace(/[\u{1F300}-\u{1F5FF}]/gu, '') // Miscellaneous Symbols and Pictographs
      .replace(/[\u{1F680}-\u{1F6FF}]/gu, '') // Transport and Map Symbols
      .replace(/[\u{1F1E0}-\u{1F1FF}]/gu, '') // Regional Indicator Symbols
      .replace(/[\u{2600}-\u{26FF}]/gu, '') // Miscellaneous Symbols
      .replace(/[\u{2700}-\u{27BF}]/gu, '') // Dingbats
      .replace(/[🚨⚠️🔹📋⚡🔥💥]/g, '') // Specific emojis
      // Remove markdown formatting more thoroughly
      .replace(/\*\*(.*?)\*\*/g, '$1') // Remove **bold**
      .replace(/\*(.*?)\*/g, '$1') // Remove *italic*
      .replace(/^#{1,6}\s+/gm, '') // Remove headers
      .replace(/[[\](){}]/g, '') // Remove brackets and braces
      .replace(/`(.*?)`/g, '$1') // Remove backticks
      .replace(/~~(.*?)~~/g, '$1') // Remove strikethrough
      .replace(/^\s*[-*+]\s+/gm, '') // Remove bullet points
      .replace(/^\s*\d+\.\s+/gm, '') // Remove numbered lists
      .replace(/^\s*>\s+/gm, '') // Remove blockquotes
      .replace(/^\s*\|.*\|.*$/gm, '') // Remove table rows
      .replace(/^\s*[-=]+\s*$/gm, '') // Remove horizontal rules
      // Clean up multiple lines and convert to single flowing text
      .replace(/\n\s*\n/g, ' ') // Replace double line breaks with space
      .replace(/\n/g, ' ') // Replace single line breaks with space
      .replace(/\s+/g, ' ') // Replace multiple spaces with single space
      .replace(/\.\s*\./g, '.') // Fix double periods
      .replace(/\s*,\s*/g, ', ') // Fix comma spacing
      .replace(/\s*:\s*/g, ': ') // Fix colon spacing
      .replace(/\s*;\s*/g, '; ') // Fix semicolon spacing
      .replace(/\s*!\s*/g, '! ') // Fix exclamation spacing
      .replace(/\s*\?\s*/g, '? ') // Fix question mark spacing
      .trim();
  };

  // Utility function to format AI response with proper structure and indentations
  const formatAIResponse = (text, messageId) => {
    // Remove emojis and markdown formatting from display text but keep structure
    const displayText = text
      .replace(/[\u{1F600}-\u{1F64F}]/gu, '') // Emoticons
      .replace(/[\u{1F300}-\u{1F5FF}]/gu, '') // Miscellaneous Symbols and Pictographs
      .replace(/[\u{1F680}-\u{1F6FF}]/gu, '') // Transport and Map Symbols
      .replace(/[\u{1F1E0}-\u{1F1FF}]/gu, '') // Regional Indicator Symbols
      .replace(/[\u{2600}-\u{26FF}]/gu, '') // Miscellaneous Symbols
      .replace(/[\u{2700}-\u{27BF}]/gu, '') // Dingbats
      .replace(/[🚨⚠️🔹📋⚡🔥💥]/g, '') // Specific emojis
      .replace(/\*\*(.*?)\*\*/g, '$1') // Remove ** markdown
      .replace(/\*(.*?)\*/g, '$1'); // Remove * markdown
    
    // Split into sections if there are clear separators
    const sections = displayText.split(/\n\s*\n/);
    
    return sections.map((section, index) => {
      const trimmed = section.trim();
      if (!trimmed) return null;
      
      // Check if this is a header section
      const isHeader = /^(System Status|Urgent Recommendation|Critical Situation|Next Steps|Emergency Procedures|Historical Reference|Lessons Learned|Applicable Procedures|Diversion Recommendation|Approach Procedures|Alternatives|IMMEDIATE ACTION REQUIRED|CLOSING IMMEDIATE DISTANCE|CRITICAL EMERGENCY|Flight Phase|Checklist|Procedures|Warnings)/i.test(trimmed);
      
      // Format the text with proper structure
      const lines = trimmed.split('\n').map(line => line.trim()).filter(line => line.length > 0);
      
      const formattedLines = lines.map((line, lineIndex) => {
        // Handle bullet points
        if (/^[-•*]\s/.test(line)) {
          return `  • ${line.replace(/^[-•*]\s/, '')}`;
        }
        // Handle numbered lists
        if (/^\d+\.\s/.test(line)) {
          return `  ${line}`;
        }
        // Handle headers (first line of header sections)
        if (isHeader && lineIndex === 0) {
          return `SECTION: ${line}`;
        }
        // Handle sub-headers
        if (/^[A-Z][A-Z\s]+:$/.test(line)) {
          return `\nSUB-SECTION: ${line}`;
        }
        // Regular content with proper indentation
        if (isHeader && lineIndex > 0) {
          return `  ${line}`;
        }
        return line;
      });
      
      const formattedText = formattedLines.join('\n');
      
      return (
        <motion.div 
          key={index} 
          className={`ai-section ${isHeader ? 'ai-header' : 'ai-content'}`}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ 
            duration: 0.3, 
            delay: index * 0.1,
            ease: "easeOut"
          }}
        >
          <pre className="ai-text">
            {formattedText}
          </pre>
        </motion.div>
      );
    }).filter(Boolean);
  };

  // Handle flight phase button click
  const handleFlightPhaseClick = async (phaseId) => {
    setCurrentFlightPhase(phaseId);
    const phase = flightPhases.find(p => p.id === phaseId);
    
    const userMessage = {
      id: Date.now(),
      text: `Requesting ${phase.label} procedures and checklist`,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setLoadingMessage(`Analyzing ${phase.label} procedures...`);

    try {
      // Use the copilot_chat endpoint for flight phase guidance
      const response = await fetch(`${BASE_URL}/copilot_chat/?question=${encodeURIComponent(`Provide detailed ${phase.label} procedures, checklist, and safety considerations for commercial aviation. Include specific steps, speed requirements, altitude considerations, and any warnings or critical points.`)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      const aiMessage = {
        id: Date.now() + 1,
        text: data.answer,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error getting flight phase guidance:', error);
      
      // Fallback response
      const fallbackMessage = {
        id: Date.now() + 1,
        text: `Flight Phase: ${phase.label}\n\nProcedures and checklist for ${phase.label} phase. Please refer to your aircraft's operating manual for specific procedures.`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, fallbackMessage]);
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  // Handle quick action button click
  const handleQuickActionClick = async (action) => {
    const userMessage = {
      id: Date.now(),
      text: `Requesting ${action.label}`,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setLoadingMessage(`Processing ${action.label}...`);

    try {
      let response;
      let data;

      console.log(`Processing quick action: ${action.id} with endpoint: ${action.endpoint}`);

      switch (action.endpoint) {
        case 'advise_pilot':
          // Use emergency advice endpoint with full flight_data object
          response = await fetch(`${BASE_URL}/advise_pilot/`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              flight_data: {
                flight_id: 'KAL801',
                aircraft_type: 'Boeing 737',
                pilot_id: 'PILOT001',
                timestamp: new Date().toISOString(),
                location: {
                  latitude: 37.7749,
                  longitude: -122.4194,
                  altitude_ft: 35000
                },
                speed: {
                  airspeed_knots: 450,
                  vertical_speed_fpm: 0
                },
                engine: {
                  engine_1_rpm: 95,
                  engine_2_rpm: 95
                },
                aircraft_systems: {
                  landing_gear_status: 'UP',
                  flap_setting: '0',
                  autopilot_engaged: true,
                  warnings: []
                },
                environment: {
                  wind_speed_knots: 20,
                  wind_direction_deg: 270,
                  temperature_c: -50,
                  visibility_miles: 10,
                  precipitation: 'NONE',
                  terrain_proximity_ft: 1000
                },
                pilot_actions: {
                  throttle_percent: 85,
                  pitch_deg: 2,
                  roll_deg: 0,
                  yaw_deg: 0
                }
              }
            })
          });
          data = await response.json();
          break;

        case 'chat/system_status':
          // Use system status endpoint
          response = await fetch(`${BASE_URL}/chat/system_status/`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              flight_id: 'CUSTOM_FLIGHT',
              message: 'Check all aircraft systems and instruments for any anomalies or warnings'
            })
          });
          data = await response.json();
          break;

        case 'similar_crashes':
          // Use similar crashes endpoint
          response = await fetch(`${BASE_URL}/similar_crashes/?query=${encodeURIComponent('flight safety incidents and accidents')}&top_k=2`);
          data = await response.json();
          // Format the results - fix the data structure
          const formattedResults = data.results.map((crash, index) => 
            `${index + 1}. Flight ID: ${crash.flight_id}\n   Summary: ${crash.summary}\n   Similarity Score: ${(crash.similarity * 100).toFixed(1)}%`
          ).join('\n\n');
          data = { advice: `Similar Historical Incidents:\n\n${formattedResults}` };
          break;

        default:
          throw new Error(`Unknown endpoint: ${action.endpoint}`);
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      console.log('Final data for AI message:', data);

      const aiMessage = {
        id: Date.now() + 1,
        text: data.advice || data.explanation || data.answer || 'No response received',
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error(`Error processing ${action.label}:`, error);
      
      const fallbackMessage = {
        id: Date.now() + 1,
        text: `Unable to process ${action.label} at this time. Please try again or contact support. Error: ${error.message}`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, fallbackMessage]);
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  // Send custom message
  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setLoadingMessage('Analyzing flight data and generating AI response...');

    const loadingTimeout = setTimeout(() => {
      if (isLoading) {
        console.warn('Loading timeout reached, showing fallback message');
        setLoadingMessage('Taking longer than expected...');
      }
    }, 10000);

    try {
      // Use the status_update endpoint for general queries
      const response = await fetch(`${BASE_URL}/chat/status_update/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          flight_id: 'CUSTOM_FLIGHT',
          message: inputMessage
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      const aiMessage = {
        id: Date.now() + 1,
        text: data.advice,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      const fallbackMessage = {
        id: Date.now() + 1,
        text: "I'm here to assist with your flight. Please ask me about procedures, checklists, or any flight-related questions.",
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, fallbackMessage]);
    } finally {
      clearTimeout(loadingTimeout);
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleBackClick = () => {
    navigate('/copilot');
  };

  // Check backend connection status
  const checkConnection = useCallback(async () => {
    try {
      const response = await fetch(`${BASE_URL}/`, {
        method: 'GET',
        signal: AbortSignal.timeout(3000)
      });
      setIsConnected(response.ok);
    } catch (error) {
      console.warn('Backend connection check failed:', error);
      setIsConnected(false);
    }
  }, []);

  // Check connection on component mount and periodically
  useEffect(() => {
    checkConnection();
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, [checkConnection]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    const chatMessages = document.querySelector('.chat-messages');
    if (chatMessages) {
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  }, [messages]);

  // Global stop function
  const stopAllAudio = useCallback(() => {
    console.log('stopAllAudio called, current state:', { isSpeaking, audioRef: currentAudioRef?.current });
    stopSpeech(currentAudioRef);
    setIsSpeaking(false);
    console.log('stopAllAudio completed');
  }, []);

  // Auto-speak effect for new AI messages
  useEffect(() => {
    const lastMessage = messages[messages.length - 1];
    
    if (lastMessage && lastMessage.role === 'assistant' && lastMessage.id !== lastSpokenRef.current) {
      const textToSpeak = cleanMarkdown(lastMessage.content);
      
      if (textToSpeak) {
        lastSpokenRef.current = lastMessage.id;
        setIsSpeaking(true);
        
        speak(textToSpeak, ttsProvider, currentAudioRef).catch(error => {
          console.error('TTS error:', error);
        }).finally(() => {
          setIsSpeaking(false);
        });
      }
    }
  }, [messages, ttsProvider, stopAllAudio]);

  // Manual speak button handler
  const handleSpeak = useCallback(async (messageId, content) => {
    console.log('handleSpeak called:', { messageId, isSpeaking, ttsProvider });
    
    // If already speaking, stop first
    if (isSpeaking) {
      console.log('Already speaking, stopping audio...');
      stopAllAudio();
      return;
    }
    
    const textToSpeak = cleanMarkdown(content);
    if (!textToSpeak) {
      console.log('No text to speak after cleaning');
      return;
    }
    
    console.log('Starting speech for message:', messageId);
    
    // Stop any existing audio before starting new one
    stopAllAudio();
    
    lastSpokenRef.current = messageId;
    setIsSpeaking(true);
    
    try {
      console.log('Calling speak function with provider:', ttsProvider);
      await speak(textToSpeak, ttsProvider, currentAudioRef);
      console.log('Speech completed successfully');
    } catch (error) {
      console.error('TTS error:', error);
    } finally {
      console.log('Setting isSpeaking to false');
      setIsSpeaking(false);
    }
  }, [ttsProvider, isSpeaking, stopAllAudio]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (e.key === 'Escape' && isSpeaking) {
        stopAllAudio();
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [isSpeaking, stopAllAudio]);

  // Animation variants
  const pageVariants = {
    initial: { opacity: 0 },
    animate: { 
      opacity: 1,
      transition: { duration: 0.8, ease: "easeOut" }
    }
  };

  const headerVariants = {
    initial: { opacity: 0, y: -30 },
    animate: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.8, delay: 0.2, ease: "easeOut" }
    }
  };

  const chatVariants = {
    initial: { opacity: 0, y: 50 },
    animate: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.8, delay: 0.4, ease: "easeOut" }
    }
  };

  const phaseButtonVariants = {
    hover: { 
      scale: 1.05,
      transition: { duration: 0.2, ease: "easeInOut" }
    },
    tap: { 
      scale: 0.95,
      transition: { duration: 0.1 }
    }
  };

  return (
    <motion.div 
      className="flight-status-page"
      variants={pageVariants}
      initial="initial"
      animate="animate"
    >
      <div className="page-background">
        <div className="background-overlay"></div>
        <div className="hud-grid"></div>
      </div>

      <div className="page-content">
        <div className="container">
          {/* Header */}
          <motion.header 
            className="flight-status-header"
            variants={headerVariants}
            initial="initial"
            animate="animate"
          >
            <button className="back-btn" onClick={handleBackClick}>
              <BackArrowIcon size={16} /> Back to Simulations
            </button>
            
            <div className="flight-info">
              <h1 className="flight-title">Interactive Flight Simulation</h1>
              <div className="flight-details">
                <span className="flight-id">CUSTOM_FLIGHT</span>
                <span className="current-phase">Current Phase: {flightPhases.find(p => p.id === currentFlightPhase)?.label}</span>
              </div>
              
              {/* Connection Status */}
              <div className="connection-status">
                <span className={`connection-indicator ${isConnected ? 'connected' : 'disconnected'}`}></span>
                <span className="connection-text">
                  {isConnected ? 'Backend Connected' : 'Backend Disconnected'}
                </span>
              </div>
              
              {/* TTS Provider Status */}
              <div className="tts-status">
                <span className="tts-status-indicator">
                  {ttsProvider === TTS_PROVIDERS.ELEVENLABS ? (
                    <MicrophoneIcon size={16} />
                  ) : (
                    <SpeakerIcon size={16} />
                  )}
                </span>
                <span className="tts-status-text">
                  {ttsProvider === TTS_PROVIDERS.ELEVENLABS ? 'ElevenLabs Active' : 'Web Speech Active'}
                </span>
              </div>
              
              {/* TTS Provider Toggle */}
              <div className="tts-toggle">
                <span className="tts-label">Voice Quality:</span>
                <select 
                  value={ttsProvider} 
                  onChange={(e) => {
                    const newProvider = e.target.value;
                    setTTSProvider(newProvider);
                    console.log('TTS provider changed to:', newProvider);
                  }}
                  className="tts-select"
                >
                  <option value={TTS_PROVIDERS.WEB_SPEECH}>
                    🔊 Web Speech (Free)
                  </option>
                  {isElevenLabsAvailable() ? (
                    <option value={TTS_PROVIDERS.ELEVENLABS}>
                      🎤 ElevenLabs (Premium)
                    </option>
                  ) : (
                    <option value={TTS_PROVIDERS.ELEVENLABS} disabled>
                      🎤 ElevenLabs (API Key Required)
                    </option>
                  )}
                </select>
                {!isElevenLabsAvailable() && (
                  <div className="tts-warning">
                    <small>Add REACT_APP_ELEVENLABS_API_KEY to .env for premium voice</small>
                  </div>
                )}
              </div>
            </div>
          </motion.header>

          {/* Quick Actions */}
          <motion.div 
            className="quick-actions-container"
            initial={{ opacity: 0, y: 20 }}
            animate={{ 
              opacity: 1, 
              y: 0,
              transition: { duration: 0.6, delay: 0.2, ease: "easeOut" }
            }}
          >
            <h2 className="actions-title">Quick Actions</h2>
            <div className="quick-actions-grid">
              {quickActions.map((action, index) => (
                <motion.button
                  key={action.id}
                  className="quick-action-btn"
                  onClick={() => handleQuickActionClick(action)}
                  variants={phaseButtonVariants}
                  whileHover="hover"
                  whileTap="tap"
                  style={{
                    '--action-color': action.color,
                    animationDelay: `${index * 0.1}s`
                  }}
                  title={action.description}
                >
                  <span className="action-icon">{action.icon}</span>
                  <span className="action-label">{action.label}</span>
                </motion.button>
              ))}
            </div>
          </motion.div>

          {/* Flight Phase Buttons */}
          <motion.div 
            className="flight-phases-container"
            initial={{ opacity: 0, y: 20 }}
            animate={{ 
              opacity: 1, 
              y: 0,
              transition: { duration: 0.6, delay: 0.3, ease: "easeOut" }
            }}
          >
            <h2 className="phases-title">Flight Phases</h2>
            <div className="flight-phases-grid">
              {flightPhases.map((phase, index) => (
                <motion.button
                  key={phase.id}
                  className={`phase-btn ${currentFlightPhase === phase.id ? 'active' : ''}`}
                  onClick={() => handleFlightPhaseClick(phase.id)}
                  variants={phaseButtonVariants}
                  whileHover="hover"
                  whileTap="tap"
                  style={{
                    '--phase-color': phase.color,
                    animationDelay: `${index * 0.1}s`
                  }}
                >
                  <span className="phase-icon">{phase.icon}</span>
                  <span className="phase-label">{phase.label}</span>
                </motion.button>
              ))}
            </div>
          </motion.div>

          {/* Chat Interface */}
          <motion.div 
            className="chat-container"
            variants={chatVariants}
            initial="initial"
            animate="animate"
          >
            <div className="chat-messages">
              {messages.length === 0 && (
                <div className="welcome-message">
                  <div className="welcome-icon">
                    <PlaneIcon size={32} />
                  </div>
                  <h3>Interactive Flight Simulation</h3>
                  <p>Select a flight phase above, use quick actions, or ask me anything about aviation procedures, checklists, and safety protocols.</p>
                </div>
              )}
              
              <AnimatePresence>
                {messages.map((message, index) => (
                  <motion.div
                    key={message.id || index}
                    className={`message ${message.sender}`}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="message-content">
                      {message.sender === 'ai' ? (
                        <div className="ai-response">
                          {formatAIResponse(message.text, message.id)}
                          <div className="ai-controls">
                            <button
                              className={`speak-button ${isSpeaking ? 'speaking' : ''}`}
                              onClick={() => handleSpeak(message.id, message.text)}
                              title={isSpeaking ? 'Stop speaking (or press Escape)' : `Speak using ${ttsProvider === TTS_PROVIDERS.ELEVENLABS ? 'ElevenLabs' : 'Web Speech'}`}
                            >
                              {isSpeaking ? <StopIcon size={16} /> : <SpeakerIcon size={16} />}
                            </button>
                            <span className="tts-provider-indicator">
                              {ttsProvider === TTS_PROVIDERS.ELEVENLABS ? (
                                <MicrophoneIcon size={12} />
                              ) : (
                                <SpeakerIcon size={12} />
                              )}
                            </span>
                          </div>
                        </div>
                      ) : (
                        <div className="user-message">
                          <pre>{message.text}</pre>
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              
              {isLoading && (
                <motion.div 
                  className="message ai loading-message"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="loading-content">
                    <div className="loading-indicator">
                      <div className="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                    <div className="loading-text">
                      <div className="loading-message-text">{loadingMessage}</div>
                      <div className="loading-subtitle">
                        AI Copilot is analyzing the situation...
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>

            <div className="chat-input-container">
              <div className="input-wrapper">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask about flight procedures, checklists, or any aviation questions..."
                  className="chat-input"
                  disabled={isLoading}
                />
                <button 
                  onClick={sendMessage}
                  className="send-btn"
                  disabled={!inputMessage.trim() || isLoading}
                >
                  <span className="send-icon">→</span>
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
};

export default FlightStatusPage; 