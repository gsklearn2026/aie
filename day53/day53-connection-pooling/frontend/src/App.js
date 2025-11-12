import React, { useState, useEffect } from 'react';
import QuizGenerator from './components/QuizGenerator';
import PoolMetrics from './components/PoolMetrics';
import QuizList from './components/QuizList';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('generate');
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  return (
    <div className="App">
      <header className="app-header">
        <h1>🎯 Quiz Platform - Connection Pooling Demo</h1>
        <p>Day 53: Real-time Pool Monitoring & Resource Management</p>
      </header>

      <nav className="tab-nav">
        <button 
          className={activeTab === 'generate' ? 'active' : ''}
          onClick={() => setActiveTab('generate')}
        >
          Generate Quiz
        </button>
        <button 
          className={activeTab === 'metrics' ? 'active' : ''}
          onClick={() => setActiveTab('metrics')}
        >
          Pool Metrics
        </button>
        <button 
          className={activeTab === 'list' ? 'active' : ''}
          onClick={() => setActiveTab('list')}
        >
          Quiz History
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'generate' && (
          <QuizGenerator onQuizGenerated={() => setRefreshTrigger(prev => prev + 1)} />
        )}
        {activeTab === 'metrics' && <PoolMetrics />}
        {activeTab === 'list' && <QuizList key={refreshTrigger} />}
      </main>
    </div>
  );
}

export default App;
