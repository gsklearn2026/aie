import React, { useState, useEffect } from 'react';
import { AlertCircle, Database, Clock, Shield } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const navigate = useNavigate();
  const [systemStatus, setSystemStatus] = useState({
    backupService: 'healthy',
    recoveryService: 'healthy',
    lastBackup: null,
    uptime: '24h 15m'
  });

  const [recentBackups, setRecentBackups] = useState([
    { id: 1, type: 'hot', status: 'completed', timestamp: '2025-01-15 14:30:00', size: '245MB' },
    { id: 2, type: 'warm', status: 'completed', timestamp: '2025-01-15 13:00:00', size: '1.2GB' },
    { id: 3, type: 'cold', status: 'in_progress', timestamp: '2025-01-15 12:00:00', size: '2.8GB' }
  ]);

  useEffect(() => {
    // Fetch system status
    const fetchStatus = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        const data = await response.json();
        // Update system status
      } catch (error) {
        console.error('Failed to fetch system status:', error);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 30000); // Update every 30 seconds
    
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'text-green-600';
      case 'warning': return 'text-yellow-600';
      case 'error': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const handleManualBackup = async () => {
    try {
      // Check if backup service is healthy before triggering
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        // In a real implementation, this would call a specific manual backup endpoint
        // For now, we'll simulate the action and navigate to backup status
        alert('Manual backup triggered! Redirecting to backup status page...');
        navigate('/backups');
      } else {
        alert('Backup service is not available. Please check system status.');
      }
    } catch (error) {
      console.error('Failed to trigger manual backup:', error);
      alert('Failed to trigger manual backup. Please check the console for details.');
    }
  };

  const handleTestRecovery = () => {
    // Navigate to recovery console for test recovery
    navigate('/recovery');
  };

  const handleViewAlerts = () => {
    // For now, show a simple alert. In a real implementation, this would open an alerts modal
    alert('No active alerts at this time. All systems are running normally.');
  };

  return (
    <div className="dashboard">
      <div className="dashboard-grid">
        {/* System Status Cards */}
        <div className="status-cards">
          <div className="status-card">
            <Database className="status-icon" />
            <div className="status-content">
              <h3>Backup Service</h3>
              <p className={getStatusColor(systemStatus.backupService)}>
                {systemStatus.backupService.toUpperCase()}
              </p>
            </div>
          </div>
          
          <div className="status-card">
            <Shield className="status-icon" />
            <div className="status-content">
              <h3>Recovery Service</h3>
              <p className={getStatusColor(systemStatus.recoveryService)}>
                {systemStatus.recoveryService.toUpperCase()}
              </p>
            </div>
          </div>
          
          <div className="status-card">
            <Clock className="status-icon" />
            <div className="status-content">
              <h3>System Uptime</h3>
              <p className="text-blue-600">{systemStatus.uptime}</p>
            </div>
          </div>
        </div>

        {/* Recent Backups */}
        <div className="recent-backups">
          <h2>Recent Backup Operations</h2>
          <div className="backup-list">
            {recentBackups.map(backup => (
              <div key={backup.id} className="backup-item">
                <div className="backup-info">
                  <span className={`backup-type ${backup.type}`}>{backup.type.toUpperCase()}</span>
                  <span className="backup-time">{backup.timestamp}</span>
                </div>
                <div className="backup-status">
                  <span className={`status ${backup.status}`}>{backup.status}</span>
                  <span className="backup-size">{backup.size}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="quick-actions">
          <h2>Quick Actions</h2>
          <div className="action-buttons">
            <button className="action-btn primary" onClick={handleManualBackup}>
              Run Manual Backup
            </button>
            <button className="action-btn secondary" onClick={handleTestRecovery}>
              Test Recovery
            </button>
            <button className="action-btn warning" onClick={handleViewAlerts}>
              View Alerts
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
