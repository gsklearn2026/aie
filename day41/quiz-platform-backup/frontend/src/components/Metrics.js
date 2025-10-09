import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Database, Clock, Shield } from 'lucide-react';

const Metrics = () => {
  const [metrics, setMetrics] = useState(null);
  const [timeRange, setTimeRange] = useState('24h');

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000);
    return () => clearInterval(interval);
  }, [timeRange]);

  const fetchMetrics = async () => {
    try {
      const response = await fetch('http://localhost:8000/metrics');
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  };

  // Mock data for demo
  const backupTrendData = [
    { time: '00:00', hot: 4, warm: 1, cold: 0 },
    { time: '04:00', hot: 16, warm: 4, cold: 0 },
    { time: '08:00', hot: 32, warm: 8, cold: 1 },
    { time: '12:00', hot: 48, warm: 12, cold: 1 },
    { time: '16:00', hot: 64, warm: 16, cold: 1 },
    { time: '20:00', hot: 80, warm: 20, cold: 1 },
    { time: '24:00', hot: 96, warm: 24, cold: 2 }
  ];

  const performanceData = [
    { type: 'Hot', duration: 45, size: 245 },
    { type: 'Warm', duration: 180, size: 1200 },
    { type: 'Cold', duration: 720, size: 2800 }
  ];

  const healthData = [
    { name: 'Healthy', value: 95, color: '#10B981' },
    { name: 'Warning', value: 4, color: '#F59E0B' },
    { name: 'Error', value: 1, color: '#EF4444' }
  ];

  return (
    <div className="metrics-dashboard">
      <div className="metrics-header">
        <h1>System Metrics</h1>
        <div className="time-selector">
          <button 
            className={timeRange === '1h' ? 'active' : ''}
            onClick={() => setTimeRange('1h')}
          >
            1H
          </button>
          <button 
            className={timeRange === '24h' ? 'active' : ''}
            onClick={() => setTimeRange('24h')}
          >
            24H
          </button>
          <button 
            className={timeRange === '7d' ? 'active' : ''}
            onClick={() => setTimeRange('7d')}
          >
            7D
          </button>
        </div>
      </div>

      <div className="metrics-grid">
        {/* Key Metrics Cards */}
        <div className="metrics-cards">
          <div className="metric-card">
            <TrendingUp className="metric-icon" />
            <div className="metric-content">
              <h3>Success Rate</h3>
              <p className="metric-value">95.2%</p>
              <span className="metric-trend positive">+2.1% vs last week</span>
            </div>
          </div>

          <div className="metric-card">
            <Database className="metric-icon" />
            <div className="metric-content">
              <h3>Total Backups</h3>
              <p className="metric-value">1,247</p>
              <span className="metric-trend positive">+156 this week</span>
            </div>
          </div>

          <div className="metric-card">
            <Clock className="metric-icon" />
            <div className="metric-content">
              <h3>Avg Duration</h3>
              <p className="metric-value">3.2min</p>
              <span className="metric-trend negative">+0.4min vs last week</span>
            </div>
          </div>

          <div className="metric-card">
            <Shield className="metric-icon" />
            <div className="metric-content">
              <h3>System Health</h3>
              <p className="metric-value">98.7%</p>
              <span className="metric-trend positive">+1.2% vs last week</span>
            </div>
          </div>
        </div>

        {/* Backup Trends Chart */}
        <div className="chart-container">
          <h2>Backup Trends ({timeRange})</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={backupTrendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="hot" stroke="#EF4444" strokeWidth={2} />
              <Line type="monotone" dataKey="warm" stroke="#F59E0B" strokeWidth={2} />
              <Line type="monotone" dataKey="cold" stroke="#3B82F6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Performance Chart */}
        <div className="chart-container">
          <h2>Backup Performance</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="type" />
              <YAxis yAxisId="duration" orientation="left" />
              <YAxis yAxisId="size" orientation="right" />
              <Tooltip />
              <Bar yAxisId="duration" dataKey="duration" fill="#8884d8" name="Duration (min)" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Health Distribution */}
        <div className="chart-container">
          <h2>System Health Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={healthData}
                cx="50%"
                cy="50%"
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}%`}
              >
                {healthData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Metrics;
