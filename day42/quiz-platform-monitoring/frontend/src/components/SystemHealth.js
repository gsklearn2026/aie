import React from 'react';

const SystemHealth = ({ health }) => {
  if (!health) return <div>Loading system health...</div>;

  const getHealthColor = (value, thresholds) => {
    if (value < thresholds.good) return '#28a745';
    if (value < thresholds.warning) return '#ffc107';
    return '#dc3545';
  };

  const cpuColor = getHealthColor(health.cpu, { good: 50, warning: 80 });
  const memoryColor = getHealthColor(health.memory, { good: 60, warning: 80 });

  return (
    <div className="system-health-panel">
      <h3>🖥️ System Health</h3>
      
      <div className="health-metric">
        <div className="health-label">CPU Usage</div>
        <div className="health-bar">
          <div 
            className="health-fill" 
            style={{ width: `${health.cpu}%`, backgroundColor: cpuColor }}
          ></div>
        </div>
        <div className="health-value">{health.cpu.toFixed(1)}%</div>
      </div>

      <div className="health-metric">
        <div className="health-label">Memory Usage</div>
        <div className="health-bar">
          <div 
            className="health-fill" 
            style={{ width: `${health.memory}%`, backgroundColor: memoryColor }}
          ></div>
        </div>
        <div className="health-value">{health.memory.toFixed(1)}%</div>
      </div>

      <div className="health-status">
        <span className={`status-badge status-${health.status}`}>
          {health.status.toUpperCase()}
        </span>
      </div>
    </div>
  );
};

export default SystemHealth;
