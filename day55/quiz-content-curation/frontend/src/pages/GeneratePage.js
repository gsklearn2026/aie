import React, { useState } from 'react';
import {
  Paper, Typography, Box, Button, TextField, MenuItem,
  Alert, CircularProgress, Card, CardContent
} from '@mui/material';
import { questionApi } from '../services/api';

function GeneratePage() {
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('medium');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    if (!topic) {
      setError('Please enter a topic');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await questionApi.generate(topic, difficulty);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to generate question');
    }
    setLoading(false);
  };

  const topics = [
    'Mathematics', 'Science', 'History', 'Geography',
    'Literature', 'Computer Science', 'Physics', 'Chemistry'
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Generate Question
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" gap={2} flexDirection="column">
          <TextField
            select
            label="Topic"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            fullWidth
          >
            {topics.map((t) => (
              <MenuItem key={t} value={t}>{t}</MenuItem>
            ))}
          </TextField>

          <TextField
            select
            label="Difficulty"
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            fullWidth
          >
            <MenuItem value="easy">Easy</MenuItem>
            <MenuItem value="medium">Medium</MenuItem>
            <MenuItem value="hard">Hard</MenuItem>
          </TextField>

          <Button
            variant="contained"
            onClick={handleGenerate}
            disabled={loading || !topic}
            size="large"
          >
            {loading ? <CircularProgress size={24} /> : 'Generate & Submit for Curation'}
          </Button>
        </Box>
      </Paper>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {result && (
        <Card>
          <CardContent>
            <Alert severity="success" sx={{ mb: 2 }}>
              Question generated and submitted for curation!
            </Alert>

            <Typography variant="h6" gutterBottom>
              Generated Question:
            </Typography>
            <Typography paragraph>
              {result.question?.text}
            </Typography>

            <Typography variant="subtitle2">
              Quality Score: {(result.quality_score * 100).toFixed(0)}%
            </Typography>
            <Typography variant="subtitle2">
              Status: {result.status}
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}

export default GeneratePage;
