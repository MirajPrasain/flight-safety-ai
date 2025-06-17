import React from 'react';
import { useNavigate } from 'react-router-dom';
import WhyAICopilot from '../components/WhyAICopilot';
import '../styles/LandingPage.css';

const LandingPage = () => {
  const navigate = useNavigate();

  const handleStartDemo = () => {
    navigate('/copilot');
  };

  return (
    <div className="landing-page">
      {/* Background Video */}
      <video 
        className="background-video" 
        autoPlay 
        muted 
        loop 
        playsInline
      >
        <source src="/pilot_bg.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>

      {/* Dark Gradient Overlay */}
      <div className="overlay"></div>

      {/* Hero Section */}
      <div className="hero-section">
        <div className="content">
          <h1 className="headline">
            AI Copilot for Flight Safety
          </h1>
          <p className="subheadline">
            Prevent disasters. Assist decisions. Trusted in the skies.
          </p>
          <button 
            className="cta-button"
            onClick={handleStartDemo}
          >
            Start Demo
          </button>
        </div>

        {/* Radar-themed decorative elements */}
        <div className="radar-elements">
          <div className="radar-circle radar-circle-1"></div>
          <div className="radar-circle radar-circle-2"></div>
          <div className="radar-circle radar-circle-3"></div>
          <div className="radar-sweep"></div>
        </div>
      </div>

      {/* Scrollable Sections */}
      <div className="scrollable-sections">
        <WhyAICopilot />
  

      </div>
    </div>
  );
};

export default LandingPage;
