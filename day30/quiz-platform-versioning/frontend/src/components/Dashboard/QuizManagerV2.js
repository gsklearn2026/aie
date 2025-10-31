import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Card, CardContent, Button, TextField, Dialog,
  DialogTitle, DialogContent, DialogActions, Grid, IconButton,
  Chip, Alert, LinearProgress, Accordion, AccordionSummary, AccordionDetails
} from '@mui/material';
import { Add, Delete, Analytics, ExpandMore, AutoAwesome, Speed, Psychology } from '@mui/icons-material';

function QuizManagerV2() {
  const [quizzes, setQuizzes] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [analyticsDialog, setAnalyticsDialog] = useState(null);
  const [quizAnalytics, setQuizAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [newQuiz, setNewQuiz] = useState({
    title: '',
    description: '',
    questions: [{ question: '', options: ['', '', '', ''], correct_answer: 0, points: 1 }]
  });

  useEffect(() => {
    fetchQuizzes();
  }, []);

  const fetchQuizzes = async () => {
    try {
      const response = await fetch('/api/v2/quiz/list', {
        headers: { 'X-API-Version': 'v2' }
      });
      const data = await response.json();
      setQuizzes(data.quizzes || []);
    } catch (error) {
      console.error('Failed to fetch quizzes:', error);
    }
  };

  const createQuiz = async () => {
    if (!newQuiz.title || !newQuiz.description) return;
    
    setLoading(true);
    try {
      const response = await fetch('/api/v2/quiz/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Version': 'v2'
        },
        body: JSON.stringify(newQuiz)
      });
      
      if (response.ok) {
        setOpenDialog(false);
        setNewQuiz({
          title: '',
          description: '',
          questions: [{ question: '', options: ['', '', '', ''], correct_answer: 0, points: 1 }]
        });
        fetchQuizzes();
      }
    } catch (error) {
      console.error('Failed to create quiz:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteQuiz = async (quizId) => {
    try {
      await fetch(`/api/v2/quiz/${quizId}`, {
        method: 'DELETE',
        headers: { 'X-API-Version': 'v2' }
      });
      fetchQuizzes();
    } catch (error) {
      console.error('Failed to delete quiz:', error);
    }
  };

  const fetchQuizAnalytics = async (quizId) => {
    try {
      const response = await fetch(`/api/v2/quiz/${quizId}/analytics`, {
        headers: { 'X-API-Version': 'v2' }
      });
      const data = await response.json();
      setQuizAnalytics(data);
      setAnalyticsDialog(quizId);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  };

  const getDifficultyColor = (score) => {
    if (score <= 3) return 'success';
    if (score <= 7) return 'warning';
    return 'error';
  };

  const getDifficultyLabel = (score) => {
    if (score <= 3) return 'Easy';
    if (score <= 7) return 'Medium';
    return 'Hard';
  };

  const addQuestion = () => {
    setNewQuiz({
      ...newQuiz,
      questions: [...newQuiz.questions, { question: '', options: ['', '', '', ''], correct_answer: 0, points: 1 }]
    });
  };

  return (
    <Box>
      <Alert severity="success" sx={{ mb: 3 }} icon={<AutoAwesome />}>
        <strong>API v2 is current!</strong> Enjoy AI-powered difficulty scoring, adaptive hints, and advanced analytics.
      </Alert>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" color="primary">
          🤖 Quiz Manager V2 (AI-Enhanced)
        </Typography>
        <Button 
          variant="contained" 
          startIcon={<Add />}
          onClick={() => setOpenDialog(true)}
          color="primary"
        >
          Create AI-Enhanced Quiz
        </Button>
      </Box>

      <Grid container spacing={3}>
        {quizzes.map((quiz) => (
          <Grid item xs={12} md={6} lg={4} key={quiz.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Typography variant="h6" gutterBottom sx={{ flex: 1 }}>
                    {quiz.title}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 0.5 }}>
                    <IconButton onClick={() => fetchQuizAnalytics(quiz.id)} color="primary">
                      <Analytics />
                    </IconButton>
                    <IconButton onClick={() => deleteQuiz(quiz.id)} color="error">
                      <Delete />
                    </IconButton>
                  </Box>
                </Box>
                
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {quiz.description}
                </Typography>
                
                <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                  <Chip 
                    label={`${quiz.question_count} questions`} 
                    size="small" 
                    color="primary" 
                  />
                  <Chip 
                    label="V2 API" 
                    size="small" 
                    color="success" 
                  />
                  <Chip
                    icon={<Speed />}
                    label={`${Math.round(quiz.estimated_duration / 60)} min`}
                    size="small"
                    variant="outlined"
                  />
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Psychology fontSize="small" />
                    <Typography variant="body2">AI Difficulty Score</Typography>
                    <Chip 
                      label={getDifficultyLabel(quiz.ai_difficulty_score)}
                      size="small"
                      color={getDifficultyColor(quiz.ai_difficulty_score)}
                    />
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={quiz.ai_difficulty_score * 10} 
                    color={getDifficultyColor(quiz.ai_difficulty_score)}
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                  <Typography variant="caption" color="text.secondary">
                    {quiz.ai_difficulty_score.toFixed(1)}/10
                  </Typography>
                </Box>

                {quiz.ai_tags && quiz.ai_tags.length > 0 && (
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {quiz.ai_tags.slice(0, 3).map((tag, index) => (
                      <Chip 
                        key={index}
                        label={tag} 
                        size="small" 
                        variant="outlined"
                        color="secondary"
                      />
                    ))}
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Create Quiz Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New AI-Enhanced Quiz</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            AI will automatically calculate difficulty scores, generate hints, and add relevant tags!
          </Alert>
          
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
            <TextField
              label="Quiz Title"
              value={newQuiz.title}
              onChange={(e) => setNewQuiz({...newQuiz, title: e.target.value})}
              fullWidth
            />
            <TextField
              label="Description"
              value={newQuiz.description}
              onChange={(e) => setNewQuiz({...newQuiz, description: e.target.value})}
              fullWidth
              multiline
              rows={2}
            />
            
            <Typography variant="h6" sx={{ mt: 2 }}>Questions</Typography>
            {newQuiz.questions.map((question, qIndex) => (
              <Accordion key={qIndex}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography>Question {qIndex + 1}</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <TextField
                      label="Question"
                      value={question.question}
                      onChange={(e) => {
                        const updated = [...newQuiz.questions];
                        updated[qIndex].question = e.target.value;
                        setNewQuiz({...newQuiz, questions: updated});
                      }}
                      fullWidth
                      multiline
                      rows={2}
                    />
                    <Grid container spacing={2}>
                      {question.options.map((option, oIndex) => (
                        <Grid item xs={6} key={oIndex}>
                          <TextField
                            label={`Option ${oIndex + 1}`}
                            value={option}
                            onChange={(e) => {
                              const updated = [...newQuiz.questions];
                              updated[qIndex].options[oIndex] = e.target.value;
                              setNewQuiz({...newQuiz, questions: updated});
                            }}
                            fullWidth
                            size="small"
                          />
                        </Grid>
                      ))}
                    </Grid>
                    <Alert severity="info" icon={<AutoAwesome />}>
                      AI will automatically generate difficulty score and hints for this question
                    </Alert>
                  </Box>
                </AccordionDetails>
              </Accordion>
            ))}
            
            <Button onClick={addQuestion} variant="outlined" startIcon={<Add />}>
              Add Question
            </Button>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={createQuiz} variant="contained" disabled={loading}>
            {loading ? 'Creating with AI...' : 'Create AI Quiz'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Analytics Dialog */}
      <Dialog 
        open={!!analyticsDialog} 
        onClose={() => setAnalyticsDialog(null)} 
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>Quiz Analytics</DialogTitle>
        <DialogContent>
          {quizAnalytics && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 2 }}>
              <Typography variant="h6">
                {quizAnalytics.title}
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>Difficulty Distribution</Typography>
                      {Object.entries(quizAnalytics.difficulty_distribution).map(([level, count]) => (
                        <Box key={level} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography>{level.charAt(0).toUpperCase() + level.slice(1)}</Typography>
                          <Typography>{count}</Typography>
                        </Box>
                      ))}
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>Cognitive Load Distribution</Typography>
                      {Object.entries(quizAnalytics.cognitive_load_distribution).map(([load, count]) => (
                        <Box key={load} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography>{load.charAt(0).toUpperCase() + load.slice(1)}</Typography>
                          <Typography>{count}</Typography>
                        </Box>
                      ))}
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
              
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body1">
                  Average Difficulty: <strong>{quizAnalytics.avg_difficulty.toFixed(1)}/10</strong>
                </Typography>
                <Typography variant="body1">
                  Total Questions: <strong>{quizAnalytics.total_questions}</strong>
                </Typography>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAnalyticsDialog(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default QuizManagerV2;
