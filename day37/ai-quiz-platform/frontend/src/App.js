import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  Box,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  CircularProgress,
  Alert,
  Paper,
  Chip
} from '@mui/material';
import { QuizOutlined, CheckCircle, Cancel } from '@mui/icons-material';
import axios from 'axios';
import './App.css';

// API_BASE is no longer needed as we use relative paths

function App() {
  const [quiz, setQuiz] = useState(null);
  const [quizId, setQuizId] = useState(null);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [health, setHealth] = useState(null);

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const response = await axios.get('/health');
      setHealth(response.data);
    } catch (err) {
      setError('Backend service unavailable');
    }
  };

  const generateQuiz = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/quiz/generate?topic=JavaScript&difficulty=medium&num_questions=5');
      setQuiz(response.data.quiz);
      setQuizId(response.data.quiz_id);
      setAnswers({});
      setResult(null);
    } catch (err) {
      setError('Failed to generate quiz. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionIndex, answerIndex) => {
    setAnswers({
      ...answers,
      [questionIndex]: answerIndex
    });
  };

  const submitQuiz = async () => {
    if (Object.keys(answers).length !== quiz.questions.length) {
      setError('Please answer all questions');
      return;
    }

    setLoading(true);
    try {
      const answerArray = quiz.questions.map((_, index) => answers[index]);
      const response = await axios.post(`/api/quiz/${quizId}/submit`, answerArray);
      setResult(response.data.result);
    } catch (err) {
      setError('Failed to submit quiz. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const resetQuiz = () => {
    setQuiz(null);
    setQuizId(null);
    setAnswers({});
    setResult(null);
    setError(null);
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box textAlign="center" mb={4}>
        <QuizOutlined sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
        <Typography variant="h3" component="h1" gutterBottom>
          AI Quiz Platform
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Docker Containerized Learning System
        </Typography>
        
        {health && (
          <Box mt={2}>
            <Chip 
              label={`Status: ${health.status}`} 
              color={health.status === 'healthy' ? 'success' : 'error'}
              variant="outlined"
            />
          </Box>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {!quiz && !result && (
        <Box textAlign="center">
          <Button
            variant="contained"
            size="large"
            onClick={generateQuiz}
            disabled={loading}
            sx={{ minWidth: 200 }}
          >
            {loading ? <CircularProgress size={24} /> : 'Generate New Quiz'}
          </Button>
        </Box>
      )}

      {quiz && !result && (
        <Card>
          <CardContent>
            <Typography variant="h4" gutterBottom>
              {quiz.title}
            </Typography>
            
            {quiz.questions.map((question, questionIndex) => (
              <Paper key={questionIndex} sx={{ p: 3, mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  {questionIndex + 1}. {question.question}
                </Typography>
                
                <FormControl component="fieldset">
                  <RadioGroup
                    value={answers[questionIndex] ?? ''}
                    onChange={(e) => handleAnswerChange(questionIndex, parseInt(e.target.value))}
                  >
                    {question.options.map((option, optionIndex) => (
                      <FormControlLabel
                        key={optionIndex}
                        value={optionIndex}
                        control={<Radio />}
                        label={option}
                      />
                    ))}
                  </RadioGroup>
                </FormControl>
              </Paper>
            ))}
            
            <Box textAlign="center" mt={3}>
              <Button
                variant="contained"
                color="primary"
                onClick={submitQuiz}
                disabled={loading || Object.keys(answers).length !== quiz.questions.length}
                sx={{ minWidth: 150, mr: 2 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Submit Quiz'}
              </Button>
              <Button variant="outlined" onClick={resetQuiz}>
                Cancel
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {result && (
        <Card>
          <CardContent>
            <Box textAlign="center" mb={3}>
              <Typography variant="h4" gutterBottom>
                Quiz Results
              </Typography>
              <Typography variant="h5" color="primary">
                Score: {result.score}/{result.total} ({result.percentage}%)
              </Typography>
            </Box>
            
            {result.results.map((item, index) => (
              <Paper key={index} sx={{ p: 2, mb: 2 }}>
                <Box display="flex" alignItems="center" mb={1}>
                  {item.is_correct ? (
                    <CheckCircle color="success" sx={{ mr: 1 }} />
                  ) : (
                    <Cancel color="error" sx={{ mr: 1 }} />
                  )}
                  <Typography variant="h6">
                    Question {index + 1}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {item.explanation}
                </Typography>
              </Paper>
            ))}
            
            <Box textAlign="center" mt={3}>
              <Button variant="contained" onClick={resetQuiz}>
                Take Another Quiz
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}
    </Container>
  );
}

export default App;
