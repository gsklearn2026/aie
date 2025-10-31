import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AnalyticsIcon from '@mui/icons-material/Analytics';

function Navigation() {
  const navigate = useNavigate();

  return (
    <AppBar position="fixed">
      <Toolbar>
        <DashboardIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Quiz Analytics Platform
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button color="inherit" onClick={() => navigate('/')}>
            Dashboard
          </Button>
          <Button color="inherit" onClick={() => navigate('/user/1')}>
            User Analytics
          </Button>
          <Button color="inherit" onClick={() => navigate('/quiz/1')}>
            Quiz Analytics
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Navigation;
