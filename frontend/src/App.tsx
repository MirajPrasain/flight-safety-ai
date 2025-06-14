import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import './App.css';

import CopilotPage from './pages/CopilotPage';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/copilot" element={<CopilotPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
