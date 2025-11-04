import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Grid,
  Chip
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { quizAPI, healthAPI } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [recentQuizzes, setRecentQuizzes] = useState([]);
  const [systemHealth, setSystemHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [quizzes, health] = await Promise.all([
          quizAPI.getQuizzes(),
          healthAPI.check()
        ]);
        
        setRecentQuizzes(quizzes.slice(0, 5));
        setSystemHealth(health);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return <LoadingSpinner message="Loading dashboard..." />;
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h3" gutterBottom>
        Welcome back, {user?.username}!
      </Typography>
      
      <Typography variant="h6" color="textSecondary" gutterBottom>
        Ready to test your knowledge with AI-generated quizzes?
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button
                  variant="contained"
                  onClick={() => navigate('/create-quiz')}
                  fullWidth
                >
                  Create New Quiz
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/quizzes')}
                  fullWidth
                >
                  Browse All Quizzes
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Quizzes */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Quizzes
              </Typography>
              {recentQuizzes.length > 0 ? (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {recentQuizzes.map((quiz) => (
                    <Box
                      key={quiz.id}
                      sx={{
                        p: 2,
                        border: '1px solid #e0e0e0',
                        borderRadius: 1,
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                      }}
                    >
                      <Box>
                        <Typography variant="subtitle1">{quiz.title}</Typography>
                        <Typography variant="body2" color="textSecondary">
                          {quiz.description}
                        </Typography>
                        <Box sx={{ mt: 1 }}>
                          <Chip
                            label={quiz.difficulty}
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                          <Chip
                            label={quiz.category}
                            size="small"
                            sx={{ ml: 1 }}
                          />
                        </Box>
                      </Box>
                      <Button
                        variant="outlined"
                        onClick={() => navigate(`/quiz/${quiz.id}`)}
                      >
                        Take Quiz
                      </Button>
                    </Box>
                  ))}
                </Box>
              ) : (
                <Typography variant="body2" color="textSecondary">
                  No quizzes available yet. Create your first quiz to get started!
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* System Status */}
        {systemHealth && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  System Status
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <Chip
                    label={`API: ${systemHealth.services.api}`}
                    color="success"
                    variant="outlined"
                  />
                  <Chip
                    label={`Database: ${systemHealth.services.database}`}
                    color="success"
                    variant="outlined"
                  />
                  <Chip
                    label={`AI Service: ${systemHealth.services.gemini_ai}`}
                    color="success"
                    variant="outlined"
                  />
                  <Typography variant="body2" color="textSecondary" sx={{ ml: 'auto' }}>
                    Last updated: {new Date(systemHealth.timestamp).toLocaleString()}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Container>
  );
};

export default Dashboard;
