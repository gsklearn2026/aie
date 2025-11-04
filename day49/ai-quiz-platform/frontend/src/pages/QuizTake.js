import React, { useState, useEffect } from 'react';
import {
  Container, Typography, Card, CardContent, Button, Radio,
  RadioGroup, FormControlLabel, FormControl, Box, Alert, Paper
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { quizAPI } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';

const QuizTake = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [quiz, setQuiz] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const fetchQuiz = async () => {
      try {
        const quizData = await quizAPI.getQuiz(id);
        setQuiz(quizData);
        const parsedQuestions = JSON.parse(quizData.questions);
        setQuestions(parsedQuestions.questions || []);
      } catch (error) {
        console.error('Error fetching quiz:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchQuiz();
  }, [id]);

  const handleAnswerChange = (questionIndex, answerIndex) => {
    setAnswers({ ...answers, [questionIndex]: answerIndex });
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const result = await quizAPI.submitQuizAttempt(id, answers);
      setResult(result);
    } catch (error) {
      console.error('Error submitting quiz:', error);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading quiz..." />;
  if (!quiz) return <Alert severity="error">Quiz not found</Alert>;

  if (result) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h3" gutterBottom color="primary">
            Quiz Complete!
          </Typography>
          <Typography variant="h4" gutterBottom>
            Your Score: {result.score}%
          </Typography>
          <Typography variant="h6" gutterBottom>
            You got {result.correct_answers} out of {result.total_questions} questions correct
          </Typography>
          <Box sx={{ mt: 4 }}>
            <Button
              variant="contained"
              onClick={() => navigate('/quizzes')}
              sx={{ mr: 2 }}
            >
              Take Another Quiz
            </Button>
            <Button variant="outlined" onClick={() => navigate('/dashboard')}>
              Back to Dashboard
            </Button>
          </Box>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h3" gutterBottom>{quiz.title}</Typography>
      <Typography variant="body1" paragraph>{quiz.description}</Typography>
      
      {questions.map((question, index) => (
        <Card key={index} sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Question {index + 1}: {question.question}
            </Typography>
            <FormControl component="fieldset">
              <RadioGroup
                value={answers[index] ?? ''}
                onChange={(e) => handleAnswerChange(index, parseInt(e.target.value))}
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
          </CardContent>
        </Card>
      ))}
      
      <Box sx={{ textAlign: 'center', mt: 4 }}>
        <Button
          variant="contained"
          size="large"
          onClick={handleSubmit}
          disabled={submitting || Object.keys(answers).length !== questions.length}
        >
          {submitting ? 'Submitting...' : 'Submit Quiz'}
        </Button>
      </Box>
    </Container>
  );
};

export default QuizTake;
