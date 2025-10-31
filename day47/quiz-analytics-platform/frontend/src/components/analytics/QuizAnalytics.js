import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Container, Grid, Paper, Typography, Box, CircularProgress,
  Card, CardContent, List, ListItem, ListItemText, Chip
} from '@mui/material';
import {
  Quiz, People, Speed, TrendingUp
} from '@mui/icons-material';
import { fetchQuizAnalytics } from '../../services/api';

function QuizAnalytics() {
  const { quizId } = useParams();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadQuizAnalytics();
  }, [quizId]);

  const loadQuizAnalytics = async () => {
    try {
      setLoading(true);
      const response = await fetchQuizAnalytics(quizId);
      setAnalytics(response.data.data);
    } catch (error) {
      console.error('Error loading quiz analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy': return 'success';
      case 'medium': return 'warning';
      case 'hard': return 'error';
      case 'very_hard': return 'error';
      default: return 'default';
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
        Quiz Analytics - Quiz #{quizId}
      </Typography>
      
      <Grid container spacing={3}>
        {/* Quiz Overview */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Quiz color="primary" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{analytics?.total_attempts || 0}</Typography>
                  <Typography color="textSecondary">Total Attempts</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <TrendingUp color="success" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{analytics?.average_score?.toFixed(1) || 0}%</Typography>
                  <Typography color="textSecondary">Average Score</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Speed color="info" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{Math.round(analytics?.average_completion_time / 60) || 0}</Typography>
                  <Typography color="textSecondary">Avg Time (min)</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <People color="warning" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{analytics?.completion_rate?.toFixed(1) || 0}%</Typography>
                  <Typography color="textSecondary">Completion Rate</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Quiz Statistics */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quiz Statistics
            </Typography>
            <Box>
              <Box display="flex" justifyContent="space-between" mb={2}>
                <Typography>Difficulty Rating:</Typography>
                <Chip 
                  label={analytics?.difficulty_rating || 'unknown'}
                  color={getDifficultyColor(analytics?.difficulty_rating)}
                  size="small"
                />
              </Box>
              <Box display="flex" justifyContent="space-between" mb={2}>
                <Typography>Median Score:</Typography>
                <Typography fontWeight="bold">
                  {analytics?.median_score?.toFixed(1) || 0}%
                </Typography>
              </Box>
              <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                Score Distribution:
              </Typography>
              {analytics?.score_distribution && Object.entries(analytics.score_distribution).map(([range, count]) => (
                <Box key={range} display="flex" justifyContent="space-between" mb={1}>
                  <Typography>{range}%:</Typography>
                  <Typography fontWeight="bold">{count} students</Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>

        {/* AI Insights */}
        {analytics?.ai_insights && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                🤖 AI-Generated Insights
              </Typography>
              <List>
                {analytics.ai_insights.map((insight, index) => (
                  <ListItem key={index} divider={index < analytics.ai_insights.length - 1}>
                    <ListItemText
                      primary={insight}
                      secondary={`Insight ${index + 1}`}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Container>
  );
}

export default QuizAnalytics;
