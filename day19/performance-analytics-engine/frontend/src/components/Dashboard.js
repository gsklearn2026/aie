import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { analyticsService } from '../services/analyticsService';
import { websocketService } from '../services/websocketService';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [realTimeData, setRealTimeData] = useState(null);

  useEffect(() => {
    loadDashboardData();
    
    // Setup WebSocket for real-time updates
    websocketService.connect((data) => {
      if (data.type === 'dashboard_update') {
        setRealTimeData(data.data);
      }
    });

    return () => {
      websocketService.disconnect();
    };
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const data = await analyticsService.getDashboardMetrics(7);
      setDashboardData(data);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading performance analytics...</p>
      </div>
    );
  }

  if (!dashboardData) {
    return <div className="error-message">Failed to load dashboard data</div>;
  }

  const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#8dd1e1'];

  return (
    <div className="dashboard">
      <h1>Performance Analytics Dashboard</h1>
      
      {realTimeData && (
        <div className="real-time-alert">
          <span className="pulse-indicator"></span>
          Live Update: {realTimeData.total_attempts_today} attempts today, 
          {realTimeData.average_score_today.toFixed(1)}% avg score
        </div>
      )}

      <div className="metrics-grid">
        <div className="metric-card">
          <h3>Total Attempts</h3>
          <div className="metric-value">{dashboardData.overview.total_attempts.toLocaleString()}</div>
          <div className="metric-period">Last 7 days</div>
        </div>
        
        <div className="metric-card">
          <h3>Average Score</h3>
          <div className="metric-value">{dashboardData.overview.average_score_percentage.toFixed(1)}%</div>
          <div className="metric-period">System-wide average</div>
        </div>
        
        <div className="metric-card">
          <h3>Active Users</h3>
          <div className="metric-value">{dashboardData.overview.active_users}</div>
          <div className="metric-period">Unique learners</div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-container">
          <h3>Daily Activity</h3>
          <LineChart width={500} height={300} data={dashboardData.daily_activity}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="attempts" stroke="#8884d8" strokeWidth={2} />
          </LineChart>
        </div>

        <div className="chart-container">
          <h3>Topic Performance</h3>
          <BarChart width={500} height={300} data={dashboardData.topic_performance.slice(0, 5)}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="topic_id" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="average_score_percentage" fill="#82ca9d" />
          </BarChart>
        </div>

        <div className="chart-container">
          <h3>Attempt Distribution</h3>
          <PieChart width={400} height={300}>
            <Pie
              data={dashboardData.topic_performance.slice(0, 5)}
              cx={200}
              cy={150}
              outerRadius={80}
              fill="#8884d8"
              dataKey="attempts"
              label={({topic_id, attempts}) => `${topic_id}: ${attempts}`}
            >
              {dashboardData.topic_performance.slice(0, 5).map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </div>
      </div>

      <div className="insights-section">
        <h3>System Insights</h3>
        <div className="insights-grid">
          {dashboardData.topic_performance
            .filter(topic => topic.average_score_percentage < 60)
            .slice(0, 3)
            .map((topic, index) => (
              <div key={index} className="insight-card warning">
                <h4>⚠️ Challenging Topic</h4>
                <p><strong>{topic.topic_id}</strong> has a low average score of {topic.average_score_percentage.toFixed(1)}%</p>
                <p>Consider reviewing content or providing additional resources</p>
              </div>
            ))
          }
          
          {dashboardData.topic_performance
            .filter(topic => topic.average_score_percentage > 85)
            .slice(0, 2)
            .map((topic, index) => (
              <div key={index} className="insight-card success">
                <h4>✅ High Performing Topic</h4>
                <p><strong>{topic.topic_id}</strong> shows excellent performance at {topic.average_score_percentage.toFixed(1)}%</p>
                <p>Great content quality - consider using as a template</p>
              </div>
            ))
          }
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
