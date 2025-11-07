import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

function App() {
  const [metrics, setMetrics] = useState(null);
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFields, setSelectedFields] = useState('');

  const API_BASE = 'http://localhost:8000';

  useEffect(() => {
    fetchMetrics();
    fetchQuizzes();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/metrics/performance`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setMetrics(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching metrics:', error);
      setLoading(false);
    }
  };

  const fetchQuizzes = async (fields = '') => {
    try {
      const url = fields 
        ? `${API_BASE}/api/quizzes?fields=${fields}&limit=10`
        : `${API_BASE}/api/quizzes?limit=10`;
      
      const startTime = performance.now();
      const response = await fetch(url);
      const endTime = performance.now();
      
      const data = await response.json();
      
      // Extract compression info from headers
      const originalSize = response.headers.get('X-Original-Size');
      const compressedSize = response.headers.get('X-Compressed-Size');
      const compressionRatio = response.headers.get('X-Compression-Ratio');
      
      setQuizzes({
        data: data.quizzes || [],
        responseTime: Math.round(endTime - startTime),
        originalSize: originalSize ? `${Math.round(originalSize / 1024)}KB` : 'N/A',
        compressedSize: compressedSize ? `${Math.round(compressedSize / 1024)}KB` : 'N/A',
        compressionRatio: compressionRatio || 'N/A'
      });
    } catch (error) {
      console.error('Error fetching quizzes:', error);
    }
  };

  const handleFieldFilterChange = (e) => {
    setSelectedFields(e.target.value);
  };

  const applyFieldFilter = () => {
    fetchQuizzes(selectedFields);
  };

  if (loading) {
    return <div className="loading">Loading Dashboard...</div>;
  }

  const performanceData = metrics?.performance_by_endpoint || [];
  const cacheStats = metrics?.cache_statistics || {};

  return (
    <div className="App">
      <header className="header">
        <h1>🚀 API Response Optimization Dashboard</h1>
        <p>Real-time Performance Monitoring</p>
      </header>

      <div className="container">
        {/* Summary Cards */}
        <div className="cards-grid">
          <div className="card card-green">
            <h3>Cache Hit Rate</h3>
            <div className="card-value">{cacheStats.hit_rate || 0}%</div>
            <p className="card-subtitle">
              {cacheStats.keyspace_hits || 0} hits / {cacheStats.keyspace_misses || 0} misses
            </p>
          </div>
          
          <div className="card card-blue">
            <h3>Avg Response Time</h3>
            <div className="card-value">
              {performanceData.length > 0 
                ? Math.round(performanceData.reduce((sum, p) => sum + p.avg_response_time_ms, 0) / performanceData.length)
                : 0}ms
            </div>
            <p className="card-subtitle">Across all endpoints</p>
          </div>
          
          <div className="card card-orange">
            <h3>Avg Compression</h3>
            <div className="card-value">
              {performanceData.length > 0 
                ? Math.round(performanceData.reduce((sum, p) => sum + p.compression_saving_percent, 0) / performanceData.length)
                : 0}%
            </div>
            <p className="card-subtitle">Bandwidth saved</p>
          </div>
          
          <div className="card card-purple">
            <h3>Total Requests</h3>
            <div className="card-value">
              {performanceData.reduce((sum, p) => sum + p.total_requests, 0)}
            </div>
            <p className="card-subtitle">Since last restart</p>
          </div>
        </div>

        {/* Response Time Chart */}
        <div className="chart-container">
          <h2>Response Time by Endpoint</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="endpoint" angle={-45} textAnchor="end" height={100} />
              <YAxis label={{ value: 'Response Time (ms)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="avg_response_time_ms" fill="#4CAF50" name="Avg Response Time" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Compression Chart */}
        <div className="chart-container">
          <h2>Compression Efficiency</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="endpoint" angle={-45} textAnchor="end" height={100} />
              <YAxis label={{ value: 'Size (KB)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="avg_size_kb" fill="#FF9800" name="Original Size" />
              <Bar dataKey="avg_compressed_kb" fill="#2196F3" name="Compressed Size" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Field Filter Demo */}
        <div className="demo-section">
          <h2>Live Optimization Demo</h2>
          <div className="filter-controls">
            <input
              type="text"
              placeholder="e.g., id,title,category"
              value={selectedFields}
              onChange={handleFieldFilterChange}
              className="filter-input"
            />
            <button onClick={applyFieldFilter} className="btn-primary">
              Apply Field Filter
            </button>
            <button onClick={() => { setSelectedFields(''); fetchQuizzes(''); }} className="btn-secondary">
              Clear Filter
            </button>
          </div>
          
          {quizzes.data && (
            <div className="result-stats">
              <div className="stat">
                <strong>Response Time:</strong> {quizzes.responseTime}ms
              </div>
              <div className="stat">
                <strong>Original Size:</strong> {quizzes.originalSize}
              </div>
              <div className="stat">
                <strong>Compressed Size:</strong> {quizzes.compressedSize}
              </div>
              <div className="stat">
                <strong>Compression Ratio:</strong> {quizzes.compressionRatio}
              </div>
            </div>
          )}
          
          <div className="quiz-list">
            <h3>Quizzes ({quizzes.data?.length || 0})</h3>
            {quizzes.data?.map((quiz) => (
              <div key={quiz.id} className="quiz-item">
                {Object.entries(quiz).map(([key, value]) => (
                  <div key={key}>
                    <strong>{key}:</strong> {value}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>

        {/* Performance Table */}
        <div className="table-container">
          <h2>Detailed Performance Metrics</h2>
          <table className="performance-table">
            <thead>
              <tr>
                <th>Endpoint</th>
                <th>Avg Response (ms)</th>
                <th>Original (KB)</th>
                <th>Compressed (KB)</th>
                <th>Compression %</th>
                <th>Cache Hit %</th>
                <th>Total Requests</th>
              </tr>
            </thead>
            <tbody>
              {performanceData.map((stat, idx) => (
                <tr key={idx}>
                  <td>{stat.endpoint}</td>
                  <td>{stat.avg_response_time_ms}</td>
                  <td>{stat.avg_size_kb}</td>
                  <td>{stat.avg_compressed_kb}</td>
                  <td className="success">{stat.compression_saving_percent}%</td>
                  <td className="success">{stat.cache_hit_rate}%</td>
                  <td>{stat.total_requests}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default App;
