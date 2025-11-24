import React, { useState, useEffect } from 'react';
import {
  Paper, Typography, Grid, Card, CardContent, Box, Chip
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import axios from 'axios';

function HealthMonitor() {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    try {
      const response = await axios.get('/api/health/ready');
      setHealth(response.data);
    } catch (error) {
      setHealth({ status: 'error', checks: {} });
    }
  };

  if (!health) return null;

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>System Health</Typography>

      <Grid container spacing={2}>
        {Object.entries(health.checks || {}).map(([service, status]) => (
          <Grid item xs={12} sm={6} md={4} key={service}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Typography variant="h6" sx={{ textTransform: 'capitalize' }}>
                    {service.replace('_', ' ')}
                  </Typography>
                  {status.toLowerCase().startsWith('healthy') ? (
                    <CheckCircleIcon sx={{ color: '#4caf50', fontSize: 32 }} />
                  ) : (
                    <ErrorIcon sx={{ color: '#f44336', fontSize: 32 }} />
                  )}
                </Box>
                <Chip
                  label={status}
                  color={status.toLowerCase().startsWith('healthy') ? 'success' : 'error'}
                  size="small"
                  sx={{ mt: 1 }}
                />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Paper>
  );
}

export default HealthMonitor;
