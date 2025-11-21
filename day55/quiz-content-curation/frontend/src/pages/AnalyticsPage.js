import React, { useState, useEffect } from 'react';
import {
  Paper, Typography, Box, Grid, Card, CardContent,
  CircularProgress, Alert
} from '@mui/material';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import { analyticsApi } from '../services/api';

const COLORS = ['#2e7d32', '#f57c00', '#1976d2', '#d32f2f', '#7b1fa2'];

function AnalyticsPage() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const data = await analyticsApi.getCurationAnalytics(7);
      setAnalytics(data);
      setError(null);
    } catch (err) {
      setError('Failed to load analytics');
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  const statusData = Object.entries(analytics.status_distribution).map(([key, value]) => ({
    name: key.replace(/_/g, ' '),
    value
  }));

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Curation Analytics
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Items
              </Typography>
              <Typography variant="h4">
                {analytics.total_items || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Reviewed (7d)
              </Typography>
              <Typography variant="h4">
                {analytics.total_reviewed || 0}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                All-time: {analytics.total_reviewed_alltime || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Approval Rate (7d)
              </Typography>
              <Typography variant="h4">
                {(analytics.approval_rate * 100).toFixed(1)}%
              </Typography>
              <Typography variant="caption" color="textSecondary">
                All-time: {(analytics.approval_rate_alltime * 100).toFixed(1)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Avg Review Time (7d)
              </Typography>
              <Typography variant="h4">
                {analytics.avg_review_time_minutes.toFixed(0)}m
              </Typography>
              <Typography variant="caption" color="textSecondary">
                All-time: {analytics.avg_review_time_alltime_minutes.toFixed(0)}m
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Pending Items
              </Typography>
              <Typography variant="h4">
                {analytics.status_distribution?.pending || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Daily Review Activity
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics.daily_stats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="reviewed" fill="#2e7d32" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Status Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {analytics.model_performance && Object.keys(analytics.model_performance).length > 0 && (
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Model Performance
              </Typography>
              <Grid container spacing={2}>
                {Object.entries(analytics.model_performance).map(([model, stats]) => (
                  <Grid item xs={12} sm={6} md={4} key={model}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="subtitle1">{model}</Typography>
                        <Typography variant="body2">
                          Generated: {stats.total_generated}
                        </Typography>
                        <Typography variant="body2">
                          Avg Score: {(stats.avg_quality_score * 100).toFixed(1)}%
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Box>
  );
}

export default AnalyticsPage;
