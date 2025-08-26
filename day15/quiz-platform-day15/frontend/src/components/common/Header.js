import React from 'react';
import { AppBar, Toolbar, Typography, Tabs, Tab, Box } from '@mui/material';

const Header = ({ activeTab, setActiveTab }) => {
  return (
    <AppBar position="static" sx={{ backgroundColor: '#4285f4' }}>
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Quiz Platform - Day 15
        </Typography>
        <Box>
          <Tabs
            value={activeTab}
            onChange={(e, newValue) => setActiveTab(newValue)}
            textColor="inherit"
            TabIndicatorProps={{ style: { backgroundColor: 'white' } }}
          >
            <Tab label="Question Analyzer" value="analyzer" />
            <Tab label="Dashboard" value="dashboard" />
          </Tabs>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
