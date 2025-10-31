import React, { useState, useEffect } from 'react';
import {
  Grid, Paper, Typography, Box, Alert, Card, CardContent,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  LinearProgress, Chip
} from '@mui/material';
import {
  PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, LineChart, Line
} from 'recharts';

const COLORS = {
  v1: '#ff7043',
  v2: '#42a5f5',
  v3: '#66bb6a'
};

function VersionAnalyticsDashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await fetch('/api/version/analytics');
        const data = await response.json();
        setAnalytics(data);
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>Loading version analytics...</Typography>
        <LinearProgress />
      </Box>
    );
  }

  if (!analytics) {
    return (
      <Alert severity="error">
        Failed to load analytics data. Please ensure the backend is running.
      </Alert>
    );
  }

  // Prepare chart data
  const versionData = Object.entries(analytics.version_distribution).map(([version, count]) => ({
    name: version.toUpperCase(),
    value: count,
    fill: COLORS[version] || '#757575'
  }));

  const dailyData = Object.entries(analytics.daily_stats).map(([date, versions]) => ({
    date,
    ...versions
  }));

  const endpointData = Object.entries(analytics.endpoint_popularity).map(([endpoint, count]) => ({
    endpoint: endpoint.split('/').pop() || endpoint,
    requests: count
  }));

  const deprecationImpact = analytics.deprecation_impact;

  return (
    <Box>
      <Typography variant="h4" gutterBottom color="primary">
        📊 API Version Analytics Dashboard
      </Typography>

      {/* Deprecation Alert */}
      {deprecationImpact.impact_percentage > 0 && (
        <Alert 
          severity={deprecationImpact.impact_percentage > 15 ? 'warning' : 'info'} 
          sx={{ mb: 3 }}
        >
          <strong>Deprecation Impact Analysis:</strong> V1 API accounts for{' '}
          {deprecationImpact.impact_percentage}% of traffic ({deprecationImpact.affected_requests} requests).
          <br />
          <em>Recommendation: {deprecationImpact.recommendation}</em>
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Version Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Version Usage Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={versionData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value, percent }) => `${name}: ${value} (${(percent).toFixed(1)}%)`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {versionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Daily Usage Trends */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Daily Usage Trends
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={dailyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="v1" stroke="#ff7043" name="V1" />
                  <Line type="monotone" dataKey="v2" stroke="#42a5f5" name="V2" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Endpoint Popularity */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Most Popular Endpoints
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={endpointData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="endpoint" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="requests" fill="#66bb6a" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Version Summary */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Version Summary
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {Object.entries(analytics.version_distribution).map(([version, count]) => (
                  <Box key={version} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip 
                        label={version.toUpperCase()} 
                        size="small"
                        sx={{ 
                          backgroundColor: COLORS[version] || '#757575',
                          color: 'white'
                        }}
                      />
                      {version === 'v1' && <Chip label="DEPRECATED" size="small" color="warning" />}
                      {version === 'v2' && <Chip label="CURRENT" size="small" color="success" />}
                    </Box>
                    <Typography variant="h6">{count}</Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Client Type Breakdown */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Client Type Distribution by Version
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Version</TableCell>
                      <TableCell align="right">Web Browser</TableCell>
                      <TableCell align="right">Mobile</TableCell>
                      <TableCell align="right">API Client</TableCell>
                      <TableCell align="right">Unknown</TableCell>
                      <TableCell align="right">Total</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(analytics.client_breakdown).map(([version, clients]) => {
                      const total = Object.values(clients).reduce((sum, count) => sum + count, 0);
                      return (
                        <TableRow key={version}>
                          <TableCell>
                            <Chip 
                              label={version.toUpperCase()}
                              size="small"
                              sx={{ 
                                backgroundColor: COLORS[version] || '#757575',
                                color: 'white'
                              }}
                            />
                          </TableCell>
                          <TableCell align="right">{clients.web_browser || 0}</TableCell>
                          <TableCell align="right">{clients.mobile || 0}</TableCell>
                          <TableCell align="right">{clients.api_client || 0}</TableCell>
                          <TableCell align="right">{clients.unknown || 0}</TableCell>
                          <TableCell align="right"><strong>{total}</strong></TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default VersionAnalyticsDashboard;
