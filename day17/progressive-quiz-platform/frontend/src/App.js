import React, { useState } from 'react';
import DifficultyDashboard from './components/DifficultyDashboard';
import './App.css';

function App() {
  const [sessionStarted, setSessionStarted] = useState(false);
  const [userId] = useState(`user_${Math.random().toString(36).substr(2, 9)}`);
  const [sessionId] = useState(`session_${Math.random().toString(36).substr(2, 9)}`);

  const startSession = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/difficulty/create-session?user_id=${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        setSessionStarted(true);
      }
    } catch (error) {
      console.error('Error starting session:', error);
      // For demo, continue anyway
      setSessionStarted(true);
    }
  };

  if (!sessionStarted) {
    return (
      <div className="welcome-screen">
        <div className="welcome-container">
          <h1>🧠 Progressive Quiz Platform</h1>
          <p>Experience AI-powered adaptive difficulty that learns from your performance</p>
          <div className="features">
            <div className="feature">
              <span className="feature-icon">🎯</span>
              <span>Adaptive Difficulty</span>
            </div>
            <div className="feature">
              <span className="feature-icon">📊</span>
              <span>Real-time Analytics</span>
            </div>
            <div className="feature">
              <span className="feature-icon">🚀</span>
              <span>Progressive Learning</span>
            </div>
          </div>
          <button onClick={startSession} className="start-button">
            Start Learning Session
          </button>
          <div className="demo-info">
            <p>User ID: {userId}</p>
            <p>Session ID: {sessionId}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <DifficultyDashboard userId={userId} sessionId={sessionId} />
    </div>
  );
}

export default App;
