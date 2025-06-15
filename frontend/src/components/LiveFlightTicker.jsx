import React, { useState, useEffect } from 'react';
import { PlaneIcon } from './Icons';
import './LiveFlightTicker.css';

const LiveFlightTicker = () => {
  const [flights, setFlights] = useState([]);
  const [loading, setLoading] = useState(true);

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
            .slice(0, 8) // Limit to 8 flights for ticker
            .map(flight => ({
              id: flight[0] || 'unknown',
              callsign: flight[1] || 'N/A',
              country: flight[2] || 'Unknown',
              altitude: flight[7],
              velocity: flight[9] || 0,
              onGround: flight[8] || false
            }));
          
          setFlights(processedFlights);
        }
      } catch (error) {
        console.error('Error fetching flight data:', error);
        // Fallback to demo data if API fails
        setFlights([
          { id: 'demo1', callsign: 'UAL123', country: 'US', altitude: 35000, velocity: 450, onGround: false },
          { id: 'demo2', callsign: 'DLH456', country: 'DE', altitude: 32000, velocity: 480, onGround: false },
          { id: 'demo3', callsign: 'BAW789', country: 'GB', altitude: 28000, velocity: 420, onGround: false },
          { id: 'demo4', callsign: 'AFR234', country: 'FR', altitude: 30000, velocity: 460, onGround: false },
          { id: 'demo5', callsign: 'KLM567', country: 'NL', altitude: 25000, velocity: 440, onGround: false }
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

  const inFlightCount = flights.filter(f => !f.onGround).length;
  const onGroundCount = flights.filter(f => f.onGround).length;

  return (
    <div className="live-flight-ticker">
      <div className="ticker-container">
        <div className="ticker-header">
          <div className="ticker-title">
            <span className="ticker-icon">
              <PlaneIcon size={20} />
            </span>
            <span className="ticker-text">LIVE FLIGHT TRACKING</span>
          </div>
          <div className="ticker-stats">
            <div className="stat-item">
              <span className="stat-number">{inFlightCount}</span>
              <span className="stat-label">IN FLIGHT</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{onGroundCount}</span>
              <span className="stat-label">ON GROUND</span>
            </div>
          </div>
        </div>
        
        <div className="ticker-content">
          <div className="ticker-track">
            {loading ? (
              <div className="ticker-item loading">
                <span>Loading live flight data...</span>
              </div>
            ) : (
              <>
                {flights.map((flight, index) => (
                  <div key={`${flight.id}-${index}`} className="ticker-item">
                    <span className="flight-callsign">{flight.callsign}</span>
                    <span className="flight-altitude">{Math.round(flight.altitude)}ft</span>
                    <span className="flight-speed">{Math.round(flight.velocity)}kts</span>
                    <span className="flight-country">{flight.country}</span>
                    <span className="flight-status">{flight.onGround ? 'GROUND' : 'AIRBORNE'}</span>
                  </div>
                ))}
                {/* Duplicate items for seamless loop */}
                {flights.map((flight, index) => (
                  <div key={`${flight.id}-${index}-duplicate`} className="ticker-item">
                    <span className="flight-callsign">{flight.callsign}</span>
                    <span className="flight-altitude">{Math.round(flight.altitude)}ft</span>
                    <span className="flight-speed">{Math.round(flight.velocity)}kts</span>
                    <span className="flight-country">{flight.country}</span>
                    <span className="flight-status">{flight.onGround ? 'GROUND' : 'AIRBORNE'}</span>
                  </div>
                ))}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveFlightTicker; 