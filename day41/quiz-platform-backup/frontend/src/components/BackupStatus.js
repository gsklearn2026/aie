import React, { useState, useEffect } from 'react';
import { Database, Clock, AlertCircle, CheckCircle, RefreshCw } from 'lucide-react';

const BackupStatus = () => {
  const [backups, setBackups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchBackups();
    const interval = setInterval(fetchBackups, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchBackups = async () => {
    try {
      const response = await fetch('http://localhost:8000/backups');
      const data = await response.json();
      setBackups(data.backups || []);
    } catch (error) {
      console.error('Failed to fetch backups:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'hot': return 'bg-red-100 text-red-800';
      case 'warm': return 'bg-yellow-100 text-yellow-800';
      case 'cold': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredBackups = backups.filter(backup => 
    filter === 'all' || backup.type === filter
  );

  if (loading) {
    return (
      <div className="backup-status loading">
        <RefreshCw className="animate-spin" size={32} />
        <p>Loading backup status...</p>
      </div>
    );
  }

  return (
    <div className="backup-status">
      <div className="backup-header">
        <h1>Backup Status</h1>
        <div className="backup-filters">
          <button 
            className={filter === 'all' ? 'active' : ''}
            onClick={() => setFilter('all')}
          >
            All Backups
          </button>
          <button 
            className={filter === 'hot' ? 'active' : ''}
            onClick={() => setFilter('hot')}
          >
            Hot Backups
          </button>
          <button 
            className={filter === 'warm' ? 'active' : ''}
            onClick={() => setFilter('warm')}
          >
            Warm Backups
          </button>
          <button 
            className={filter === 'cold' ? 'active' : ''}
            onClick={() => setFilter('cold')}
          >
            Cold Backups
          </button>
        </div>
      </div>

      <div className="backup-grid">
        {filteredBackups.map((backup, index) => (
          <div key={index} className="backup-card">
            <div className="backup-card-header">
              <Database size={20} />
              <span className={`backup-type-badge ${getTypeColor(backup.type)}`}>
                {backup.type.toUpperCase()}
              </span>
            </div>
            
            <div className="backup-details">
              <h3>{backup.filename}</h3>
              <div className="backup-meta">
                <div className="meta-item">
                  <Clock size={16} />
                  <span>{new Date(backup.created_at).toLocaleString()}</span>
                </div>
                <div className="meta-item">
                  <Database size={16} />
                  <span>{formatFileSize(backup.size)}</span>
                </div>
              </div>
            </div>
            
            <div className="backup-actions">
              <button className="btn-secondary">View Details</button>
              <button className="btn-primary">Use for Recovery</button>
            </div>
          </div>
        ))}
      </div>

      {filteredBackups.length === 0 && (
        <div className="no-backups">
          <AlertCircle size={48} />
          <h3>No backups found</h3>
          <p>No backups match the current filter criteria.</p>
        </div>
      )}
    </div>
  );
};

export default BackupStatus;
