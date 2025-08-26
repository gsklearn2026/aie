import React, { useState, useEffect } from 'react';
import {
  Container,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Grid,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  CheckCircle,
  PlayCircle,
  Pause,
  TrendingUp,
  School,
  Timer,
  Edit,
} from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { usersApi, learningPathApi } from '../services/api';

function UserProgress() {
  const [userProgress, setUserProgress] = useState([]);
  const [userStats, setUserStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [editDialog, setEditDialog] = useState({ open: false, topic: null });
  const [progressData, setProgressData] = useState([]);

  useEffect(() => {
    loadUserProgress();
  }, []);

  const loadUserProgress = async () => {
    try {
      setLoading(true);
      const userId = 1; // Demo user
      
      const progressResponse = await usersApi.getUserProgress(userId);
      setUserProgress(progressResponse.progress);
      
      const stats = {
        totalTopics: progressResponse.total_topics,
        completedTopics: progressResponse.completed_topics,
        avgMastery: progressResponse.progress.length > 0 
          ? progressResponse.progress.reduce((sum, p) => sum + p.mastery_level, 0) / progressResponse.progress.length 
          : 0,
        totalTimeSpent: progressResponse.progress.reduce((sum, p) => sum + p.time_spent, 0)
      };
      setUserStats(stats);

      // Create progress chart data
      const chartData = progressResponse.progress.map(p => ({
        topic_id: p.topic_id,
        mastery: p.mastery_level * 100,
        time_spent: p.time_spent,
        attempts: p.attempts
      }));
      setProgressData(chartData);

    } catch (error) {
      console.error('Error loading user progress:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProgress = async (topicId, updateData) => {
    try {
      await learningPathApi.updateProgress(1, {
        topic_id: topicId,
        ...updateData
      });
      
      // Reload progress data
      loadUserProgress();
      setEditDialog({ open: false, topic: null });
      
    } catch (error) {
      console.error('Error updating progress:', error);
    }
  };

  const ProgressEditDialog = () => {
    const [formData, setFormData] = useState({
      mastery_level: 0,
      completion_status: 'not_started',
      time_spent: 0
    });

    useEffect(() => {
      if (editDialog.topic) {
        setFormData({
          mastery_level: editDialog.topic.mastery_level,
          completion_status: editDialog.topic.completion_status,
          time_spent: 30 // Add 30 minutes by default
        });
      }
    }, [editDialog.topic]);

    return (
      <Dialog open={editDialog.open} onClose={() => setEditDialog({ open: false, topic: null })}>
        <DialogTitle>Update Progress</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, minWidth: 400 }}>
            <Typography gutterBottom>
              Mastery Level: {(formData.mastery_level * 100).toFixed(0)}%
            </Typography>
            <Slider
              value={formData.mastery_level}
              onChange={(e, value) => setFormData(prev => ({ ...prev, mastery_level: value }))}
              min={0}
              max={1}
              step={0.1}
              marks
              valueLabelDisplay="auto"
              valueLabelFormat={(value) => `${(value * 100).toFixed(0)}%`}
              sx={{ mb: 3 }}
            />

            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Completion Status</InputLabel>
              <Select
                value={formData.completion_status}
                onChange={(e) => setFormData(prev => ({ ...prev, completion_status: e.target.value }))}
                label="Completion Status"
              >
                <MenuItem value="not_started">Not Started</MenuItem>
                <MenuItem value="in_progress">In Progress</MenuItem>
                <MenuItem value="completed">Completed</MenuItem>
              </Select>
            </FormControl>

            <TextField
              label="Additional Time Spent (minutes)"
              type="number"
              value={formData.time_spent}
              onChange={(e) => setFormData(prev => ({ ...prev, time_spent: parseInt(e.target.value) || 0 }))}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog({ open: false, topic: null })}>
            Cancel
          </Button>
          <Button 
            onClick={() => handleUpdateProgress(editDialog.topic.topic_id, formData)}
            variant="contained"
          >
            Update
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle sx={{ color: 'success.main' }} />;
      case 'in_progress':
        return <PlayCircle sx={{ color: 'warning.main' }} />;
      default:
        return <Pause sx={{ color: 'text.secondary' }} />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'warning';
      default:
        return 'default';
    }
  };

  // Sample radar chart data
  const radarData = [
    { subject: 'Fundamentals', A: userStats.avgMastery * 100, fullMark: 100 },
    { subject: 'Intermediate', A: (userStats.avgMastery * 0.8) * 100, fullMark: 100 },
    { subject: 'Advanced', A: (userStats.avgMastery * 0.6) * 100, fullMark: 100 },
    { subject: 'Practical', A: (userStats.avgMastery * 0.9) * 100, fullMark: 100 },
    { subject: 'Theory', A: (userStats.avgMastery * 0.7) * 100, fullMark: 100 },
  ];

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
          <LinearProgress sx={{ width: '50%' }} />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Learning Progress
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Track your mastery across all topics and learning paths
      </Typography>

      {/* Stats Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <School sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
              <Typography variant="h4" color="primary">
                {userStats.totalTopics}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Total Topics
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <CheckCircle sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
              <Typography variant="h4" color="success.main">
                {userStats.completedTopics}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Completed
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <TrendingUp sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
              <Typography variant="h4" color="warning.main">
                {(userStats.avgMastery * 100).toFixed(0)}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Avg Mastery
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Timer sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
              <Typography variant="h4" color="info.main">
                {Math.round(userStats.totalTimeSpent / 60)}h
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Time Spent
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Progress Chart */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Mastery Levels by Topic
              </Typography>
              <Box height={300}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={progressData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="topic_id" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="mastery" fill="#667eea" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Skill Radar */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Skill Areas
              </Typography>
              <Box height={300}>
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={radarData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="subject" />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} />
                    <Radar
                      name="Mastery"
                      dataKey="A"
                      stroke="#667eea"
                      fill="#667eea"
                      fillOpacity={0.3}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Detailed Progress List */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Detailed Progress
              </Typography>
              <List>
                {userProgress.map((progress) => (
                  <ListItem 
                    key={progress.topic_id}
                    divider
                    sx={{ 
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 2,
                      mb: 1,
                      bgcolor: 'background.paper'
                    }}
                  >
                    <ListItemIcon>
                      {getStatusIcon(progress.completion_status)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="subtitle1">
                            Topic {progress.topic_id}
                          </Typography>
                          <Chip 
                            label={progress.completion_status.replace('_', ' ')}
                            size="small"
                            color={getStatusColor(progress.completion_status)}
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Box display="flex" justifyContent="between" alignItems="center" mb={1}>
                            <Typography variant="body2" color="textSecondary">
                              Mastery: {(progress.mastery_level * 100).toFixed(0)}% • 
                              Time: {progress.time_spent} min • 
                              Attempts: {progress.attempts}
                            </Typography>
                          </Box>
                          <LinearProgress 
                            variant="determinate" 
                            value={progress.mastery_level * 100}
                            sx={{ height: 6, borderRadius: 3 }}
                          />
                        </Box>
                      }
                    />
                    <Button
                      startIcon={<Edit />}
                      onClick={() => setEditDialog({ open: true, topic: progress })}
                      size="small"
                    >
                      Update
                    </Button>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <ProgressEditDialog />
    </Container>
  );
}

export default UserProgress;
