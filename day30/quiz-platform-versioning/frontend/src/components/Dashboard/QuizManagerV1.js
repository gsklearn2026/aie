import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Card, CardContent, Button, TextField, Dialog,
  DialogTitle, DialogContent, DialogActions, List, ListItem,
  ListItemText, ListItemSecondary, Chip, Alert, Grid, IconButton
} from '@mui/material';
import { Add, Delete, Warning } from '@mui/icons-material';

function QuizManagerV1() {
  const [quizzes, setQuizzes] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
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
      const response = await fetch('/api/v1/quiz/list', {
        headers: { 'X-API-Version': 'v1' }
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
      const response = await fetch('/api/v1/quiz/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Version': 'v1'
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
      await fetch(`/api/v1/quiz/${quizId}`, {
        method: 'DELETE',
        headers: { 'X-API-Version': 'v1' }
      });
      fetchQuizzes();
    } catch (error) {
      console.error('Failed to delete quiz:', error);
    }
  };

  const addQuestion = () => {
    setNewQuiz({
      ...newQuiz,
      questions: [...newQuiz.questions, { question: '', options: ['', '', '', ''], correct_answer: 0, points: 1 }]
    });
  };

  return (
    <Box>
      <Alert severity="warning" sx={{ mb: 3 }} icon={<Warning />}>
        <strong>API v1 is deprecated!</strong> This version lacks AI features and will be sunset soon.
        Consider migrating to v2 for enhanced functionality.
      </Alert>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" color="primary">
          📝 Quiz Manager V1 (Legacy)
        </Typography>
        <Button 
          variant="contained" 
          startIcon={<Add />}
          onClick={() => setOpenDialog(true)}
          color="warning"
        >
          Create V1 Quiz
        </Button>
      </Box>

      <Grid container spacing={3}>
        {quizzes.map((quiz) => (
          <Grid item xs={12} md={6} key={quiz.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h6" gutterBottom>
                      {quiz.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {quiz.description}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                      <Chip 
                        label={`${quiz.question_count} questions`} 
                        size="small" 
                        color="primary" 
                      />
                      <Chip 
                        label="V1 API" 
                        size="small" 
                        color="warning" 
                      />
                    </Box>
                  </Box>
                  <IconButton onClick={() => deleteQuiz(quiz.id)} color="error">
                    <Delete />
                  </IconButton>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Create Quiz Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New V1 Quiz</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
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
              <Card key={qIndex} sx={{ p: 2, bgcolor: 'grey.50' }}>
                <TextField
                  label={`Question ${qIndex + 1}`}
                  value={question.question}
                  onChange={(e) => {
                    const updated = [...newQuiz.questions];
                    updated[qIndex].question = e.target.value;
                    setNewQuiz({...newQuiz, questions: updated});
                  }}
                  fullWidth
                  sx={{ mb: 2 }}
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
              </Card>
            ))}
            
            <Button onClick={addQuestion} variant="outlined">
              Add Question
            </Button>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={createQuiz} variant="contained" disabled={loading}>
            {loading ? 'Creating...' : 'Create Quiz'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default QuizManagerV1;
