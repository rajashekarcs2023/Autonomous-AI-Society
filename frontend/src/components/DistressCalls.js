import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';  // For navigation
import './DistressCalls.css';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';

const DistressCalls = () => {
  const [distressCalls, setDistressCalls] = useState([]);
  const [summary, setSummary] = useState('');
  const [highestDistressLevel, setHighestDistressLevel] = useState('');
  const [identifiedCity, setIdentifiedCity] = useState('');
  
  const navigate = useNavigate();  // Hook for navigation

  const fetchDistressCall = async (callNumber) => {
    try {
      const response = await fetch(`http://localhost:4001/distress_details/distress_call_${callNumber}.txt`);
      const data = await response.text();
      return data;
    } catch (error) {
      console.error(`Error fetching distress call ${callNumber}:`, error);
      return '';
    }
  };

  const fetchSummary = async () => {
    try {
      const response = await fetch('http://localhost:4001/distress_details/final_summary.txt');
      const data = await response.text();
      return data;
    } catch (error) {
      console.error('Error fetching final summary:', error);
      return '';
    }
  };

  useEffect(() => {
    const fetchDistressData = async () => {
      const newDistressCalls = [];
      for (let i = 1; i <= 5; i++) {
        const callData = await fetchDistressCall(i);
        newDistressCalls.push(callData);
      }
      setDistressCalls(newDistressCalls);

      const summaryData = await fetchSummary();
      setSummary(summaryData);

      const matchDistress = summaryData.match(/Highest Distress Level: (.+)/);
      const matchCity = summaryData.match(/Identified City: (.+)/);
      if (matchDistress) {
        setHighestDistressLevel(matchDistress[1]);
      }
      if (matchCity) {
        setIdentifiedCity(matchCity[1]);
      }
    };

    const interval = setInterval(fetchDistressData, 3000);
    return () => clearInterval(interval);
  }, []);

  const getDistressSeverity = (level) => {
    if (level >= 0.75) {
      return { className: 'urgent', label: 'Urgent' };
    } else if (level >= 0.4) {
      return { className: 'moderate', label: 'Moderate' };
    } else {
      return { className: 'low', label: 'Low' };
    }
  };

  return (
    <div className="distress-container">
      <h1>Distress Calls Overview</h1>
      <div className="distress-calls">
        {distressCalls.map((call, index) => {
          const distressLevel = parseFloat(call.match(/Distress Level for .+: (.+)/)?.[1]) || 0;
          const severity = getDistressSeverity(distressLevel);

          return (
            <div key={index} className={`distress-call-box ${severity.className}`}>
              <div>
                <h3>Distress Call {index + 1}</h3>
                <pre>{call}</pre>
              </div>
              <div className="urgency-label">{severity.label}</div>
              <div className="distress-bar">
                <CircularProgressbar
                  value={distressLevel * 100}
                  text={`${Math.round(distressLevel * 100)}%`}
                  styles={buildStyles({
                    textColor: '#333',
                    pathColor: severity.className === 'urgent' ? '#ff0000' : severity.className === 'moderate' ? '#ffa500' : '#28a745',
                    trailColor: '#eee',
                  })}
                />
              </div>
            </div>
          );
        })}
      </div>

      <div className="summary-container">
        <h2>Highest Distress Level</h2>
        <p>{highestDistressLevel}</p>

        <h2>Identified City</h2>
        <p>{identifiedCity}</p>

        <h2>Summary</h2>
        <pre>{summary}</pre>
      </div>

      {/* Button to navigate to the Drone Updates page */}
      <button onClick={() => navigate('/drone-updates')} className="drone-updates-button">
        View Drone Updates
      </button>
    </div>
  );
};

export default DistressCalls;
