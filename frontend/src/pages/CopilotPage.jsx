import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import './CopilotPage.css';

const CopilotPage = () => {
  const navigate = useNavigate();

  // Fix scroll position on page mount
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  const flights = [
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

  const cardVariants = {
    initial: { opacity: 0, y: 50 },
    animate: (index) => ({
      opacity: 1,
      y: 0,
      transition: { 
        duration: 0.6, 
        delay: 0.4 + (index * 0.1), 
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

          <div className="flights-grid">
            {flights.map((flight, index) => (
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
    </motion.div>
  );
};

export default CopilotPage;