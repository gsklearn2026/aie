import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './MetricsDashboard.css';

function MetricsDashboard({ apiBaseUrl, profiles }) {
  const [selectedProfile, setSelectedProfile] = useState('');
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);

  const profileNames = Object.keys(profiles);

  useEffect(() => {
    if (profileNames.length > 0 && !selectedProfile) {
      setSelectedProfile(profileNames[0]);
    }
  }, [profileNames, selectedProfile]);

  useEffect(() => {
    if (selectedProfile) {
      fetchMetrics();
    }
  }, [selectedProfile]);

  const fetchMetrics = async () => {
    setLoading(true);
    try {
      const response = await axios.get(
        `${apiBaseUrl}/api/generation/metrics/${selectedProfile}?days=7`
      );
      setMetrics(response.data);
    } catch (err) {
      console.error('Failed to fetch metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat().format(Math.round(num));
  };

  return (
    <div className="metrics-dashboard">
      <div className="dashboard-header">
        <h2>Performance Metrics Dashboard</h2>
        <div className="profile-selector">
          <label>Select Profile:</label>
          <select value={selectedProfile} onChange={(e) => setSelectedProfile(e.target.value)}>
            {profileNames.map(name => (
              <option key={name} value={name}>{name}</option>
            ))}
          </select>
        </div>
      </div>

      {loading && <div className="loading">Loading metrics...</div>}

      {metrics && !loading && (
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-card-header">
              <div className="metric-icon">📊</div>
              <div className="metric-content">
                <div className="metric-label">Total Requests</div>
                <div className="metric-value">{formatNumber(metrics.total_requests)}</div>
              </div>
            </div>
          </div>

          <div className="metric-card success">
            <div className="metric-card-header">
              <div className="metric-icon">✅</div>
              <div className="metric-content">
                <div className="metric-label">Success Rate</div>
                <div className="metric-value">{metrics.success_rate.toFixed(1)}%</div>
              </div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-card-header">
              <div className="metric-icon">⚡</div>
              <div className="metric-content">
                <div className="metric-label">Avg Latency</div>
                <div className="metric-value">{metrics.avg_latency_ms.toFixed(0)}ms</div>
              </div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-card-header">
              <div className="metric-icon">💰</div>
              <div className="metric-content">
                <div className="metric-label">Avg Cost</div>
                <div className="metric-value">${metrics.avg_cost.toFixed(4)}</div>
              </div>
            </div>
          </div>

          <div className="metric-card quality">
            <div className="metric-card-header">
              <div className="metric-icon">⭐</div>
              <div className="metric-content">
                <div className="metric-label">Avg Quality</div>
                <div className="metric-value">{metrics.avg_quality_score.toFixed(2)}/5.0</div>
              </div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-card-header">
              <div className="metric-icon">❌</div>
              <div className="metric-content">
                <div className="metric-label">Failed Requests</div>
                <div className="metric-value">{formatNumber(metrics.failed_requests)}</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {selectedProfile && profiles[selectedProfile] && (
        <div className="profile-details-card">
          <h3>Profile Configuration</h3>
          <div className="config-grid">
            <div className="config-item">
              <span className="config-label">Model:</span>
              <span className="config-value">{profiles[selectedProfile].model}</span>
            </div>
            <div className="config-item">
              <span className="config-label">Cost Tier:</span>
              <span className={`config-value badge ${profiles[selectedProfile].cost_tier}`}>
                {profiles[selectedProfile].cost_tier}
              </span>
            </div>
            <div className="config-item">
              <span className="config-label">Temperature:</span>
              <span className="config-value">{profiles[selectedProfile].temperature}</span>
            </div>
            <div className="config-item">
              <span className="config-label">Max Tokens:</span>
              <span className="config-value">{profiles[selectedProfile].max_tokens}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default MetricsDashboard;
