import React, { useState, useEffect } from 'react';
import {
  Container,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  TextField,
  Chip,
  Grid,
  FormControlLabel,
  Switch,
  Slider,
  Alert,
  CircularProgress,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
} from '@mui/material';
import {
  Add,
  Remove,
  Science,
  Psychology,
  Speed,
  Timeline,
  CheckCircle,
} from '@mui/icons-material';
import { learningPathApi, topicsApi } from '../services/api';

function PathGenerator() {
  const [topics, setTopics] = useState([]);
  const [selectedTopics, setSelectedTopics] = useState([]);
  const [generationSettings, setGenerationSettings] = useState({
    maxDifficultyJump: 2.0,
    preferredDuration: null,
    useCollaborative: false,
  });
  const [generatedPath, setGeneratedPath] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadTopics();
  }, []);

  const loadTopics = async () => {
    try {
      const response = await topicsApi.getTopics();
      setTopics(response.topics);
    } catch (error) {
      console.error('Error loading topics:', error);
      setError('Failed to load topics');
    }
  };

  const handleTopicToggle = (topicId) => {
    setSelectedTopics(prev => 
      prev.includes(topicId)
        ? prev.filter(id => id !== topicId)
        : [...prev, topicId]
    );
  };

  const generatePath = async () => {
    if (selectedTopics.length === 0) {
      setError('Please select at least one topic');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      const request = {
        user_id: 1, // Demo user
        target_topics: selectedTopics,
        max_difficulty_jump: generationSettings.maxDifficultyJump,
        preferred_duration: generationSettings.preferredDuration,
        use_collaborative: generationSettings.useCollaborative,
      };

      const result = await learningPathApi.generatePath(request);
      setGeneratedPath(result);
      
    } catch (error) {
      console.error('Error generating path:', error);
      setError('Failed to generate learning path');
    } finally {
      setLoading(false);
    }
  };

  const PathVisualization = ({ path }) => {
    const topicMap = topics.reduce((map, topic) => {
      map[topic.id] = topic;
      return map;
    }, {});

    return (
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Generated Learning Path
          </Typography>
          
          {/* Path Overview */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={6} sm={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" color="primary">
                  {path.total_topics}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Topics
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" color="primary">
                  {Math.round(path.estimated_duration / 60)}h
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Duration
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" color="primary">
                  {(path.completion_probability * 100).toFixed(0)}%
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Success Rate
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h4" color="primary">
                  {path.difficulty_progression[path.difficulty_progression.length - 1].toFixed(1)}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Max Difficulty
                </Typography>
              </Paper>
            </Grid>
          </Grid>

          {/* Topic Sequence */}
          <Typography variant="subtitle1" gutterBottom>
            Learning Sequence
          </Typography>
          <List>
            {path.topic_sequence.map((topicId, index) => {
              const topic = topicMap[topicId];
              const difficulty = path.difficulty_progression[index];
              
              return (
                <ListItem 
                  key={topicId}
                  sx={{ 
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 2,
                    mb: 1,
                    bgcolor: 'background.paper'
                  }}
                >
                  <ListItemIcon>
                    <Chip 
                      label={index + 1} 
                      size="small" 
                      color="primary"
                      sx={{ minWidth: 32 }}
                    />
                  </ListItemIcon>
                  <ListItemText
                    primary={topic?.name || `Topic ${topicId}`}
                    secondary={
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          {topic?.description}
                        </Typography>
                        <Box display="flex" gap={1} mt={1}>
                          <Chip 
                            label={`${difficulty.toFixed(1)}/10`} 
                            size="small" 
                            variant="outlined"
                          />
                          <Chip 
                            label={`${topic?.estimated_duration || 60} min`} 
                            size="small" 
                            variant="outlined"
                          />
                          <Chip 
                            label={topic?.content_type || 'mixed'} 
                            size="small" 
                            variant="outlined"
                          />
                        </Box>
                      </Box>
                    }
                  />
                </ListItem>
              );
            })}
          </List>

          {/* Path Analysis */}
          {path.path_analysis && (
            <Box mt={3}>
              <Typography variant="subtitle1" gutterBottom>
                Path Analysis
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={4}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="body2" color="textSecondary">
                      Prerequisite Coverage
                    </Typography>
                    <Typography variant="h6">
                      {(path.path_analysis.prerequisite_coverage * 100).toFixed(0)}%
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="body2" color="textSecondary">
                      Difficulty Balance
                    </Typography>
                    <Typography variant="h6">
                      {path.path_analysis.difficulty_balance.toFixed(2)}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="body2" color="textSecondary">
                      Knowledge Gaps
                    </Typography>
                    <Typography variant="h6">
                      {path.path_analysis.knowledge_gaps.length}
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            </Box>
          )}

          {/* Collaborative Insights */}
          {path.collaborative_insights && (
            <Box mt={3}>
              <Typography variant="subtitle1" gutterBottom>
                Collaborative Insights
              </Typography>
              <Alert severity="info" sx={{ mb: 2 }}>
                This path is enhanced with insights from {path.collaborative_insights.similar_users_count} similar learners
              </Alert>
              <Typography variant="body2">
                Confidence boost: +{(path.collaborative_insights.confidence_boost * 100).toFixed(1)}%
              </Typography>
            </Box>
          )}

          {/* Action Buttons */}
          <Box display="flex" gap={2} mt={3}>
            <Button 
              variant="contained" 
              startIcon={<CheckCircle />}
              onClick={() => setError('Path saved! (Demo - not actually saved)')}
            >
              Save Path
            </Button>
            <Button 
              variant="outlined" 
              startIcon={<Timeline />}
              onClick={() => setError('Path started! (Demo - not actually started)')}
            >
              Start Learning
            </Button>
          </Box>
        </CardContent>
      </Card>
    );
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Learning Path Generator
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Create personalized learning paths using AI-powered curriculum sequencing
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Configuration Panel */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Path Configuration
              </Typography>

              {/* Topic Selection */}
              <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                Select Topics ({selectedTopics.length} selected)
              </Typography>
              <Box sx={{ maxHeight: 300, overflow: 'auto', mb: 3 }}>
                {topics.map((topic) => (
                  <Chip
                    key={topic.id}
                    label={topic.name}
                    onClick={() => handleTopicToggle(topic.id)}
                    color={selectedTopics.includes(topic.id) ? 'primary' : 'default'}
                    variant={selectedTopics.includes(topic.id) ? 'filled' : 'outlined'}
                    sx={{ m: 0.5 }}
                    size="small"
                  />
                ))}
              </Box>

              {/* Generation Settings */}
              <Typography variant="subtitle2" gutterBottom>
                Generation Settings
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" gutterBottom>
                  Max Difficulty Jump: {generationSettings.maxDifficultyJump}
                </Typography>
                <Slider
                  value={generationSettings.maxDifficultyJump}
                  onChange={(e, value) => setGenerationSettings(prev => ({
                    ...prev,
                    maxDifficultyJump: value
                  }))}
                  min={0.5}
                  max={5.0}
                  step={0.5}
                  marks
                  valueLabelDisplay="auto"
                />
              </Box>

              <TextField
                label="Preferred Duration (minutes)"
                type="number"
                value={generationSettings.preferredDuration || ''}
                onChange={(e) => setGenerationSettings(prev => ({
                  ...prev,
                  preferredDuration: e.target.value ? parseInt(e.target.value) : null
                }))}
                fullWidth
                sx={{ mb: 2 }}
                helperText="Leave empty for no time constraint"
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={generationSettings.useCollaborative}
                    onChange={(e) => setGenerationSettings(prev => ({
                      ...prev,
                      useCollaborative: e.target.checked
                    }))}
                  />
                }
                label="Use Collaborative Filtering"
              />

              <Button
                variant="contained"
                fullWidth
                onClick={generatePath}
                disabled={loading || selectedTopics.length === 0}
                startIcon={loading ? <CircularProgress size={20} /> : <Science />}
                sx={{ mt: 3 }}
              >
                {loading ? 'Generating...' : 'Generate Learning Path'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Results Panel */}
        <Grid item xs={12} md={8}>
          {!generatedPath ? (
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 8 }}>
                <Psychology sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="textSecondary" gutterBottom>
                  Configure and Generate Your Learning Path
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Select topics and adjust settings to create a personalized learning experience
                </Typography>
              </CardContent>
            </Card>
          ) : (
            <PathVisualization path={generatedPath} />
          )}
        </Grid>
      </Grid>
    </Container>
  );
}

export default PathGenerator;
