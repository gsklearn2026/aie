import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [notifications, setNotifications] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    unread: 0,
    read: 0
  });
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // Simulate WebSocket connection
    setConnected(true);
    
    // Load initial notifications
    loadNotifications();
    
    // Set up polling for new notifications
    const interval = setInterval(loadNotifications, 5000);
    
    return () => clearInterval(interval);
  }, []);

  const loadNotifications = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/notifications/user/user123');
      setNotifications(response.data.notifications);
      
      // Calculate stats
      const total = response.data.notifications.length;
      const unread = response.data.notifications.filter(n => n.status !== 'read').length;
      const read = total - unread;
      
      setStats({ total, unread, read });
    } catch (error) {
      console.error('Failed to load notifications:', error);
    }
  };

  const createTestNotification = async () => {
    try {
      await axios.post('http://localhost:8000/api/notifications/test-event');
      alert('Test notification created!');
      loadNotifications(); // Reload to show new notification
    } catch (error) {
      alert('Failed to create test notification');
    }
  };

  const markAsRead = (notificationId) => {
    setNotifications(prev => 
      prev.map(n => 
        n.id === notificationId ? { ...n, status: 'read' } : n
      )
    );
    loadNotifications(); // Reload to update stats
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 Notification Service Dashboard</h1>
        <div className="connection-status">
          Status: <span className={connected ? 'connected' : 'disconnected'}>
            {connected ? '🟢 Connected' : '🔴 Disconnected'}
          </span>
        </div>
      </header>

      <main className="App-main">
        {/* Stats Section */}
        <section className="stats-section">
          <h2>📊 Notification Statistics</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Total</h3>
              <p className="stat-number">{stats.total}</p>
            </div>
            <div className="stat-card">
              <h3>Unread</h3>
              <p className="stat-number unread">{stats.unread}</p>
            </div>
            <div className="stat-card">
              <h3>Read</h3>
              <p className="stat-number read">{stats.read}</p>
            </div>
          </div>
        </section>

        {/* Actions Section */}
        <section className="actions-section">
          <h2>⚡ Quick Actions</h2>
          <button onClick={createTestNotification} className="action-button">
            🔔 Create Test Notification
          </button>
          <button onClick={loadNotifications} className="action-button">
            🔄 Refresh Notifications
          </button>
        </section>

        {/* Notifications Section */}
        <section className="notifications-section">
          <h2>📋 Recent Notifications</h2>
          {notifications.length === 0 ? (
            <p className="no-notifications">No notifications yet. Create one using the button above!</p>
          ) : (
            <div className="notifications-list">
              {notifications.map((notification) => (
                <div 
                  key={notification.id} 
                  className={`notification-item ${notification.status === 'read' ? 'read' : 'unread'}`}
                  onClick={() => markAsRead(notification.id)}
                >
                  <div className="notification-header">
                    <h4>{notification.title}</h4>
                    <span className="notification-time">
                      {new Date(notification.created_at).toLocaleString()}
                    </span>
                  </div>
                  <p className="notification-message">{notification.message}</p>
                  <div className="notification-meta">
                    <span className="notification-type">{notification.event_type}</span>
                    <span className={`notification-status ${notification.status}`}>
                      {notification.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
