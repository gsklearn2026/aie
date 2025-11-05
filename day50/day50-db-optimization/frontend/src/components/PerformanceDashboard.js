import React from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './PerformanceDashboard.css';

function PerformanceDashboard({ performanceData, queryStats, indexUsage }) {
  if (!performanceData) {
    return <div className="loading">Loading performance data...</div>;
  }

  // Handle case when no requests have been made yet
  const hasData = performanceData && !performanceData.message && performanceData.total_requests > 0;
  const avgResponseTime = hasData ? (performanceData.avg_response_time * 1000).toFixed(2) : '0.00';
  const maxResponseTime = hasData ? (performanceData.max_response_time * 1000).toFixed(2) : '0.00';
  const totalRequests = hasData ? performanceData.total_requests : 0;
  const slowRequests = hasData ? performanceData.slow_requests : 0;

  const topQueries = queryStats.slice(0, 5);
  // Sort indexes by scans descending and take top 5
  const sortedIndexes = [...indexUsage].sort((a, b) => (b.scans || 0) - (a.scans || 0));
  const topIndexes = sortedIndexes.slice(0, 5);

  return (
    <div className="performance-dashboard">
      <div className="metrics-grid">
        <div className="metric-card">
          <h3>Average Response Time</h3>
          <div className="metric-value">
            {avgResponseTime} ms
          </div>
          <div className="metric-label">Target: &lt; 100ms</div>
        </div>

        <div className="metric-card">
          <h3>Max Response Time</h3>
          <div className="metric-value">
            {maxResponseTime} ms
          </div>
          <div className="metric-label">Peak latency</div>
        </div>

        <div className="metric-card">
          <h3>Total Requests</h3>
          <div className="metric-value">
            {totalRequests}
          </div>
          <div className="metric-label">Since server start</div>
        </div>

        <div className="metric-card alert">
          <h3>Slow Requests</h3>
          <div className="metric-value">
            {slowRequests}
          </div>
          <div className="metric-label">&gt; 500ms threshold</div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-container">
          <h3>Top 5 Slowest Queries</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topQueries}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="query" angle={-45} textAnchor="end" height={100} />
              <YAxis label={{ value: 'Time (ms)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="avg_time" fill="#10b981" name="Avg Time (ms)" />
              <Bar dataKey="max_time" fill="#f97316" name="Max Time (ms)" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Top 5 Most Used Indexes</h3>
          {topIndexes.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={topIndexes}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="index" angle={-45} textAnchor="end" height={100} />
                <YAxis label={{ value: 'Scans', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="scans" fill="#10b981" name="Index Scans" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="no-data">No index usage data available. Make some queries to see index statistics.</div>
          )}
        </div>
      </div>

      <div className="query-stats-table">
        <h3>Query Performance Details</h3>
        <table>
          <thead>
            <tr>
              <th>Query</th>
              <th>Count</th>
              <th>Avg Time (ms)</th>
              <th>Max Time (ms)</th>
              <th>Total Time (ms)</th>
            </tr>
          </thead>
          <tbody>
            {queryStats.map((stat, index) => (
              <tr key={index} className={stat.avg_time > 100 ? 'slow-query' : ''}>
                <td>{stat.query}</td>
                <td>{stat.count}</td>
                <td>{stat.avg_time}</td>
                <td>{stat.max_time}</td>
                <td>{stat.total_time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default PerformanceDashboard;
