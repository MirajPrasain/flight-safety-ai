import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import '../styles/CrashCaseStudies.css';

const CrashCaseStudies = () => {
  const [crashes, setCrashes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedCards, setExpandedCards] = useState({});
  const sectionRef = useRef(null);

  useEffect(() => {
    const fetchCrashes = async () => {
      try {
        setLoading(true);
        const response = await axios.get('http://localhost:8000/similar_crashes?query=terrain alert ignored');
        setCrashes(response.data.results || []);
      } catch (err) {
        console.error('Error fetching crashes:', err);
        setError('Failed to load crash data');
        // Enhanced fallback data for demo purposes
        setCrashes([
          {
            flight_id: "Turkish Airlines Flight 1951",
            summary: "Crashed short of the runway at Amsterdam due to faulty radio altimeter and delayed pilot response.",
            top_reason: "Radio altimeter malfunction and pilot confusion",
            learnings: "AI Copilot could have flagged the unreliable altimeter readings and prompted corrective action before stall conditions."
          },
          {
            flight_id: "Korean Air Flight 801",
            summary: "Crashed into terrain near Guam due to pilot fatigue and ignored terrain proximity warnings during approach.",
            top_reason: "Pilot fatigue and ignored terrain warnings",
            learnings: "AI Copilot could have provided enhanced terrain awareness alerts and fatigue monitoring to prevent critical decision errors."
          },
          {
            flight_id: "Air France Flight 447",
            summary: "Crashed into Atlantic Ocean due to pilot confusion and incorrect stall recovery procedures at high altitude.",
            top_reason: "Pilot error in stall recovery",
            learnings: "AI Copilot could have detected the aerodynamic stall early and provided real-time recovery guidance to prevent loss of control."
          },
          {
            flight_id: "US Airways Flight 1549",
            summary: "Successfully landed on Hudson River after bird strike disabled both engines, saving all 155 passengers.",
            top_reason: "Bird strike and engine failure",
            learnings: "AI Copilot could have assisted with emergency landing site selection and optimal glide path calculations for maximum survivability."
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchCrashes();
  }, []);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
          }
        });
      },
      { threshold: 0.3 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  const toggleCardExpansion = (index) => {
    setExpandedCards(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  if (loading) {
    return (
      <section ref={sectionRef} className="crash-case-studies">
        <div className="container">
          <h2 className="section-title">Crash Case Studies</h2>
          <div className="loading">Loading crash data...</div>
        </div>
      </section>
    );
  }

  return (
    <section ref={sectionRef} className="crash-case-studies">
      <div className="container">
        <h2 className="section-title">Crash Case Studies</h2>
        
        <div className="crash-cards-grid">
          {crashes.map((crash, index) => (
            <div 
              key={index} 
              className="crash-card"
              style={{ animationDelay: `${index * 0.2}s` }}
            >
              <div className="card-glass">
                <div className="card-content">
                  <div className="card-header">
                    <h3 className="flight-title">{crash.flight_id}</h3>
                    <div className="card-accent"></div>
                  </div>
                  
                  <div className="crash-summary-container">
                    <p className={`crash-summary ${expandedCards[index] ? 'expanded' : ''}`}>
                      {crash.summary}
                    </p>
                    {crash.summary.length > 150 && (
                      <button 
                        className="read-more-btn"
                        onClick={() => toggleCardExpansion(index)}
                      >
                        {expandedCards[index] ? 'Read Less' : 'Read More'}
                      </button>
                    )}
                  </div>
                  
                  <div className="crash-causes">
                    <h4 className="causes-title">Primary Cause</h4>
                    <div className="cause-tag">
                      {crash.top_reason}
                    </div>
                  </div>
                  
                  <div className="crash-learnings">
                    <h4 className="learnings-title">AI Solution</h4>
                    <blockquote className="learning-quote">
                      "{crash.learnings}"
                    </blockquote>
                  </div>
                  
                  <div className="card-glow"></div>
                  <div className="card-reflection"></div>
                  <div className="card-shadow"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default CrashCaseStudies; 