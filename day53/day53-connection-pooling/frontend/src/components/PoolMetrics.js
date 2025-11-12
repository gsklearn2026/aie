import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

function PoolMetrics() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/metrics/pools`);
        setMetrics(response.data.metrics);
        setError(null);
      } catch (err) {
        setError('Failed to fetch metrics');
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 2000);

    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="loading">Loading metrics...</div>;
  if (error) return <div className="error-message">{error}</div>;

  const db = metrics.database;
  const gemini = metrics.gemini_ai;

  return (
    <div className="metrics-dashboard">
      <div className="metric-card">
        <h3>🗄️ Database Pool</h3>
        <div className="metric-item">
          <span className="metric-label">Current Usage:</span>
          <span className="metric-value">{db.current_usage} / {db.max_connections}</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Available:</span>
          <span className="metric-value">{db.available}</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Total Checkouts:</span>
          <span className="metric-value">{db.total_checkouts}</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Total Returns:</span>
          <span className="metric-value">{db.total_returns}</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Peak Usage:</span>
          <span className="metric-value">{db.peak_usage}</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Reuse Rate:</span>
          <span className="metric-value">{db.reuse_rate.toFixed(2)}%</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Uptime:</span>
          <span className="metric-value">{Math.floor(db.uptime_seconds)}s</span>
        </div>
      </div>

      <div className="metric-card">
        <h3>🤖 Gemini AI Pool</h3>
        <div className="metric-item">
          <span className="metric-label">Current Usage:</span>
          <span className="metric-value">{gemini.current_usage} / {gemini.pool_size}</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Available:</span>
          <span className="metric-value">{gemini.available}</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Total Requests:</span>
          <span className="metric-value">{gemini.total_requests}</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Rate Limited:</span>
          <span className="metric-value">{gemini.total_rate_limited}</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Current Rate:</span>
          <span className="metric-value">{gemini.current_rate} / {gemini.rate_limit_per_min} per min</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Uptime:</span>
          <span className="metric-value">{Math.floor(gemini.uptime_seconds)}s</span>
        </div>
      </div>
    </div>
  );
}

export default PoolMetrics;
