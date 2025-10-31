import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import MetricsChart from './components/MetricsChart';
import SystemHealth from './components/SystemHealth';
import AlertsPanel from './components/AlertsPanel';

function App() {
  const [dashboardStats, setDashboardStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Get API base URL from environment variable or use proxy for local development
  const API_BASE_URL = process.env.REACT_APP_API_URL || '';

  useEffect(() => {
    fetchDashboardStats();
    const interval = setInterval(fetchDashboardStats, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/dashboard/stats`);
      const data = await response.json();
      setDashboardStats(data);
      
      // Check for alerts
      const newAlerts = [];
      if (data.systemHealth.cpu > 80) {
        newAlerts.push({
          id: 'cpu_high',
          severity: 'warning',
          message: `High CPU usage: ${data.systemHealth.cpu}%`,
          timestamp: new Date().toISOString()
        });
      }
      if (data.errorRate > 10) {
        newAlerts.push({
          id: 'error_rate_high',
          severity: 'critical',
          message: `High error rate: ${data.errorRate}%`,
          timestamp: new Date().toISOString()
        });
      }
      setAlerts(newAlerts);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      setLoading(false);
    }
  };

  const simulateLoad = async () => {
    try {
      await fetch(`${API_BASE_URL}/api/simulate/load`, { method: 'POST' });
      fetchDashboardStats();
    } catch (error) {
      console.error('Error simulating load:', error);
    }
  };

  const simulateError = async () => {
    try {
      await fetch(`${API_BASE_URL}/api/simulate/error`, { method: 'POST' });
    } catch (error) {
      // Expected error for testing
      fetchDashboardStats();
    }
  };

  if (loading) {
    return (
      <div className="app">
        <div className="loading">Loading monitoring dashboard...</div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎯 Quiz Platform Monitoring Dashboard</h1>
        <div className="header-controls">
          <button onClick={simulateLoad} className="btn btn-primary">
            Simulate Load
          </button>
          <button onClick={simulateError} className="btn btn-warning">
            Test Alerting
          </button>
        </div>
      </header>

      <div className="dashboard-container">
        <div className="dashboard-row">
          <Dashboard stats={dashboardStats} />
        </div>
        
        <div className="dashboard-row">
          <div className="dashboard-col">
            <SystemHealth health={dashboardStats?.systemHealth} />
          </div>
          <div className="dashboard-col">
            <AlertsPanel alerts={alerts} />
          </div>
        </div>
        
        <div className="dashboard-row">
          <MetricsChart stats={dashboardStats} />
        </div>
      </div>
    </div>
  );
}

export default App;
