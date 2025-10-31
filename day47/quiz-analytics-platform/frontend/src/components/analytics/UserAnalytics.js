import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Container, Grid, Paper, Typography, Box, CircularProgress,
  Card, CardContent, Chip, List, ListItem, ListItemText
} from '@mui/material';
import {
  TrendingUp, School, Speed, CheckCircle
} from '@mui/icons-material';
import { fetchUserPerformance, fetchLearningProgress } from '../../services/api';

function UserAnalytics() {
  const { userId } = useParams();
  const [performance, setPerformance] = useState(null);
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUserAnalytics();
  }, [userId]);

  const loadUserAnalytics = async () => {
    try {
      setLoading(true);
      const [perfRes, progRes] = await Promise.all([
        fetchUserPerformance(userId),
        fetchLearningProgress(userId)
      ]);
      
      setPerformance(perfRes.data.data);
      setProgress(progRes.data.data);
    } catch (error) {
      console.error('Error loading user analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTrendColor = (trend) => {
    switch (trend) {
      case 'improving': return 'success';
      case 'declining': return 'error';
      default: return 'default';
    }
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'improving': return '📈';
      case 'declining': return '📉';
      default: return '📊';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl">
      <Typography variant="h4" gutterBottom>
        User Analytics - User #{userId}
      </Typography>
      
      <Grid container spacing={3}>
        {/* Performance Overview */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <School color="primary" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{performance?.average_score || 0}%</Typography>
                  <Typography color="textSecondary">Average Score</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <CheckCircle color="success" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{performance?.total_sessions || 0}</Typography>
                  <Typography color="textSecondary">Total Sessions</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <TrendingUp color="info" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{performance?.best_score || 0}%</Typography>
                  <Typography color="textSecondary">Best Score</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Speed color="warning" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{performance?.completion_rate?.toFixed(1) || 0}%</Typography>
                  <Typography color="textSecondary">Completion Rate</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Trend */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Performance Trend
            </Typography>
            <Box display="flex" alignItems="center" mb={2}>
              <Typography variant="h3" sx={{ mr: 2 }}>
                {getTrendIcon(performance?.recent_performance_trend)}
              </Typography>
              <Box>
                <Chip 
                  label={performance?.recent_performance_trend || 'stable'}
                  color={getTrendColor(performance?.recent_performance_trend)}
                  sx={{ mb: 1 }}
                />
                <Typography variant="body2" color="textSecondary">
                  Based on recent quiz sessions
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Learning Progress */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Learning Progress (Last 30 Days)
            </Typography>
            <Box>
              <Typography variant="body1" gutterBottom>
                Sessions Completed: {progress?.total_sessions || 0}
              </Typography>
              <Box display="flex" alignItems="center" sx={{ mb: 2 }}>
                <Typography variant="body1" component="span">
                  Improvement Trend: 
                </Typography>
                <Chip 
                  label={progress?.improvement_trend?.trend || 'stable'}
                  color={getTrendColor(progress?.improvement_trend?.trend)}
                  size="small"
                  sx={{ ml: 1 }}
                />
              </Box>
              {progress?.improvement_trend?.improvement_rate && (
                <Typography variant="body2" color="textSecondary">
                  {progress.improvement_trend.improvement_rate}
                </Typography>
              )}
            </Box>
          </Paper>
        </Grid>

        {/* AI Recommendations */}
        {progress?.ai_recommendations && (
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                🤖 AI-Powered Learning Recommendations
              </Typography>
              <List>
                {progress.ai_recommendations.map((recommendation, index) => (
                  <ListItem key={index} divider={index < progress.ai_recommendations.length - 1}>
                    <ListItemText
                      primary={recommendation}
                      secondary={`Recommendation ${index + 1}`}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Container>
  );
}

export default UserAnalytics;
