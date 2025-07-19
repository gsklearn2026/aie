import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Container, Box } from '@mui/material';
import QuestionAnalyzer from './components/QuestionAnalyzer/QuestionAnalyzer';
import Dashboard from './components/Dashboard/Dashboard';
import Header from './components/common/Header';
import './App.css';

// Google Cloud Skills Boost inspired theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#4285f4',
      light: '#70a1ff',
      dark: '#1a73e8',
    },
    secondary: {
      main: '#34a853',
      light: '#5fb85f',
      dark: '#137333',
    },
    background: {
      default: '#f8f9fa',
      paper: '#ffffff',
    },
    text: {
      primary: '#202124',
      secondary: '#5f6368',
    },
  },
  typography: {
    fontFamily: '"Google Sans", "Roboto", sans-serif',
    h4: {
      fontWeight: 500,
      color: '#202124',
    },
    h6: {
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 3px rgba(60,64,67,.3)',
          border: '1px solid #dadce0',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
  },
});

function App() {
  const [activeTab, setActiveTab] = useState('analyzer');

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ minHeight: '100vh', backgroundColor: '#f8f9fa' }}>
        <Header activeTab={activeTab} setActiveTab={setActiveTab} />
        <Container maxWidth="lg" sx={{ py: 4 }}>
          {activeTab === 'analyzer' ? <QuestionAnalyzer /> : <Dashboard />}
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
