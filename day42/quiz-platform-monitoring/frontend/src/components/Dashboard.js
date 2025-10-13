import React from 'react';

const Dashboard = ({ stats }) => {
  if (!stats) return <div>Loading dashboard...</div>;

  const formatNumber = (num) => {
    return num?.toLocaleString() || '0';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return '#28a745';
      case 'warning': return '#ffc107';
      case 'critical': return '#dc3545';
      default: return '#6c757d';
    }
  };

  return (
    <div className="dashboard-metrics">
      <div className="metric-card">
        <div className="metric-header">
          <h3>👥 Active Users</h3>
        </div>
        <div className="metric-value">
          {formatNumber(stats.activeUsers)}
        </div>
        <div className="metric-trend positive">
          +5% from last hour
        </div>
      </div>

      <div className="metric-card">
        <div className="metric-header">
          <h3>❓ Questions Answered</h3>
        </div>
        <div className="metric-value">
          {formatNumber(stats.questionsAnswered)}
        </div>
        <div className="metric-trend positive">
          +12% from last hour
        </div>
      </div>

      <div className="metric-card">
        <div className="metric-header">
          <h3>⏱️ Avg Response Time</h3>
        </div>
        <div className="metric-value">
          {(stats.avgResponseTime * 1000).toFixed(0)}ms
        </div>
        <div className="metric-trend negative">
          +2ms from last hour
        </div>
      </div>

      <div className="metric-card">
        <div className="metric-header">
          <h3>🚨 Error Rate</h3>
        </div>
        <div className="metric-value">
          {stats.errorRate.toFixed(1)}%
        </div>
        <div className={`metric-trend ${stats.errorRate < 1 ? 'positive' : 'negative'}`}>
          {stats.errorRate < 1 ? 'Normal' : 'High'}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
