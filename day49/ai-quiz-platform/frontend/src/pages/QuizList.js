import React, { useState, useEffect } from 'react';
import { Container, Typography, Grid, Card, CardContent, Button, Chip, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { quizAPI } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';

const QuizList = () => {
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchQuizzes = async () => {
      try {
        const data = await quizAPI.getQuizzes();
        setQuizzes(data);
      } catch (error) {
        console.error('Error fetching quizzes:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchQuizzes();
  }, []);

  if (loading) return <LoadingSpinner message="Loading quizzes..." />;

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h3" gutterBottom>Available Quizzes</Typography>
      
      <Grid container spacing={3}>
        {quizzes.map((quiz) => (
          <Grid item xs={12} sm={6} md={4} key={quiz.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>{quiz.title}</Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  {quiz.description}
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Chip label={quiz.difficulty} size="small" color="primary" />
                  <Chip label={quiz.category} size="small" sx={{ ml: 1 }} />
                </Box>
                <Button
                  variant="contained"
                  fullWidth
                  onClick={() => navigate(`/quiz/${quiz.id}`)}
                >
                  Take Quiz
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default QuizList;
