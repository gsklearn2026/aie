import React from 'react';

const ProviderStatus = ({ providers }) => {
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleTimeString();
  };

  return (
    <div className="provider-status">
      {providers.length === 0 ? (
        <p className="no-data">No provider information available</p>
      ) : (
        <div className="providers-grid">
          {providers.map((provider, index) => (
            <div key={index} className={`provider-card ${provider.is_healthy ? 'healthy' : 'unhealthy'}`}>
              <div className="provider-header">
                <h4 className="provider-name">{provider.provider}</h4>
                <span className={`status-badge ${provider.is_healthy ? 'healthy' : 'unhealthy'}`}>
                  {provider.is_healthy ? '🟢 Healthy' : '🔴 Unhealthy'}
                </span>
              </div>
              
              <div className="provider-details">
                <div className="detail-row">
                  <span className="label">Last Checked:</span>
                  <span className="value">{formatTimestamp(provider.last_checked)}</span>
                </div>
                
                {provider.response_time && (
                  <div className="detail-row">
                    <span className="label">Response Time:</span>
                    <span className="value">{provider.response_time}ms</span>
                  </div>
                )}
                
                <div className="detail-row">
                  <span className="label">Error Count:</span>
                  <span className={`value ${provider.error_count > 0 ? 'error' : ''}`}>
                    {provider.error_count}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProviderStatus;
