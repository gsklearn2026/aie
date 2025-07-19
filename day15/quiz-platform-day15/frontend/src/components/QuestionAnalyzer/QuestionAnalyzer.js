import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Chip,
  Grid,
  LinearProgress,
  Paper,
} from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const QuestionAnalyzer = () => {
  const [questionText, setQuestionText] = useState('');
  const [subject, setSubject] = useState('');
  const [questionType, setQuestionType] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const questionTypes = [
    { value: 'multiple_choice', label: 'Multiple Choice' },
    { value: 'short_answer', label: 'Short Answer' },
    { value: 'essay', label: 'Essay' },
    { value: 'true_false', label: 'True/False' },
    { value: 'fill_blank', label: 'Fill in the Blank' },
  ];

  const subjects = [
    'Mathematics', 'Physics', 'Chemistry', 'Biology', 'History',
    'Geography', 'Literature', 'Computer Science', 'Economics'
  ];

  const handleAnalyze = async () => {
    if (!questionText.trim() || !subject || !questionType) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await axios.post('/api/v1/classify', {
        question_text: questionText,
        subject: subject.toLowerCase(),
        question_type: questionType,
      });

      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Classification failed');
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (level) => {
    const colors = {
      beginner: '#4caf50',
      intermediate: '#ff9800',
      advanced: '#f44336',
      expert: '#9c27b0',
    };
    return colors[level] || '#757575';
  };

  const getFeatureData = () => {
    if (!result) return [];
    
    const features = result.features;
    return [
      { name: 'Readability', value: Math.round(features.readability_score * 10) / 10 },
      { name: 'Syntax', value: Math.round(features.syntactic_complexity * 100) },
      { name: 'Vocabulary', value: Math.round(features.vocabulary_difficulty * 100) },
      { name: 'Concepts', value: Math.round(features.concept_density * 100) },
      { name: 'Cognitive Load', value: Math.round(features.cognitive_load * 100) },
    ];
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ color: '#202124', fontWeight: 500 }}>
        🎯 Question Difficulty Analyzer
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Analyze educational questions and get AI-powered difficulty assessments
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Question Analysis
              </Typography>
              
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Question Text"
                value={questionText}
                onChange={(e) => setQuestionText(e.target.value)}
                placeholder="Enter your question here..."
                sx={{ mb: 2 }}
              />

              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={6}>
                  <FormControl fullWidth>
                    <InputLabel>Subject</InputLabel>
                    <Select
                      value={subject}
                      label="Subject"
                      onChange={(e) => setSubject(e.target.value)}
                    >
                      {subjects.map((subj) => (
                        <MenuItem key={subj} value={subj}>
                          {subj}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={6}>
                  <FormControl fullWidth>
                    <InputLabel>Question Type</InputLabel>
                    <Select
                      value={questionType}
                      label="Question Type"
                      onChange={(e) => setQuestionType(e.target.value)}
                    >
                      {questionTypes.map((type) => (
                        <MenuItem key={type.value} value={type.value}>
                          {type.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>

              <Button
                fullWidth
                variant="contained"
                onClick={handleAnalyze}
                disabled={loading}
                sx={{ mb: 2 }}
              >
                {loading ? 'Analyzing...' : 'Analyze Question'}
              </Button>

              {loading && <LinearProgress />}
              {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          {result && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Analysis Results
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" color="text.secondary">
                    Difficulty Level
                  </Typography>
                  <Chip
                    label={result.difficulty_level.toUpperCase()}
                    sx={{
                      backgroundColor: getDifficultyColor(result.difficulty_level),
                      color: 'white',
                      fontWeight: 'bold',
                      fontSize: '0.9rem',
                    }}
                  />
                </Box>

                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={6}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4" color="primary">
                        {Math.round(result.difficulty_score * 100)}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Difficulty Score
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={6}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4" color="secondary">
                        {Math.round(result.confidence * 100)}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Confidence
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>

                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Processing Time: {result.processing_time_ms.toFixed(1)}ms
                </Typography>

                <Alert severity="info" sx={{ mt: 2 }}>
                  <Typography variant="body2">
                    <strong>AI Reasoning:</strong> {result.reasoning}
                  </Typography>
                </Alert>
              </CardContent>
            </Card>
          )}
        </Grid>

        {result && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Feature Analysis
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={getFeatureData()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#4285f4" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default QuestionAnalyzer;
