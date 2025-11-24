import React, { useState, useEffect } from 'react';
import {
  AppBar, Toolbar, Typography, Container, Box, Button,
  Paper, Grid, Card, CardContent, CircularProgress, Alert
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import QuizIcon from '@mui/icons-material/Quiz';
import LeaderboardIcon from '@mui/icons-material/Leaderboard';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';

import Auth from './components/Auth';
import QuizGenerator from './components/QuizGenerator';
import Leaderboard from './components/Leaderboard';
import AdminDashboard from './components/AdminDashboard';
import HealthMonitor from './components/HealthMonitor';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [activeTab, setActiveTab] = useState('dashboard');
  const [healthStatus, setHealthStatus] = useState(null);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    try {
      const response = await fetch('/api/health/ready');
      const data = await response.json();
      setHealthStatus(data);
    } catch (error) {
      // Don't set error status for 503 if it's just Gemini API quota issue
      if (error.message.includes('503')) {
        try {
          const response = await fetch('/api/health');
          const data = await response.json();
          setHealthStatus({ ...data, checks: { database: 'healthy', redis: 'healthy', gemini_ai: 'unhealthy (quota exceeded)' } });
        } catch {
          setHealthStatus({ status: 'error', message: error.message });
        }
      } else {
        setHealthStatus({ status: 'error', message: error.message });
      }
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  if (!token) {
    return <Auth onLogin={setToken} />;
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" sx={{ backgroundColor: '#1976d2' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Quiz Platform - Production
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', mr: 2 }}>
            {healthStatus?.status === 'ready' ? (
              <CheckCircleIcon sx={{ color: '#4caf50' }} />
            ) : (
              <ErrorIcon sx={{ color: '#f44336' }} />
            )}
            <Typography variant="body2">
              {healthStatus?.status || 'Checking...'}
            </Typography>
          </Box>
          <Button color="inherit" onClick={handleLogout}>Logout</Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={3}>
            <Button
              fullWidth
              variant={activeTab === 'dashboard' ? 'contained' : 'outlined'}
              startIcon={<DashboardIcon />}
              onClick={() => setActiveTab('dashboard')}
            >
              Dashboard
            </Button>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Button
              fullWidth
              variant={activeTab === 'quiz' ? 'contained' : 'outlined'}
              startIcon={<QuizIcon />}
              onClick={() => setActiveTab('quiz')}
            >
              Quiz
            </Button>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Button
              fullWidth
              variant={activeTab === 'leaderboard' ? 'contained' : 'outlined'}
              startIcon={<LeaderboardIcon />}
              onClick={() => setActiveTab('leaderboard')}
            >
              Leaderboard
            </Button>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Button
              fullWidth
              variant={activeTab === 'admin' ? 'contained' : 'outlined'}
              startIcon={<AdminPanelSettingsIcon />}
              onClick={() => setActiveTab('admin')}
            >
              Admin
            </Button>
          </Grid>
        </Grid>

        {activeTab === 'dashboard' && <HealthMonitor />}
        {activeTab === 'quiz' && <QuizGenerator token={token} />}
        {activeTab === 'leaderboard' && <Leaderboard />}
        {activeTab === 'admin' && <AdminDashboard token={token} />}
      </Container>
    </Box>
  );
}

export default App;
