import React, { useState, useEffect } from 'react';
import { 
  Paper, Typography, Box, Chip, CircularProgress 
} from '@mui/material';
import { Speed, TrendingUp, Update } from '@mui/icons-material';
import { fetchRealtimeDashboard } from '../../services/api';

function RealTimeStats() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRealtimeStats();
    const interval = setInterval(loadRealtimeStats, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const loadRealtimeStats = async () => {
    try {
      const response = await fetchRealtimeDashboard();
      setStats(response.data.data.real_time_stats);
      setLoading(false);
    } catch (error) {
      console.error('Error loading real-time stats:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Paper sx={{ p: 2 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
          <CircularProgress />
        </Box>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2 }}>
      <Box display="flex" alignItems="center" justifyContent="between" mb={2}>
        <Typography variant="h6" gutterBottom>
          Real-Time Statistics
        </Typography>
        <Chip 
          icon={<Update />} 
          label="Live" 
          color="success" 
          variant="outlined" 
          size="small"
        />
      </Box>
      
      <Box spacing={2}>
        <Box display="flex" alignItems="center" mb={2}>
          <Speed color="primary" sx={{ mr: 2 }} />
          <Box>
            <Typography variant="h5">{stats?.active_sessions_24h || 0}</Typography>
            <Typography color="textSecondary">Active Sessions (24h)</Typography>
          </Box>
        </Box>
        
        <Box display="flex" alignItems="center" mb={2}>
          <TrendingUp color="success" sx={{ mr: 2 }} />
          <Box>
            <Typography variant="h5">{stats?.platform_avg_score || 0}%</Typography>
            <Typography color="textSecondary">Platform Average Score</Typography>
          </Box>
        </Box>
        
        <Box mt={2}>
          <Typography variant="body2" color="textSecondary">
            Data updates every 10 seconds
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
}

export default RealTimeStats;
