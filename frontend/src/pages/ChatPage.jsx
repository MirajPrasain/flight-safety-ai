import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  setTTSProvider, 
  getTTSProvider, 
  TTS_PROVIDERS, 
  isElevenLabsAvailable,
  isSpeaking,
  stopSpeech
} from '../utils/ttsUtils';
import { 
  PlaneIcon, 
  MicrophoneIcon, 
  SpeakerIcon, 
  StopIcon, 
  BackArrowIcon,
  RefreshIcon
} from '../components/Icons';
import BASE_URL from '../config/api';
import './ChatPage.css';

// Enhanced TTS function that supports both Web Speech and ElevenLabs
async function speak(text, provider = TTS_PROVIDERS.WEB_SPEECH) {
  if (provider === TTS_PROVIDERS.ELEVENLABS) {
    // Use ElevenLabs TTS
    try {
      const ELEVEN_API_KEY = 'sk_4b2613e45519ce186448c6005bcb577baf889521bd1c7776';
      const VOICE_ID = 'NFG5qt843uXKj4pFvR7C';
      
      // Clean the text for speech
      const cleanedText = text
        .replace(/\*\*(.*?)\*\*/g, '$1')
        .replace(/\*(.*?)\*/g, '$1')
        .replace(/^#{1,6}\s+/gm, '')
        .replace(/⚠️|🚨|🚀|🎯|✅|❌|💡|🔧|🎮|🛡|💰|🔊|🎤/g, '')
        .replace(/[[\](){}]/g, '')
        .replace(/\n\s*\n/g, '. ')
        .replace(/\n/g, '. ')
        .replace(/\.\s*\./g, '.')
        .replace(/\s+/g, ' ')
        .trim();

      const response = await fetch(
        `https://api.elevenlabs.io/v1/text-to-speech/${VOICE_ID}`,
        {
          method: 'POST',
          headers: {
            'xi-api-key': ELEVEN_API_KEY,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            text: cleanedText,
            model_id: "eleven_monolingual_v1",
            voice_settings: {
              stability: 0.7,
              similarity_boost: 0.8,
              style: 0.0,
              use_speaker_boost: true
            }
          })
        }
      );

      if (!response.ok) {
        throw new Error('ElevenLabs API error');
      }

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      
      return new Promise((resolve, reject) => {
        audio.onended = () => {
          URL.revokeObjectURL(audioUrl);
          resolve();
        };
        
        audio.onerror = (error) => {
          URL.revokeObjectURL(audioUrl);
          reject(error);
        };
        
        audio.play().catch(error => {
          URL.revokeObjectURL(audioUrl);
          reject(error);
        });
      });
      
    } catch (error) {
      console.error('ElevenLabs TTS error:', error);
      console.log('Falling back to Web Speech API...');
      // Fallback to Web Speech
      return speak(text, TTS_PROVIDERS.WEB_SPEECH);
    }
  } else {
    // Use Web Speech API
    if ('speechSynthesis' in window) {
      // Stop any ongoing speech
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'en-US';
      utterance.rate = 0.8; // Slightly slower for better comprehension
      utterance.pitch = 0.9; // Lower pitch for professionalism
      utterance.volume = 0.9;
      
      return new Promise((resolve, reject) => {
        utterance.onend = resolve;
        utterance.onerror = reject;
        window.speechSynthesis.speak(utterance);
      });
    }
  }
}

