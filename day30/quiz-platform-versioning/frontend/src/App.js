import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Tabs, Tab, Alert } from '@mui/material';
import VersionAnalyticsDashboard from './components/VersionAnalytics/VersionAnalyticsDashboard';
import QuizManagerV1 from './components/Dashboard/QuizManagerV1';
import QuizManagerV2 from './components/Dashboard/QuizManagerV2';
import './App.css';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [activeTab, setActiveTab] = useState(0);
  const [apiStatus, setApiStatus] = useState('checking');

  useEffect(() => {
    // Check API health
    fetch('/health')
      .then(response => response.json())
      .then(() => setApiStatus('healthy'))
      .catch(() => setApiStatus('error'));
  }, []);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom color="primary">
          🚀 Quiz Platform - API Versioning Demo
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Day 30: Multi-Version API Management System
        </Typography>
        
        {apiStatus === 'healthy' && (
          <Alert severity="success" sx={{ mt: 2, maxWidth: 400, mx: 'auto' }}>
            Backend API is running on both v1 and v2 endpoints
          </Alert>
        )}
        {apiStatus === 'error' && (
          <Alert severity="error" sx={{ mt: 2, maxWidth: 400, mx: 'auto' }}>
            Backend API connection failed. Please check if server is running.
          </Alert>
        )}
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange} centered>
          <Tab label="📊 Version Analytics" />
          <Tab label="📝 Quiz Manager V1 (Deprecated)" />
          <Tab label="🤖 Quiz Manager V2 (Current)" />
        </Tabs>
      </Box>

      <TabPanel value={activeTab} index={0}>
        <VersionAnalyticsDashboard />
      </TabPanel>
      
      <TabPanel value={activeTab} index={1}>
        <QuizManagerV1 />
      </TabPanel>
      
      <TabPanel value={activeTab} index={2}>
        <QuizManagerV2 />
      </TabPanel>
    </Container>
  );
}

export default App;
