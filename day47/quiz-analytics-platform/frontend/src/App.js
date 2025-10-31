import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Dashboard from './components/dashboard/Dashboard';
import UserAnalytics from './components/analytics/UserAnalytics';
import QuizAnalytics from './components/analytics/QuizAnalytics';
import Navigation from './components/Navigation';
import './App.css';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2196f3',
    },
    secondary: {
      main: '#ff9800',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <div className="App">
          <Navigation />
          <main style={{ padding: '20px', marginTop: '64px' }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/user/:userId" element={<UserAnalytics />} />
              <Route path="/quiz/:quizId" element={<QuizAnalytics />} />
            </Routes>
          </main>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
