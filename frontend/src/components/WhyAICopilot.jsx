import React, { useEffect, useRef } from 'react';
import '../styles/WhyAICopilot.css';

const WhyAICopilot = () => {
  const sectionRef = useRef(null);

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

  const reasons = [
    {
      title: "Cognitive Load Reduction",
      description: "AI continuously monitors and supports decisions, reducing mental overload during critical phases.",
      delay: 0.2,
      gradient: "linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 153, 204, 0.05))"
    },
    {
      title: "Human Error Mitigation",
      description: "Over 75% of flight incidents trace back to human error. The AI Copilot adds a layer of fail-safe judgment.",
      delay: 0.4,
      gradient: "linear-gradient(135deg, rgba(0, 255, 200, 0.1), rgba(0, 200, 150, 0.05))"
    },
    {
      title: "Situational Awareness Support",
      description: "In low-visibility or high-stress scenarios, AI maintains vigilance and gives objective insights.",
      delay: 0.6,
      gradient: "linear-gradient(135deg, rgba(0, 180, 255, 0.1), rgba(0, 140, 200, 0.05))"
    },
    {
      title: "Procedural Safety in Takeoff & Landing",
      description: "The AI tracks protocols, confirms conditions, and surfaces anomalies before they escalate.",
      delay: 0.8,
      gradient: "linear-gradient(135deg, rgba(0, 220, 180, 0.1), rgba(0, 180, 140, 0.05))"
    }
  ];

  return (
    <section ref={sectionRef} className="why-ai-copilot">
      <div className="container">
        <h2 className="section-title">Why AI Copilot?</h2>
        
        <div className="luxury-cards">
          {reasons.map((reason, index) => (
            <div 
              key={index} 
              className="luxury-card"
              style={{ 
                animationDelay: `${reason.delay}s`,
                '--card-gradient': reason.gradient
              }}
            >
              <div className="card-glass">
                <div className="card-content">
                  <div className="card-header">
                    <h3 className="card-title">{reason.title}</h3>
                    <div className="card-accent"></div>
                  </div>
                  
                  <p className="card-description">{reason.description}</p>
                  
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

export default WhyAICopilot; 