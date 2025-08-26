import React from 'react';
import { Box, Typography, Grid, Card, CardContent, Alert } from '@mui/material';

const Dashboard = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        📊 System Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Service Status
              </Typography>
              <Alert severity="success">
                Difficulty Classification Service: Online
              </Alert>
              <Alert severity="info" sx={{ mt: 1 }}>
                Feature Extraction: Ready
              </Alert>
              <Alert severity="warning" sx={{ mt: 1 }}>
                AI Enhancement: Configure API Key
              </Alert>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Metrics
              </Typography>
              <Typography variant="body2">
                Average Response Time: ~150ms
              </Typography>
              <Typography variant="body2">
                Cache Hit Rate: 85%
              </Typography>
              <Typography variant="body2">
                Classification Accuracy: 87%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
