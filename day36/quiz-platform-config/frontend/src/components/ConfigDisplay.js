import React, { useState, useEffect } from 'react';

const ConfigDisplay = () => {
  const [config, setConfig] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchConfiguration();
    fetchHealth();
  }, []);

  const fetchConfiguration = async () => {
    try {
      const response = await fetch('/config');
      if (response.ok) {
        const data = await response.json();
        setConfig(data);
      } else if (response.status !== 404) {
        setError('Failed to fetch configuration');
      }
    } catch (err) {
      console.error('Config fetch error:', err);
    }
  };

  const fetchHealth = async () => {
    try {
      const response = await fetch('/health');
      const data = await response.json();
      setHealth(data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch health status');
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    return status === 'healthy' ? '#10B981' : '#EF4444';
  };

  const getEnvironmentColor = (env) => {
    const colors = {
      development: '#3B82F6',
      testing: '#F59E0B',
      production: '#10B981'
    };
    return colors[env] || '#6B7280';
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <span style={{ marginLeft: '8px', color: '#6B7280' }}>Loading configuration...</span>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <h1 className="dashboard-title">
        Environment Configuration Dashboard
      </h1>

        {/* Environment Status */}
        {health && (
          <div className="status-grid">
            <div className="status-card">
              <div className="status-card-header">
                <span className="status-label">Environment</span>
                <span 
                  className="status-value"
                  style={{ backgroundColor: getEnvironmentColor(health.environment) }}
                >
                  {health.environment.toUpperCase()}
                </span>
              </div>
            </div>

            <div className="status-card">
              <div className="status-card-header">
                <span className="status-label">System Status</span>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <div 
                    className="status-indicator"
                    style={{ backgroundColor: getStatusColor(health.status) }}
                  ></div>
                  <span style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>
                    {health.status.toUpperCase()}
                  </span>
                </div>
              </div>
            </div>

            <div className="status-card">
              <div className="status-card-header">
                <span className="status-label">Services</span>
                <div style={{ fontSize: '12px' }}>
                  {Object.entries(health.services || {}).map(([service, status]) => (
                    <div key={service} style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                      <div 
                        className="status-indicator"
                        style={{ width: '8px', height: '8px', backgroundColor: getStatusColor(status) }}
                      ></div>
                      <span>{service}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Configuration Details */}
        {config && (
          <div className="config-section">
            <h2 className="config-title">
              Configuration Details
            </h2>
            <div className="config-grid">
              {Object.entries(config.configuration || {}).map(([section, values]) => (
                <div key={section} className="config-card">
                  <h3 className="config-card-title">
                    {section.replace('_', ' ')}
                  </h3>
                  <div>
                    {typeof values === 'object' ? (
                      Object.entries(values).map(([key, value]) => (
                        <div key={key} className="config-item">
                          <span className="config-key">{key}:</span>
                          <span className="config-value">
                            {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                          </span>
                        </div>
                      ))
                    ) : (
                      <div className="config-value">{String(values)}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Features Status */}
        {health && health.features && (
          <div className="config-section">
            <h2 className="config-title">
              Feature Flags
            </h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px' }}>
              {Object.entries(health.features).map(([feature, enabled]) => (
                <div key={feature} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div 
                    className="status-indicator"
                    style={{ backgroundColor: enabled ? '#10B981' : '#EF4444' }}
                  ></div>
                  <span style={{ fontSize: '14px', color: '#374151', textTransform: 'capitalize' }}>
                    {feature.replace('_', ' ')}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {error && (
          <div className="error-container">
            <div className="error-icon">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <p className="error-message">{error}</p>
          </div>
        )}
    </div>
  );
};

export default ConfigDisplay;