const ChatPage = () => {
  const { flightId } = useParams();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [ttsProvider, setTTSProviderState] = useState(getTTSProvider());
  const [isSpeaking, setIsSpeakingState] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState(''); // Track loading message content
  const [retryCount, setRetryCount] = useState(0); // Track retry attempts
  const maxRetries = 2; // Maximum number of retry attempts
  const [isConnected, setIsConnected] = useState(true); // Track backend connection
  
  // Track last spoken message to prevent duplicates
  const lastSpokenRef = useRef(null);

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
      // Remove markdown formatting
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/\*(.*?)\*/g, '$1')
      .replace(/^#{1,6}\s+/gm, '')
      .replace(/[[\](){}]/g, '')
      // Clean up multiple lines and convert to single flowing text
      .replace(/\n\s*\n/g, ' ') // Replace double line breaks with space
      .replace(/\n/g, ' ') // Replace single line breaks with space
      .replace(/\s+/g, ' ') // Replace multiple spaces with single space
      .replace(/\.\s*\./g, '.') // Fix double periods
      .replace(/\s*,\s*/g, ', ') // Fix comma spacing
      .replace(/\s*:\s*/g, ': ') // Fix colon spacing
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
      
      // Check if this is a header section (contains keywords like "System Status", "Urgent Recommendation", etc.)
      const isHeader = /^(System Status|Urgent Recommendation|Critical Situation|Next Steps|Emergency Procedures|Historical Reference|Lessons Learned|Applicable Procedures|Diversion Recommendation|Approach Procedures|Alternatives|IMMEDIATE ACTION REQUIRED|CLOSING IMMEDIATE DISTANCE|CRITICAL EMERGENCY)/i.test(trimmed);
      
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

  // Flight data for different simulations
  const flightData = {
    'KAL801': {
      title: 'Korean Air Flight 801',
      date: 'August 6, 1997',
      location: 'Guam',
      description: 'Pilot descended below glide slope despite warnings',
      status: 'Critical - Terrain Alert'
    },
    'CRASH_KAL801': {
      title: 'Korean Air Flight 801 (Historical Crash)',
      date: 'August 6, 1997',
      location: 'Guam International Airport',
      description: 'Controlled flight into terrain - 229 fatalities, 25 survivors',
      status: 'Critical - Historical Reference'
    },
    'CRASH_THY1951': {
      title: 'Turkish Airlines Flight 1951',
      date: 'February 25, 2009',
      location: 'Amsterdam',
      description: 'Radio altimeter failure and autothrottle malfunction',
      status: 'Critical - System Failure'
    },
    'TURKISH1951': {
      title: 'Turkish Airlines Flight 1951',
      date: 'February 25, 2009',
      location: 'Amsterdam',
      description: 'Radio altimeter failure & autopilot mismanagement',
      status: 'Critical - System Failure'
    },
    'CRASH_AAR214': {
      title: 'Asiana Airlines Flight 214',
      date: 'July 6, 2013',
      location: 'San Francisco',
      description: 'Low-speed approach due to autothrottle disengagement',
      status: 'Critical - Low Speed'
    },
    'ASIANA214': {
      title: 'Asiana Airlines Flight 214',
      date: 'July 6, 2013',
      location: 'San Francisco',
      description: 'Low-speed approach with inadequate manual correction',
      status: 'Critical - Low Speed'
    }
  };

  const currentFlight = flightData[flightId] || {
    title: 'Unknown Flight',
    date: 'Unknown',
    location: 'Unknown',
    description: 'Flight data not available',
    status: 'Unknown'
  };

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

    // Set a timeout to prevent loading from getting stuck
    const loadingTimeout = setTimeout(() => {
      if (isLoading) {
        console.warn('Loading timeout reached, showing fallback message');
        setLoadingMessage('Taking longer than expected...');
      }
    }, 10000); // 10 second timeout

    try {
      // Send request to backend
      const response = await fetch(`${BASE_URL}/chat/status_update/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          flight_id: flightId,
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
      
      // Fallback response if backend is not available
      const fallbackMessage = {
        id: Date.now() + 1,
        text: "This aircraft is currently descending below glide slope with terrain alerts. Immediate go-around advised.",
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

  // Function to handle retry
  const handleRetry = () => {
    if (retryCount < maxRetries) {
      setRetryCount(prev => prev + 1);
      sendMessage();
    }
  };

  // Reset retry count when message is sent successfully
  useEffect(() => {
    if (!isLoading && retryCount > 0) {
      setRetryCount(0);
    }
  }, [isLoading, retryCount]);

  // Check backend connection status
  const checkConnection = useCallback(async () => {
    try {
      const response = await fetch(`${BASE_URL}/`, {
        method: 'GET',
        signal: AbortSignal.timeout(3000) // 3 second timeout
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
    const interval = setInterval(checkConnection, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, [checkConnection]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    const chatMessages = document.querySelector('.chat-messages');
    if (chatMessages) {
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  }, [messages]);

  // Auto-speak for new AI messages (simplified without animation delays)
  useEffect(() => {
    const lastMessage = messages[messages.length - 1];
    
    if (lastMessage && lastMessage.sender === 'ai' && lastMessage.id !== lastSpokenRef.current) {
      // Clean the text for speech
      const textToSpeak = cleanMarkdown(lastMessage.text);
      
      if (textToSpeak && textToSpeak !== lastSpokenRef.current) {
        lastSpokenRef.current = lastMessage.id;
        setIsSpeakingState(true);
        
        // Speak the message immediately (no animation delay)
        speak(textToSpeak, ttsProvider).catch(error => {
          console.error('TTS error:', error);
        }).finally(() => {
          setIsSpeakingState(false);
        });
      }
    }
  }, [messages, ttsProvider]);

  // Manual speak button handler with stop functionality
  const handleSpeak = useCallback(async (messageId, content) => {
    // If currently speaking, stop it
    if (isSpeaking) {
      stopSpeech();
      setIsSpeakingState(false);
      return;
    }
    
    // If this message was already spoken, speak it again
    const textToSpeak = cleanMarkdown(content);
    if (!textToSpeak) return;
    
    lastSpokenRef.current = messageId;
    setIsSpeakingState(true);
    
    try {
      await speak(textToSpeak, ttsProvider);
    } catch (error) {
      console.error('TTS error:', error);
    } finally {
      setIsSpeakingState(false);
    }
  }, [ttsProvider, isSpeaking]);

  // Animation variants (simplified)
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

  return (
    <motion.div 
      className="chat-page"
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
            className="chat-header"
            variants={headerVariants}
            initial="initial"
            animate="animate"
          >
            <button className="back-btn" onClick={handleBackClick}>
              <BackArrowIcon size={16} /> Back to Simulations
            </button>
            
            <div className="flight-info">
              <h1 className="flight-title">{currentFlight.title}</h1>
              <div className="flight-details">
                <span className="flight-id">{flightId}</span>
                <span className="flight-date">{currentFlight.date}</span>
                <span className="flight-location">{currentFlight.location}</span>
              </div>
              <div className="flight-status">
                <span className="status-indicator critical"></span>
                <span className="status-text">{currentFlight.status}</span>
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
                    setTTSProviderState(newProvider);
                    console.log('TTS provider changed to:', newProvider);
                  }}
                  className="tts-select"
                >
                  <option value={TTS_PROVIDERS.WEB_SPEECH}>
                    <SpeakerIcon size={14} /> Web Speech
                  </option>
                  {isElevenLabsAvailable() && (
                    <option value={TTS_PROVIDERS.ELEVENLABS}>
                      <MicrophoneIcon size={14} /> ElevenLabs (Premium)
                    </option>
                  )}
                </select>
              </div>
            </div>
          </motion.header>

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
                  <h3>AI Copilot Simulation</h3>
                  <p>Ask for a flight status update to see how AI Copilot would assist in this critical situation.</p>
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
                              title={isSpeaking ? 'Stop speaking' : `Speak using ${ttsProvider}`}
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
                        {retryCount > 0 ? `Retry attempt ${retryCount}/${maxRetries}` : 'AI Copilot is analyzing the situation...'}
                      </div>
                    </div>
                  </div>
                  
                  {/* Retry button for failed requests */}
                  {retryCount > 0 && retryCount < maxRetries && (
                    <motion.div 
                      className="retry-container"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      <button 
                        onClick={handleRetry}
                        className="retry-btn"
                        title="Retry sending message"
                      >
                        <RefreshIcon size={14} /> Retry ({maxRetries - retryCount} attempts left)
                      </button>
                    </motion.div>
                  )}
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
                  placeholder="Update me with the current flight status"
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

export default ChatPage; 