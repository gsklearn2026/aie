import React, { useState, useEffect } from 'react';
import {
  Container,
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  Paper,
  Fab,
  Snackbar,
  Alert,
} from '@mui/material';
import {
  Add,
  School,
  AccessTime,
  TrendingUp,
  Visibility,
  PlayArrow,
  PlayCircle,
} from '@mui/icons-material';
import { topicsApi } from '../services/api';
import { demoService } from '../services/demoData';

function TopicsView() {
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [createDialog, setCreateDialog] = useState(false);
  const [detailDialog, setDetailDialog] = useState(false);
  const [loading, setLoading] = useState(true);
  const [demoLoading, setDemoLoading] = useState(false);
  const [demoMessage, setDemoMessage] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    loadTopics();
  }, []);

  const loadTopics = async () => {
    try {
      setLoading(true);
      const response = await topicsApi.getTopics();
      setTopics(response.topics);
    } catch (error) {
      console.error('Error loading topics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTopic = async (topicData) => {
    try {
      await topicsApi.createTopic(topicData);
      loadTopics(); // Reload topics
      setCreateDialog(false);
    } catch (error) {
      console.error('Error creating topic:', error);
    }
  };

  const handleRunDemo = async () => {
    try {
      setDemoLoading(true);
      const result = await demoService.populateTopics();
      
      setDemoMessage({
        open: true,
        message: result.message,
        severity: result.success ? 'success' : 'warning'
      });
      
      if (result.success) {
        // Reload topics after successful demo
        setTimeout(() => {
          loadTopics();
        }, 1000);
      }
    } catch (error) {
      console.error('Error running demo:', error);
      setDemoMessage({
        open: true,
        message: 'Failed to run demo. Please try again.',
        severity: 'error'
      });
    } finally {
      setDemoLoading(false);
    }
  };

  const handleCloseDemoMessage = () => {
    setDemoMessage({ ...demoMessage, open: false });
  };

  const CreateTopicDialog = () => {
    const [formData, setFormData] = useState({
      name: '',
      description: '',
      difficulty_level: 5.0,
      estimated_duration: 60,
      content_type: 'text',
      learning_objectives: []
    });

    const handleSubmit = () => {
      handleCreateTopic(formData);
    };

    return (
      <Dialog open={createDialog} onClose={() => setCreateDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Topic</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              label="Topic Name"
              fullWidth
              sx={{ mb: 2 }}
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
            />
            
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={3}
              sx={{ mb: 2 }}
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
            />
            
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={6}>
                <TextField
                  label="Difficulty (1-10)"
                  type="number"
                  fullWidth
                  inputProps={{ min: 1, max: 10, step: 0.5 }}
                  value={formData.difficulty_level}
                  onChange={(e) => setFormData(prev => ({ ...prev, difficulty_level: parseFloat(e.target.value) }))}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="Duration (minutes)"
                  type="number"
                  fullWidth
                  value={formData.estimated_duration}
                  onChange={(e) => setFormData(prev => ({ ...prev, estimated_duration: parseInt(e.target.value) }))}
                />
              </Grid>
            </Grid>
            
            <FormControl fullWidth>
              <InputLabel>Content Type</InputLabel>
              <Select
                value={formData.content_type}
                onChange={(e) => setFormData(prev => ({ ...prev, content_type: e.target.value }))}
                label="Content Type"
              >
                <MenuItem value="text">Text</MenuItem>
                <MenuItem value="video">Video</MenuItem>
                <MenuItem value="interactive">Interactive</MenuItem>
                <MenuItem value="quiz">Quiz</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialog(false)}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">Create Topic</Button>
        </DialogActions>
      </Dialog>
    );
  };

  const TopicDetailDialog = () => {
    const [relationships, setRelationships] = useState([]);

    useEffect(() => {
      if (selectedTopic) {
        loadTopicRelationships(selectedTopic.id);
      }
    }, [selectedTopic]);

    const loadTopicRelationships = async (topicId) => {
      try {
        const response = await topicsApi.getTopicRelationships(topicId);
        setRelationships(response.relationships);
      } catch (error) {
        console.error('Error loading relationships:', error);
      }
    };

    return (
      <Dialog 
        open={detailDialog} 
        onClose={() => setDetailDialog(false)} 
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>
          {selectedTopic?.name}
        </DialogTitle>
        <DialogContent>
          {selectedTopic && (
            <Box>
              <Typography variant="body1" paragraph>
                {selectedTopic.description}
              </Typography>
              
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={4}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <TrendingUp sx={{ fontSize: 32, color: 'warning.main', mb: 1 }} />
                    <Typography variant="h6">
                      {selectedTopic.difficulty_level}/10
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Difficulty
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <AccessTime sx={{ fontSize: 32, color: 'info.main', mb: 1 }} />
                    <Typography variant="h6">
                      {selectedTopic.estimated_duration} min
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Duration
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <School sx={{ fontSize: 32, color: 'primary.main', mb: 1 }} />
                    <Typography variant="h6">
                      {selectedTopic.content_type}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Content Type
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>

              {relationships.length > 0 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Topic Relationships
                  </Typography>
                  <List>
                    {relationships.map((rel, index) => (
                      <ListItem key={index} divider>
                        <ListItemText
                          primary={`Topic ${rel.source_topic_id} → Topic ${rel.target_topic_id}`}
                          secondary={
                            <Box display="flex" gap={1} mt={1}>
                              <Chip 
                                label={rel.relationship_type} 
                                size="small" 
                                color="primary"
                              />
                              <Chip 
                                label={`Strength: ${(rel.strength * 100).toFixed(0)}%`} 
                                size="small" 
                                variant="outlined"
                              />
                            </Box>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailDialog(false)}>Close</Button>
          <Button variant="contained" startIcon={<PlayArrow />}>
            Start Learning
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

  const getDifficultyColor = (difficulty) => {
    if (difficulty <= 3) return 'success';
    if (difficulty <= 6) return 'warning';
    return 'error';
  };

  const getContentTypeIcon = (type) => {
    switch (type) {
      case 'video':
        return '🎥';
      case 'interactive':
        return '⚡';
      case 'quiz':
        return '❓';
      default:
        return '📄';
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Learning Topics
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Explore available topics and their relationships
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setCreateDialog(true)}
        >
          Create Topic
        </Button>
        
        {/* Demo Button */}
        <Button
          variant="contained"
          color="secondary"
          size="large"
          startIcon={<PlayCircle />}
          onClick={handleRunDemo}
          disabled={demoLoading}
          sx={{
            background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
            color: 'white',
            px: 3,
            py: 1.5,
            borderRadius: 3,
            boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
            '&:hover': {
              background: 'linear-gradient(45deg, #5a6fd8 30%, #6a4190 90%)',
              transform: 'translateY(-2px)',
              boxShadow: '0 6px 20px rgba(102, 126, 234, 0.6)',
            },
            transition: 'all 0.3s ease'
          }}
        >
          {demoLoading ? 'Populating...' : '🚀 Populate Topics'}
        </Button>
      </Box>

      {/* Demo Message Snackbar */}
      <Snackbar
        open={demoMessage.open}
        autoHideDuration={6000}
        onClose={handleCloseDemoMessage}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleCloseDemoMessage} 
          severity={demoMessage.severity}
          sx={{ width: '100%' }}
        >
          {demoMessage.message}
        </Alert>
      </Snackbar>

      <Grid container spacing={3}>
        {topics.map((topic) => (
          <Grid item xs={12} sm={6} md={4} key={topic.id}>
            <Card 
              sx={{ 
                height: '100%',
                cursor: 'pointer',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4,
                  transition: 'all 0.3s ease'
                }
              }}
              onClick={() => {
                setSelectedTopic(topic);
                setDetailDialog(true);
              }}
            >
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
                    {topic.name}
                  </Typography>
                  <Chip 
                    label={`${topic.difficulty_level}/10`}
                    size="small"
                    color={getDifficultyColor(topic.difficulty_level)}
                  />
                </Box>
                
                <Typography variant="body2" color="textSecondary" paragraph>
                  {topic.description}
                </Typography>
                
                <Box display="flex" gap={1} mb={2}>
                  <Chip 
                    label={`${getContentTypeIcon(topic.content_type)} ${topic.content_type}`}
                    size="small"
                    variant="outlined"
                  />
                  <Chip 
                    label={`${topic.estimated_duration} min`}
                    size="small"
                    variant="outlined"
                  />
                </Box>
                
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Button size="small" startIcon={<Visibility />}>
                    View Details
                  </Button>
                  <Button size="small" startIcon={<PlayArrow />} color="primary">
                    Start
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <CreateTopicDialog />
      <TopicDetailDialog />
    </Container>
  );
}

export default TopicsView;
