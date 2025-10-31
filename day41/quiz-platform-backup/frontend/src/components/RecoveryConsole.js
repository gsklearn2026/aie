import React, { useState, useEffect } from 'react';
import { PlayCircle, StopCircle, Clock, AlertTriangle, CheckCircle } from 'lucide-react';

const RecoveryConsole = () => {
  const [activeRecoveries, setActiveRecoveries] = useState([]);
  const [recoveryHistory, setRecoveryHistory] = useState([]);
  const [showNewRecoveryModal, setShowNewRecoveryModal] = useState(false);
  const [availableBackups, setAvailableBackups] = useState([]);

  useEffect(() => {
    fetchRecoveryData();
    const interval = setInterval(fetchRecoveryData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchRecoveryData = async () => {
    try {
      const [historyRes, backupsRes] = await Promise.all([
        fetch('http://localhost:8000/recovery/history'),
        fetch('http://localhost:8000/backups')
      ]);
      
      const historyData = await historyRes.json();
      const backupsData = await backupsRes.json();
      
      setRecoveryHistory(historyData.history || []);
      setAvailableBackups(backupsData.backups || []);
    } catch (error) {
      console.error('Failed to fetch recovery data:', error);
    }
  };

  const startRecovery = async (recoveryData) => {
    try {
      const response = await fetch('http://localhost:8000/recovery/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(recoveryData)
      });
      
      if (response.ok) {
        const result = await response.json();
        setShowNewRecoveryModal(false);
        fetchRecoveryData();
      }
    } catch (error) {
      console.error('Failed to start recovery:', error);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="text-green-500" size={20} />;
      case 'failed':
        return <AlertTriangle className="text-red-500" size={20} />;
      case 'running':
        return <PlayCircle className="text-blue-500" size={20} />;
      default:
        return <Clock className="text-yellow-500" size={20} />;
    }
  };

  return (
    <div className="recovery-console">
      <div className="console-header">
        <h1>Recovery Console</h1>
        <button 
          className="btn-primary"
          onClick={() => setShowNewRecoveryModal(true)}
        >
          Start New Recovery
        </button>
      </div>

      <div className="console-content">
        {/* Recovery History */}
        <div className="recovery-section">
          <h2>Recovery Operations</h2>
          <div className="recovery-list">
            {recoveryHistory.map((recovery, index) => (
              <div key={index} className="recovery-item">
                <div className="recovery-info">
                  {getStatusIcon(recovery.status)}
                  <div className="recovery-details">
                    <h3>Recovery {recovery.recovery_id}</h3>
                    <p>{recovery.message}</p>
                    <div className="recovery-meta">
                      <span>Type: {recovery.recovery_type}</span>
                      <span>Started: {new Date(recovery.started_at).toLocaleString()}</span>
                      {recovery.completed_at && (
                        <span>Completed: {new Date(recovery.completed_at).toLocaleString()}</span>
                      )}
                    </div>
                  </div>
                </div>
                
                {recovery.status === 'running' && (
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{ width: `${recovery.progress}%` }}
                    />
                    <span className="progress-text">{recovery.progress.toFixed(1)}%</span>
                  </div>
                )}
                
                <div className="recovery-actions">
                  {recovery.status === 'running' && (
                    <button className="btn-danger">Cancel</button>
                  )}
                  <button className="btn-secondary">View Logs</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* New Recovery Modal */}
      {showNewRecoveryModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Start New Recovery</h2>
            <NewRecoveryForm 
              backups={availableBackups}
              onSubmit={startRecovery}
              onCancel={() => setShowNewRecoveryModal(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
};

const NewRecoveryForm = ({ backups, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    recovery_type: 'point_in_time',
    target_time: '',
    backup_file: '',
    dry_run: false
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validate required fields
    if (formData.recovery_type === 'point_in_time' && (!formData.target_time || formData.target_time.trim() === '')) {
      alert('Please select a target time for point-in-time recovery');
      return;
    }
    
    // Prepare the data for submission
    const submitData = {
      recovery_type: formData.recovery_type,
      dry_run: formData.dry_run
    };
    
    // Only include target_time if it's provided and not empty
    if (formData.target_time && formData.target_time.trim() !== '') {
      submitData.target_time = formData.target_time;
    }
    
    // Only include backup_file if it's provided and not empty
    if (formData.backup_file && formData.backup_file.trim() !== '') {
      submitData.backup_file = formData.backup_file;
    }
    
    onSubmit(submitData);
  };

  return (
    <form onSubmit={handleSubmit} className="recovery-form">
      <div className="form-group">
        <label>Recovery Type</label>
        <select 
          value={formData.recovery_type}
          onChange={(e) => setFormData({...formData, recovery_type: e.target.value})}
        >
          <option value="point_in_time">Point-in-Time Recovery</option>
          <option value="full">Full Recovery</option>
        </select>
      </div>

      {formData.recovery_type === 'point_in_time' && (
        <div className="form-group">
          <label>Target Time</label>
          <input 
            type="datetime-local"
            value={formData.target_time}
            onChange={(e) => setFormData({...formData, target_time: e.target.value})}
          />
        </div>
      )}

      <div className="form-group">
        <label>Backup File (optional)</label>
        <select 
          value={formData.backup_file}
          onChange={(e) => setFormData({...formData, backup_file: e.target.value})}
        >
          <option value="">Use most recent backup</option>
          {backups.map((backup, index) => (
            <option key={index} value={backup.file_path}>
              {backup.filename} ({backup.type} - {new Date(backup.created_at).toLocaleDateString()})
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label className="checkbox-label">
          <input 
            type="checkbox"
            checked={formData.dry_run}
            onChange={(e) => setFormData({...formData, dry_run: e.target.checked})}
          />
          Dry run (test recovery without applying changes)
        </label>
      </div>

      <div className="form-actions">
        <button type="button" className="btn-secondary" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn-primary">
          Start Recovery
        </button>
      </div>
    </form>
  );
};

export default RecoveryConsole;
