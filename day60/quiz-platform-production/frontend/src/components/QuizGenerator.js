import React, { useState } from 'react';
import {
  Paper, TextField, Button, Typography, Box, Radio, RadioGroup,
  FormControlLabel, FormControl, FormLabel, CircularProgress, Alert
} from '@mui/material';
import axios from 'axios';

function QuizGenerator({ token }) {
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('medium');
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const generateQuiz = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/quiz/generate',
        { topic, difficulty, num_questions: 5 },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setQuiz(response.data);
      setAnswers(new Array(response.data.questions.length).fill(null));
      setResult(null);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to generate quiz';
      if (err.response?.status === 503) {
        // Extract a cleaner message for quota errors
        let message = 'Quiz generation is temporarily unavailable due to API quota limits.';
        if (errorMessage.includes('quota') || errorMessage.includes('Quota')) {
          message = 'Quiz generation is temporarily unavailable due to API quota limits. Please try again later.';
        } else {
          message = `Quiz generation is temporarily unavailable: ${errorMessage}`;
        }
        setError(message);
      } else {
        setError(`Failed to generate quiz: ${errorMessage}`);
      }
    }
    setLoading(false);
  };

  const submitQuiz = async () => {
    try {
      const response = await axios.post('/api/quiz/submit',
        { quiz_id: quiz.quiz_id, answers },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setResult(response.data);
    } catch (error) {
      alert('Failed to submit quiz');
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>Generate Quiz</Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {!quiz && (
        <Box>
          <TextField
            fullWidth
            label="Topic"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            margin="normal"
          />

          <FormControl component="fieldset" margin="normal">
            <FormLabel>Difficulty</FormLabel>
            <RadioGroup
              row
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
            >
              <FormControlLabel value="easy" control={<Radio />} label="Easy" />
              <FormControlLabel value="medium" control={<Radio />} label="Medium" />
              <FormControlLabel value="hard" control={<Radio />} label="Hard" />
            </RadioGroup>
          </FormControl>

          <Button
            fullWidth
            variant="contained"
            onClick={generateQuiz}
            disabled={!topic || loading}
            sx={{ mt: 2 }}
          >
            {loading ? <CircularProgress size={24} /> : 'Generate Quiz'}
          </Button>
        </Box>
      )}

      {quiz && !result && (
        <Box>
          {quiz.questions.map((q, idx) => (
            <Box key={idx} sx={{ mb: 3 }}>
              <Typography variant="h6">Q{idx + 1}: {q.question}</Typography>
              <RadioGroup
                value={answers[idx] ?? ''}
                onChange={(e) => {
                  const newAnswers = [...answers];
                  newAnswers[idx] = parseInt(e.target.value);
                  setAnswers(newAnswers);
                }}
              >
                {q.options.map((option, optIdx) => (
                  <FormControlLabel
                    key={optIdx}
                    value={optIdx}
                    control={<Radio />}
                    label={option}
                  />
                ))}
              </RadioGroup>
            </Box>
          ))}

          <Button
            fullWidth
            variant="contained"
            onClick={submitQuiz}
            disabled={answers.includes(null)}
          >
            Submit Quiz
          </Button>
        </Box>
      )}

      {result && (
        <Alert severity="success">
          <Typography variant="h6">
            Score: {result.score.toFixed(1)}% ({result.correct}/{result.total})
          </Typography>
          <Button onClick={() => { setQuiz(null); setResult(null); }}>
            Take Another Quiz
          </Button>
        </Alert>
      )}
    </Paper>
  );
}

export default QuizGenerator;
