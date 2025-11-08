import React, { useState, useEffect, useRef, useCallback } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './MemoryDashboard.css';

function getBackendBaseUrl() {
  const explicit = process.env.REACT_APP_BACKEND_BASE_URL;
  if (explicit) {
    return explicit.replace(/\/$/, '');
  }

  const protocol =
    process.env.REACT_APP_BACKEND_PROTOCOL ||
    (typeof window !== 'undefined' && window.location?.protocol === 'https:' ? 'https' : 'http');
  const host =
    process.env.REACT_APP_BACKEND_HOST ||
    (typeof window !== 'undefined' ? window.location?.hostname : 'localhost') ||
    'localhost';
  const port = process.env.REACT_APP_BACKEND_PORT ?? '8000';

  return `${protocol}://${host}${port ? `:${port}` : ''}`;
}

function getBackendWsUrl(baseHttpUrl) {
  const explicit = process.env.REACT_APP_BACKEND_WS_URL;
  if (explicit) {
    return explicit.replace(/\/$/, '');
  }

  if (!baseHttpUrl) {
    return 'ws://localhost:8000';
  }

  if (baseHttpUrl.startsWith('https://')) {
    return `wss://${baseHttpUrl.slice('https://'.length)}`;
  }

  if (baseHttpUrl.startsWith('http://')) {
    return `ws://${baseHttpUrl.slice('http://'.length)}`;
  }

  return baseHttpUrl;
}

function MemoryDashboard() {
  const [memoryData, setMemoryData] = useState([]);
  const [stats, setStats] = useState(null);
  const [alertActive, setAlertActive] = useState(false);

  const wsRef = useRef(null);
  const reconnectRef = useRef(null);
  const statsIntervalRef = useRef(null);

  const backendBaseUrl = getBackendBaseUrl();
  const backendWsBase = getBackendWsUrl(backendBaseUrl);

  const fetchStats = useCallback(async () => {
    try {
      const response = await fetch(`${backendBaseUrl}/api/memory/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  }, [backendBaseUrl]);

  useEffect(() => {
    let isUnmounted = false;

    const connect = () => {
      const socket = new WebSocket(`${backendWsBase}/ws/memory`);
      wsRef.current = socket;

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          const history = Array.isArray(data.history) ? data.history : [];
          const current = data.current ?? null;

          setMemoryData(history);
          setAlertActive(Boolean(current?.alert));
        } catch (error) {
          console.error('Failed to parse memory websocket payload:', error);
        }
      };

      socket.onerror = () => {
        socket.close();
      };

      socket.onclose = () => {
        if (!isUnmounted) {
          reconnectRef.current = setTimeout(connect, 3000);
        }
      };
    };

    connect();
    statsIntervalRef.current = setInterval(fetchStats, 10000);
    fetchStats();

    return () => {
      isUnmounted = true;

      if (reconnectRef.current) {
        clearTimeout(reconnectRef.current);
        reconnectRef.current = null;
      }

      if (statsIntervalRef.current) {
        clearInterval(statsIntervalRef.current);
        statsIntervalRef.current = null;
      }

      if (wsRef.current) {
        if (wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.close();
        } else if (wsRef.current.readyState === WebSocket.CONNECTING) {
          const socket = wsRef.current;
          socket.onopen = () => {
            socket.close();
          };
        }
      }
      wsRef.current = null;
    };
  }, [backendWsBase, fetchStats]);

  const triggerGC = async () => {
    try {
      await fetch(`${backendBaseUrl}/api/memory/gc`, { method: 'POST' });
      window.alert('Garbage collection triggered');
    } catch (error) {
      window.alert('Failed to trigger GC');
    }
  };

  const clearCache = async () => {
    try {
      await fetch(`${backendBaseUrl}/api/memory/cache/clear`, { method: 'POST' });
      window.alert('Cache cleared');
    } catch (error) {
      window.alert('Failed to clear cache');
    }
  };

  return (
    <div className="memory-dashboard">
      {alertActive && (
        <div className="alert-banner">
          ⚠️ Memory usage high! Consider clearing cache or restarting.
        </div>
      )}

      <div className="dashboard-grid">
        <div className="card">
          <h2>📊 Memory Timeline</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={memoryData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" hide />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="memory_mb" stroke="#667eea" strokeWidth={2} name="Memory (MB)" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h2>💾 Current Memory</h2>
          {stats && (
            <div className="stats-grid">
              <div className="stat-item">
                <span className="stat-label">RSS Memory</span>
                <span className="stat-value">{stats.process.rss_mb.toFixed(2)} MB</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Memory %</span>
                <span className="stat-value">{stats.process.percent.toFixed(1)}%</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Cache Size</span>
                <span className="stat-value">{stats.cache.cache_size}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">GC Objects</span>
                <span className="stat-value">{stats.gc.objects}</span>
              </div>
            </div>
          )}
        </div>

        <div className="card">
          <h2>🔍 Request Statistics</h2>
          {stats && stats.tracker.endpoint_stats && (
            <div className="endpoint-list">
              {Object.entries(stats.tracker.endpoint_stats).map(([endpoint, stat]) => (
                <div key={endpoint} className="endpoint-item">
                  <div className="endpoint-name">{endpoint}</div>
                  <div className="endpoint-stats">
                    <span>{stat.count} requests</span>
                    <span>{(stat.total_memory / stat.count).toFixed(2)} MB avg</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <h2>🛠️ Actions</h2>
          <div className="action-buttons">
            <button onClick={triggerGC} className="action-btn">
              🗑️ Trigger GC
            </button>
            <button onClick={clearCache} className="action-btn danger">
              🧹 Clear Cache
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MemoryDashboard;
