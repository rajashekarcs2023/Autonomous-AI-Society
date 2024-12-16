
                // Insert your AP
              import React, { useState, useEffect } from 'react';
              import './DroneUpdates.css';
              
              const DroneUpdates = () => {
                const [results, setResults] = useState([]);
              
                // Function to call Groq API to determine the risk priority
                const getRiskPriority = async (description) => {
                  const groqApi = 'https://api.groq.com/openai/v1/chat/completions';
                  const groqApiKey = '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';  // Insert your API key
              
                  const headers = {
                    "Authorization": `Bearer ${groqApiKey}`,
                    "Content-Type": "application/json"
                  };
              
                  const payload = {
                    "model": "mixtral-8x7b-32768",
                    "messages": [
                      {
                        "role": "system",
                        "content": "You are an AI assistant. Analyze the following description and categorize it as 'Low', 'Moderate', 'High', or 'Very High' risk for a disaster response. You don't have to give long sentences, just the priority category."
                      },
                      {
                        "role": "user",
                        "content": description
                      }
                    ],
                    "max_tokens": 10
                  };
              
                  try {
                      const response = await fetch(groqApi, {
                          method: 'POST',
                          headers: headers,
                          body: JSON.stringify(payload),
                      });
                      
                      const data = await response.json();
                      
                      // Ensure the response structure is correct before accessing
                      if (data && data.choices && data.choices.length > 0 && data.choices[0].message && data.choices[0].message.content) {
                          const priority = data.choices[0].message.content.trim();
                          return priority;
                      } else {
                          console.error("Unexpected response structure from Groq:", data);
                          return "Low";  // Default to 'Low' if the response structure is unexpected
                      }
                  } catch (error) {
                      console.error("Error calling Groq:", error);
                      return "Low";  // Default to 'Low' in case of error
                  }
              };
                useEffect(() => {
                  const fetchResults = async () => {
                    try {
                      const response = await fetch('http://localhost:4001/descriptions/processed_results.txt');
                      const textData = await response.text();
              
                      const parsedResults = await Promise.all(
                        textData.split(/\n\n/).map(async (entry) => {
                          const lines = entry.split('\n');
              
                          if (lines.length < 3) {
                            return null; // Skip incomplete entries
                          }
              
                          const fileLine = lines[0] || ''; 
                          const descriptionLine = lines[1] || '';
                          const coordinatesLine = lines[2] || '';
              
                          // Parse coordinates
                          const coordinates = coordinatesLine.replace('Coordinates: ', '').replace(/'/g, '"');
                          let coordinatesObj = {};
                          try {
                            coordinatesObj = JSON.parse(coordinates);
                          } catch (error) {
                            console.error('Error parsing coordinates:', error);
                          }
              
                          // Call Groq API to determine the risk priority
                          const riskPriority = await getRiskPriority(descriptionLine);
              
                          return {
                            file: fileLine.replace('File: ', '') || 'Unknown File',
                            description: descriptionLine.replace('Description: ', '') || 'No Description',
                            coordinates: coordinatesObj || { latitude: 'N/A', longitude: 'N/A' },
                            riskPriority: riskPriority || 'Low',
                          };
                        })
                      );
              
                      setResults(parsedResults.filter(entry => entry !== null)); // Remove null entries
                    } catch (error) {
                      console.error('Error fetching processed_results:', error);
                    }
                  };
              
                  fetchResults();
                }, []);
              
                // Function to dynamically determine the color for the priority box
                const getPriorityColorClass = (riskPriority) => {
                  return (riskPriority.toLowerCase() === 'high' || riskPriority.toLowerCase() === 'very high') 
                    ? 'high-priority' 
                    : 'low-priority';
                };
              
                return (
                  <div className="drone-updates-container">
                    <h2>Drone Updates</h2>
                    <div className="results-grid">
                      {results.map((result, index) => (
                        <div key={index} className="result-row">
                          <div className="description-box">
                            <h3>Description</h3>
                            <p>{result.description}</p>
                          </div>
                          <div className="coordinates-box">
                            <h3>Coordinates</h3>
                            <p>Latitude: {result.coordinates.latitude}</p>
                            <p>Longitude: {result.coordinates.longitude}</p>
                          </div>
                          <div className={`priority-box ${getPriorityColorClass(result.riskPriority)}`}>
                            <h3>Priority</h3>
                            <p>{result.riskPriority} Priority Dispatch</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              };
              
              export default DroneUpdates;
              