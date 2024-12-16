import React from 'react';
import './App.css';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import DistressCalls from './components/DistressCalls';
import DroneUpdates from './components/DroneUpdates';  // Import your Drone Updates page

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<DistressCalls />} />
          <Route path="/drone-updates" element={<DroneUpdates />} /> {/* New route for Drone Updates */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;

