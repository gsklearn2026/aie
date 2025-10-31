import React, { useState, useEffect } from 'react';
import { 
  Container, Grid, Paper, Typography, Box, CircularProgress,
  Card, CardContent, CardHeader 
} from '@mui/material';
import {
  People, Quiz, TrendingUp, Assessment
} from '@mui/icons-material';
import PerformanceTrendChart from '../charts/PerformanceTrendChart';
import ScoreDistributionChart from '../charts/ScoreDistributionChart';
import TopPerformersTable from './TopPerformersTable';
import RealTimeStats from './RealTimeStats';
import { fetchDashboardOverview, fetchPerformanceTrends, fetchScoreDistribution } from '../../services/api';

function Dashboard() {
  const [overview, setOverview] = useState(null);
  const [trendData, setTrendData] = useState([]);
  const [distributionData, setDistributionData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [overviewRes, trendsRes, distributionRes] = await Promise.all([
        fetchDashboardOverview(),
        fetchPerformanceTrends(),
        fetchScoreDistribution()
      ]);
      
      setOverview(overviewRes.data.data);
      setTrendData(trendsRes.data.data);
      setDistributionData(distributionRes.data.data);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
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
        Analytics Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Overview Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <People color="primary" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{overview?.total_users || 0}</Typography>
                  <Typography color="textSecondary">Total Users</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Quiz color="secondary" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{overview?.total_quizzes || 0}</Typography>
                  <Typography color="textSecondary">Total Quizzes</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Assessment color="success" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{overview?.total_sessions || 0}</Typography>
                  <Typography color="textSecondary">Total Sessions</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <TrendingUp color="info" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{overview?.completion_rate?.toFixed(1) || 0}%</Typography>
                  <Typography color="textSecondary">Completion Rate</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Trend Chart */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Performance Trends (Last 30 Days)
            </Typography>
            <PerformanceTrendChart data={trendData} />
          </Paper>
        </Grid>

        {/* Score Distribution */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Score Distribution
            </Typography>
            <ScoreDistributionChart data={distributionData} />
          </Paper>
        </Grid>

        {/* Real-time Stats */}
        <Grid item xs={12} md={6}>
          <RealTimeStats />
        </Grid>

        {/* Top Performers */}
        <Grid item xs={12} md={6}>
          <TopPerformersTable />
        </Grid>
      </Grid>
    </Container>
  );
}

export default Dashboard;
