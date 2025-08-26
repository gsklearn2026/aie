import React, { useState, useEffect } from 'react';
import TestDashboard from './components/TestDashboard';
import AIGenerator from './components/AIGenerator';
import PerformanceMonitor from './components/PerformanceMonitor';
import './styles/App.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [systemHealth, setSystemHealth] = useState(null);

  useEffect(() => {
    checkSystemHealth();
    const interval = setInterval(checkSystemHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const checkSystemHealth = async () => {
    try {
      const response = await fetch('/health');
      const data = await response.json();
      setSystemHealth(data);
    } catch (error) {
      console.error('Health check failed:', error);
      setSystemHealth({ status: 'unhealthy', error: error.message });
    }
  };

  const renderActiveComponent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <TestDashboard systemHealth={systemHealth} />;
      case 'generator':
        return <AIGenerator />;
      case 'performance':
        return <PerformanceMonitor />;
      default:
        return <TestDashboard systemHealth={systemHealth} />;
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>AI Testing Framework</h1>
          <div className="system-status">
            <span className={`status-indicator ${systemHealth?.status || 'unknown'}`}>
              {systemHealth?.status === 'healthy' ? '🟢' : '🔴'}
            </span>
            <span className="status-text">
              {systemHealth?.status === 'healthy' ? 'System Online' : 'System Issues'}
            </span>
          </div>
        </div>
        
        <nav className="navigation">
          <button 
            className={`nav-button ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            Test Dashboard
          </button>
          <button 
            className={`nav-button ${activeTab === 'generator' ? 'active' : ''}`}
            onClick={() => setActiveTab('generator')}
          >
            AI Generator
          </button>
          <button 
            className={`nav-button ${activeTab === 'performance' ? 'active' : ''}`}
            onClick={() => setActiveTab('performance')}
          >
            Performance Monitor
          </button>
        </nav>
      </header>

      <main className="app-main">
        {renderActiveComponent()}
      </main>
    </div>
  );
}

export default App;
