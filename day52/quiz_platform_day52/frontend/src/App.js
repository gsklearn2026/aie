import React, { useState, useEffect } from 'react';
import './App.css';
import MemoryDashboard from './components/MemoryDashboard';
import QuizPanel from './components/QuizPanel';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="App">
      <header className="app-header">
        <h1>🧠 Quiz Platform - Memory Optimized</h1>
        <div className="tab-buttons">
          <button 
            className={activeTab === 'dashboard' ? 'active' : ''}
            onClick={() => setActiveTab('dashboard')}
          >
            Memory Dashboard
          </button>
          <button 
            className={activeTab === 'quiz' ? 'active' : ''}
            onClick={() => setActiveTab('quiz')}
          >
            Quiz Testing
          </button>
        </div>
      </header>
      
      <main className="app-main">
        {activeTab === 'dashboard' ? <MemoryDashboard /> : <QuizPanel />}
      </main>
    </div>
  );
}

export default App;
