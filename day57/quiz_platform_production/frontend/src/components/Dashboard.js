import React, { useState, useEffect } from 'react';
import {
  Container, Paper, Typography, Grid, Card, CardContent,
  Button, TextField, CircularProgress, Alert, Chip, Box
} from '@mui/material';
import {
  Speed as SpeedIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Storage as StorageIcon
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { quizService, healthService } from '../services/api';

function Dashboard() {
  const [health, setHealth] = useState(null);
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [topic, setTopic] = useState('');
  const [metrics, setMetrics] = useState([]);
  const [retryCountdown, setRetryCountdown] = useState(null);

  useEffect(() => {
    fetchHealth();
    fetchQuizzes();
    const interval = setInterval(fetchHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  // Countdown timer for retry
  useEffect(() => {
    if (retryCountdown !== null && retryCountdown > 0) {
      const timer = setTimeout(() => {
        setRetryCountdown(retryCountdown - 1);
      }, 1000);
      return () => clearTimeout(timer);
    } else if (retryCountdown === 0) {
      setRetryCountdown(null);
      setError(null);
    }
  }, [retryCountdown]);

  const fetchHealth = async () => {
    try {
      const data = await healthService.checkReadiness();
      setHealth(data);
      
      // Update metrics
      setMetrics(prev => [...prev, {
        time: new Date().toLocaleTimeString(),
        status: data.status === 'healthy' ? 100 : 0
      }].slice(-20));
    } catch (err) {
      console.error('Health check failed:', err);
    }
  };

  const fetchQuizzes = async () => {
    try {
      const data = await quizService.listQuizzes({ limit: 10 });
      setQuizzes(data);
    } catch (err) {
      console.error('Failed to fetch quizzes:', err);
    }
  };

  const handleGenerateQuiz = async () => {
    if (!topic.trim()) {
      setError('Please enter a topic');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await quizService.generateQuiz({
        topic: topic,
        num_questions: 5,
        difficulty: 'medium'
      });
      setTopic('');
      setError(null);
      setRetryCountdown(null);
      fetchQuizzes();
    } catch (err) {
      // Handle structured error responses
      let errorMessage = 'Failed to generate quiz';
      let retryAfter = null;
      
      if (err.response?.data) {
        const responseData = err.response.data;
        
        // FastAPI returns errors in the 'detail' field
        const errorData = responseData.detail || responseData;
        
        if (typeof errorData === 'string') {
          errorMessage = errorData;
        } else if (errorData && typeof errorData === 'object') {
          // Extract retry_after for countdown first
          if (errorData.retry_after) {
            retryAfter = parseInt(errorData.retry_after, 10);
          }
          
          // Check for message field first (most user-friendly)
          if (errorData.message) {
            // Remove the static time from message if countdown is active
            if (retryAfter) {
              errorMessage = errorData.message.replace(/Please try again in \d+ seconds?\.?/i, '').trim();
              if (!errorMessage) {
                errorMessage = errorData.error || 'AI service quota exceeded.';
              }
            } else {
              errorMessage = errorData.message;
            }
          } else if (errorData.error) {
            errorMessage = errorData.error;
          } else {
            // Fallback
            errorMessage = 'An error occurred. Please try again later.';
          }
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      // If it's a 429 error and we have retry_after, start countdown
      if (err.response?.status === 429 && retryAfter) {
        setRetryCountdown(retryAfter);
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    if (status === 'healthy') return 'success';
    if (status === 'degraded') return 'warning';
    return 'error';
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h3" gutterBottom>
        Production Dashboard
      </Typography>

      {/* Health Status */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography color="textSecondary" gutterBottom>
                  System Status
                </Typography>
                {health?.status === 'healthy' ? <CheckIcon color="success" /> : <ErrorIcon color="error" />}
              </Box>
              <Typography variant="h5">
                {health?.status || 'Unknown'}
              </Typography>
              <Chip 
                label={health?.status || 'Checking'}
                color={getStatusColor(health?.status)}
                size="small"
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography color="textSecondary" gutterBottom>
                  Database
                </Typography>
                <StorageIcon color="primary" />
              </Box>
              <Typography variant="h5">
                {health?.checks?.database || 'N/A'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography color="textSecondary" gutterBottom>
                  Cache
                </Typography>
                <SpeedIcon color="primary" />
              </Box>
              <Typography variant="h5">
                {health?.checks?.cache || 'N/A'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                CPU Usage
              </Typography>
              <Typography variant="h5">
                {health?.checks?.resources?.cpu_usage || 'N/A'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Metrics Chart */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          System Health Timeline
        </Typography>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={metrics}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="status" stroke="#4caf50" name="Health %" />
          </LineChart>
        </ResponsiveContainer>
      </Paper>

      {/* Quiz Generation */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Generate New Quiz
        </Typography>
        <Box display="flex" gap={2} alignItems="center">
          <TextField
            fullWidth
            label="Topic"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g., Python Programming"
            disabled={loading}
          />
          <Button
            variant="contained"
            onClick={handleGenerateQuiz}
            disabled={loading || retryCountdown !== null}
            sx={{ minWidth: 120 }}
          >
            {loading ? <CircularProgress size={24} /> : retryCountdown !== null ? `Wait ${retryCountdown}s` : 'Generate'}
          </Button>
        </Box>
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            <Typography variant="body1">{error}</Typography>
            {retryCountdown !== null && retryCountdown > 0 && (
              <Typography variant="body2" sx={{ mt: 1, fontWeight: 'bold' }}>
                Please try again in {retryCountdown} second{retryCountdown !== 1 ? 's' : ''}...
              </Typography>
            )}
          </Alert>
        )}
      </Paper>

      {/* Quiz List */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recent Quizzes ({quizzes.length})
        </Typography>
        <Grid container spacing={2}>
          {quizzes.map((quiz) => (
            <Grid item xs={12} md={6} key={quiz.id}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6">{quiz.title}</Typography>
                  <Typography color="textSecondary" variant="body2">
                    {quiz.description}
                  </Typography>
                  <Box mt={1}>
                    <Chip label={quiz.category} size="small" sx={{ mr: 1 }} />
                    <Chip label={quiz.difficulty} size="small" color="primary" sx={{ mr: 1 }} />
                    <Chip label={`${quiz.total_questions} questions`} size="small" />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>
    </Container>
  );
}

export default Dashboard;
