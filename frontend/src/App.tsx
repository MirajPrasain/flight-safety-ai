import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import './App.css';

import CopilotPage from './pages/CopilotPage';
import ChatPage from './pages/ChatPage';
import FlightStatusPage from './pages/FlightStatusPage';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/copilot" element={<CopilotPage />} />
          <Route path="/chat/:flightId" element={<ChatPage />} />
          <Route path="/flight-status" element={<FlightStatusPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
