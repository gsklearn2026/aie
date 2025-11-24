import React, { useState, useEffect } from 'react';
import {
  Paper, Typography, Grid, Card, CardContent, CircularProgress, Box
} from '@mui/material';
import PeopleIcon from '@mui/icons-material/People';
import QuizIcon from '@mui/icons-material/Quiz';
import AssignmentIcon from '@mui/icons-material/Assignment';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import axios from 'axios';

function AdminDashboard({ token }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await axios.get('/api/admin/stats', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats', error);
      // Set default stats on error
      setStats({
        total_users: 0,
        total_quizzes: 0,
        total_submissions: 0,
        average_score: 0
      });
    }
    setLoading(false);
  };

  if (loading) return <CircularProgress />;
  if (!stats) return <Typography>Failed to load statistics</Typography>;
  
  // Show message if user is not admin
  const isAdmin = !stats.message;

  const metrics = [
    { title: 'Total Users', value: stats.total_users || 0, icon: <PeopleIcon />, color: '#2196f3' },
    { title: 'Total Quizzes', value: stats.total_quizzes || 0, icon: <QuizIcon />, color: '#4caf50' },
    { title: 'Submissions', value: stats.total_submissions || 0, icon: <AssignmentIcon />, color: '#ff9800' },
    { title: 'Avg Score', value: `${stats.average_score || 0}%`, icon: <TrendingUpIcon />, color: '#9c27b0' }
  ];

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>Admin Dashboard</Typography>
      
      {!isAdmin && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Admin access required to view detailed statistics
        </Typography>
      )}

      <Grid container spacing={3}>
        {metrics.map((metric, idx) => (
          <Grid item xs={12} sm={6} md={3} key={idx}>
            <Card sx={{ backgroundColor: metric.color, color: 'white' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography variant="h4">{metric.value}</Typography>
                    <Typography variant="body2">{metric.title}</Typography>
                  </Box>
                  <Box sx={{ fontSize: 48, opacity: 0.7 }}>
                    {metric.icon}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Paper>
  );
}

export default AdminDashboard;
