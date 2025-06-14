import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Globe from 'react-globe.gl';
import LiveFlightTicker from '../components/LiveFlightTicker';
import './CopilotPage.css';

const CopilotPage = () => {
  const navigate = useNavigate();
  const globeRef = useRef();
  const [flights, setFlights] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fix scroll position on page mount
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // Fetch live flight data from OpenSky Network API
  useEffect(() => {
    const fetchFlightData = async () => {
      try {
        setLoading(true);
        const response = await fetch('https://opensky-network.org/api/states/all');
        const data = await response.json();
        
        if (data.states) {
          // Process and filter flight data
          const processedFlights = data.states
            .filter(flight => flight[5] && flight[6] && flight[7]) // Has lat, lng, altitude
            .slice(0, 15) // Limit to 15 flights for performance
            .map(flight => ({
              id: flight[0] || 'unknown',
              callsign: flight[1] || 'N/A',
              country: flight[2] || 'Unknown',
              latitude: flight[6],
              longitude: flight[5],
              altitude: flight[7],
              velocity: flight[9] || 0,
              verticalRate: flight[11] || 0,
              onGround: flight[8] || false
            }));
          
          setFlights(processedFlights);
        }
      } catch (error) {
        console.error('Error fetching flight data:', error);
        // Fallback to demo data if API fails
        setFlights([
          { id: 'demo1', callsign: 'UAL123', country: 'US', latitude: 40.7128, longitude: -74.0060, altitude: 35000, velocity: 450, verticalRate: 0, onGround: false },
          { id: 'demo2', callsign: 'DLH456', country: 'DE', latitude: 52.5200, longitude: 13.4050, altitude: 32000, velocity: 480, verticalRate: 0, onGround: false },
          { id: 'demo3', callsign: 'BAW789', country: 'GB', latitude: 51.5074, longitude: -0.1278, altitude: 28000, velocity: 420, verticalRate: 0, onGround: false }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchFlightData();
    
    // Refresh flight data every 30 seconds
    const interval = setInterval(fetchFlightData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Initialize globe
  useEffect(() => {
    if (globeRef.current) {
      globeRef.current.controls().autoRotate = true;
      globeRef.current.controls().autoRotateSpeed = 0.5;
      globeRef.current.pointOfView({ lat: 20, lng: 0, altitude: 2.5 });
    }
  }, []);

  const flightsData = [
    {
      id: "KAL801",
      title: "Korean Air Flight 801",
      date: "August 6, 1997",
      location: "Guam",
      cause: "Pilot descended below glide slope despite warnings",
    },
    {
      id: "TURKISH1951",
      title: "Turkish Airlines Flight 1951",
      date: "February 25, 2009",
      location: "Amsterdam",
      cause: "Radio altimeter failure & autopilot mismanagement",
    },
    {
      id: "ASIANA214",
      title: "Asiana Airlines Flight 214",
      date: "July 6, 2013",
      location: "San Francisco",
      cause: "Low-speed approach with inadequate manual correction",
    },
    {
      id: "AIRFRANCE447",
      title: "Air France Flight 447",
      date: "June 1, 2009",
      location: "Atlantic Ocean",
      cause: "Inconsistent speed readings → Stall → Crew disorientation",
    },
    {
      id: "COLGAN3407",
      title: "Colgan Air Flight 3407",
      date: "February 12, 2009",
      location: "Buffalo, NY",
      cause: "Stall due to pilot error & improper stick control",
    },
  ];

  const handleSimulateClick = (flightId) => {
    navigate(`/chat/${flightId}`);
  };

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

  const globeVariants = {
    initial: { opacity: 0, scale: 0.8 },
    animate: { 
      opacity: 1, 
      scale: 1,
      transition: { duration: 1, delay: 0.4, ease: "easeOut" }
    }
  };

  const cardVariants = {
    initial: { opacity: 0, y: 50 },
    animate: (index) => ({
      opacity: 1,
      y: 0,
      transition: { 
        duration: 0.6, 
        delay: 0.8 + (index * 0.1), 
        ease: "easeOut" 
      }
    })
  };

  const buttonVariants = {
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
      className="copilot-page"
      variants={pageVariants}
      initial="initial"
      animate="animate"
    >
      <div className="page-background">
        <div className="background-overlay"></div>
        <div className="hud-grid"></div>
      </div>

      {/* Live Flight Ticker */}
      <LiveFlightTicker />

      <div className="page-content">
        <div className="container">
          <motion.header 
            className="page-header"
            variants={headerVariants}
            initial="initial"
            animate="animate"
          >
            <h1 className="page-title">AI Copilot Simulation</h1>
            <p className="page-subtitle">
              Select a historic flight incident to simulate how AI Copilot could have assisted
            </p>
          </motion.header>

          {/* Live Globe Hero Card */}
          <motion.div 
            className="globe-hero-card"
            variants={globeVariants}
            initial="initial"
            animate="animate"
          >
            <div className="globe-container">
              <Globe
                ref={globeRef}
                globeImageUrl="//unpkg.com/three-globe/example/img/earth-blue-marble.jpg"
                backgroundImageUrl="//unpkg.com/three-globe/example/img/night-sky.png"
                pointsData={flights}
                pointLat="latitude"
                pointLng="longitude"
                pointColor={() => '#00b4ff'}
                pointAltitude="altitude"
                pointRadius={0.5}
                pointResolution={12}
                pointLabel={d => `
                  <div class="flight-tooltip">
                    <strong>${d.callsign}</strong><br/>
                    Alt: ${Math.round(d.altitude)}ft<br/>
                    Speed: ${Math.round(d.velocity)}kts<br/>
                    ${d.country}
                  </div>
                `}
                atmosphereColor="#0099cc"
                atmosphereAltitude={0.15}
                enablePointerInteraction={true}
                width={800}
                height={600}
              />
            </div>
          </motion.div>

          <div className="flights-grid">
            {flightsData.map((flight, index) => (
              <motion.div 
                key={flight.id} 
                className="flight-card"
                variants={cardVariants}
                initial="initial"
                animate="animate"
                custom={index}
                whileHover={{ 
                  y: -8,
                  transition: { duration: 0.3, ease: "easeOut" }
                }}
              >
                <div className="card-glass">
                  <div className="card-content">
                    <div className="card-header">
                      <h3 className="flight-title">{flight.title}</h3>
                      <div className="flight-id">{flight.id}</div>
                    </div>

                    <div className="flight-details">
                      <div className="detail-row">
                        <span className="detail-label">Date:</span>
                        <span className="detail-value">{flight.date}</span>
                      </div>
                      <div className="detail-row">
                        <span className="detail-label">Location:</span>
                        <span className="detail-value">{flight.location}</span>
                      </div>
                    </div>

                    <div className="crash-cause">
                      <h4 className="cause-title">Primary Cause</h4>
                      <p className="cause-description">{flight.cause}</p>
                    </div>

                    <motion.button 
                      className="simulate-btn"
                      onClick={() => handleSimulateClick(flight.id)}
                      variants={buttonVariants}
                      whileHover="hover"
                      whileTap="tap"
                    >
                      <span className="btn-text">Simulate with Copilot</span>
                      <span className="btn-icon">→</span>
                    </motion.button>

                    <div className="card-glow"></div>
                    <div className="card-reflection"></div>
                    <div className="card-shadow"></div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          <motion.div 
            className="page-footer"
            initial={{ opacity: 0, y: 20 }}
            animate={{ 
              opacity: 1, 
              y: 0,
              transition: { duration: 0.6, delay: 1.2, ease: "easeOut" }
            }}
          >
            <p className="footer-text">
              Experience real-time AI assistance in critical flight scenarios
            </p>
          </motion.div>
        </div>
      </div>

      <footer className="copilot-footer">
        <p className="disclaimer">
          ⚠️ Only 15 live flights are shown due to OpenSky Network's free tier API limitations.<br />
          For full functionality, authenticated access or cached flight data is recommended.
        </p>
      </footer>
    </motion.div>
  );
};

export default CopilotPage;