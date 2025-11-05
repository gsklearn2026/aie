import React, { useState, useEffect } from 'react';
import './App.css';
import PerformanceDashboard from './components/PerformanceDashboard';
import QuizList from './components/QuizList';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

function App() {
  const [performanceData, setPerformanceData] = useState(null);
  const [queryStats, setQueryStats] = useState([]);
  const [indexUsage, setIndexUsage] = useState([]);

  useEffect(() => {
    fetchPerformanceData();
    const interval = setInterval(fetchPerformanceData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchPerformanceData = async () => {
    try {
      const [statsRes, queryRes, indexRes] = await Promise.all([
        axios.get(`${API_URL}/api/stats`),
        axios.get(`${API_URL}/api/performance/query-stats`),
        axios.get(`${API_URL}/api/performance/index-usage`)
      ]);

      setPerformanceData(statsRes.data);
      setQueryStats(queryRes.data.query_stats || []);
      setIndexUsage(indexRes.data.indexes || []);
    } catch (error) {
      console.error('Error fetching performance data:', error);
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🚀 Quiz Platform Performance Dashboard</h1>
        <p>Real-time Database Query Optimization Monitoring</p>
      </header>

      <div className="dashboard-container">
        <PerformanceDashboard 
          performanceData={performanceData}
          queryStats={queryStats}
          indexUsage={indexUsage}
        />
        <QuizList />
      </div>
    </div>
  );
}

export default App;
