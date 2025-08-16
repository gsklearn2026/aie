import React, { useState, useEffect } from 'react';
import { cacheAPI } from '../../services/api';
import './CacheMonitor.css';

const CacheMonitor = () => {
  const [stats, setStats] = useState(null);
  const [keys, setKeys] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadCacheStats = async () => {
    setLoading(true);
    try {
      const [statsResponse, keysResponse] = await Promise.all([
        cacheAPI.getStats(),
        cacheAPI.getCacheKeys()
      ]);
      
      setStats(statsResponse.data);
      setKeys(keysResponse.data.keys);
    } catch (error) {
      console.error('Error loading cache stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const flushCache = async () => {
    if (window.confirm('Are you sure you want to flush all cache?')) {
      try {
        await cacheAPI.flushCache();
        await loadCacheStats();
        alert('Cache flushed successfully!');
      } catch (error) {
        console.error('Error flushing cache:', error);
      }
    }
  };

  useEffect(() => {
    loadCacheStats();
    const interval = setInterval(loadCacheStats, 5000); // Auto-refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading && !stats) {
    return <div className="loading">Loading cache statistics...</div>;
  }

  return (
    <div className="cache-monitor">
      <div className="monitor-header">
        <h2>🔍 Cache Performance Monitor</h2>
        <div className="monitor-actions">
          <button onClick={loadCacheStats}>🔄 Refresh</button>
          <button onClick={flushCache} className="danger">🗑️ Flush Cache</button>
        </div>
      </div>

      {stats && (
        <div className="stats-grid">
          <div className="stat-card hit-rate">
            <h3>Hit Rate</h3>
            <div className="stat-value">{stats.cache_performance.hit_rate}</div>
            <div className="stat-detail">
              Hits: {stats.cache_performance.hit_count} | 
              Misses: {stats.cache_performance.miss_count}
            </div>
          </div>

          <div className="stat-card memory">
            <h3>Memory Usage</h3>
            <div className="stat-value">{stats.cache_performance.used_memory_human}</div>
            <div className="stat-detail">Redis memory consumption</div>
          </div>

          <div className="stat-card connections">
            <h3>Connections</h3>
            <div className="stat-value">{stats.cache_performance.connected_clients}</div>
            <div className="stat-detail">Active Redis connections</div>
          </div>

          <div className="stat-card keyspace">
            <h3>Redis Keyspace</h3>
            <div className="stat-value">
              {stats.cache_performance.keyspace_hits} / {stats.cache_performance.keyspace_misses}
            </div>
            <div className="stat-detail">Hits / Misses (Redis level)</div>
          </div>
        </div>
      )}

      <div className="cache-keys">
        <h3>📋 Cache Keys ({keys.length})</h3>
        <div className="keys-list">
          {keys.slice(0, 20).map((key, index) => (
            <div key={index} className="cache-key">
              <span className="key-name">{key}</span>
              <span className="key-type">
                {key.includes('quiz:') ? '📝' : 
                 key.includes('user_progress:') ? '📊' : 
                 key.includes('leaderboard:') ? '🏆' : 
                 key.includes('ai_explanation:') ? '🤖' : '🔧'}
              </span>
            </div>
          ))}
          {keys.length > 20 && (
            <div className="more-keys">... and {keys.length - 20} more keys</div>
          )}
        </div>
      </div>

      {stats && (
        <div className="recommendations">
          <h3>💡 Performance Recommendations</h3>
          <ul>
            <li>Target hit rate: {stats.recommendations.hit_rate}</li>
            <li>Memory usage: {stats.recommendations.memory_usage}</li>
            <li>Connections: {stats.recommendations.connections}</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default CacheMonitor;
