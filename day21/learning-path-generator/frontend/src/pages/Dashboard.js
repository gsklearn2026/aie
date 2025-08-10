import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  IconButton,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Avatar,
  Paper,
  Button,
  Snackbar,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  School,
  Timer,
  PlayArrow,
  CheckCircle,
  Assignment,
  PlayCircle,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { learningPathApi } from '../services/api';
import { demoService } from '../services/demoData';

const COLORS = ['#667eea', '#764ba2', '#ffa726', '#66bb6a', '#ef5350'];

function Dashboard() {
  const [userStats, setUserStats] = useState({
    totalPaths: 0,
    completedTopics: 0,
    totalTopics: 0,
    avgMastery: 0,
    learningStreak: 0
  });
  const [recentPaths, setRecentPaths] = useState([]);
  const [progressData, setProgressData] = useState([]);
  const [nextTopics, setNextTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [demoLoading, setDemoLoading] = useState(false);
  const [demoMessage, setDemoMessage] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // For demo, using user_id = 1
      const userId = 1;
      
      // Load user paths
      const pathsResponse = await learningPathApi.getUserPaths(userId);
      setRecentPaths(pathsResponse.paths.slice(0, 5));
      
      // Load next topics
      const nextTopicsResponse = await learningPathApi.getNextTopics(userId, 3);
      setNextTopics(nextTopicsResponse.recommendations);
      
      // Load user progress
      const progressResponse = await learningPathApi.getUserProgress(userId);
      
      // Calculate stats
      const stats = {
        totalPaths: pathsResponse.paths.length,
        completedTopics: progressResponse.completed_topics,
        totalTopics: progressResponse.total_topics,
        avgMastery: progressResponse.progress.length > 0 
          ? progressResponse.progress.reduce((sum, p) => sum + p.mastery_level, 0) / progressResponse.progress.length 
          : 0,
        learningStreak: Math.floor(Math.random() * 15) + 1 // Mock streak
      };
      setUserStats(stats);
      
      // Mock progress chart data
      const chartData = [
        { day: 'Mon', mastery: 0.6, topics: 2 },
        { day: 'Tue', mastery: 0.65, topics: 3 },
        { day: 'Wed', mastery: 0.7, topics: 2 },
        { day: 'Thu', mastery: 0.75, topics: 4 },
        { day: 'Fri', mastery: 0.8, topics: 3 },
        { day: 'Sat', mastery: 0.82, topics: 1 },
        { day: 'Sun', mastery: 0.85, topics: 2 }
      ];
      setProgressData(chartData);
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRunDemo = async () => {
    try {
      setDemoLoading(true);
      const result = await demoService.runFullDemo();
      
      setDemoMessage({
        open: true,
        message: result.message,
        severity: result.success ? 'success' : 'warning'
      });
      
      if (result.success) {
        // Reload dashboard data after successful demo
        setTimeout(() => {
          loadDashboardData();
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

  const StatCard = ({ icon: Icon, title, value, subtitle, color }) => (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div" style={{ color }}>
              {value}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {subtitle}
            </Typography>
          </Box>
          <Avatar style={{ backgroundColor: color + '20', color }}>
            <Icon />
          </Avatar>
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
          <LinearProgress sx={{ width: '50%' }} />
        </Box>
      </Container>
    );
  }

  const completionRate = userStats.totalTopics > 0 
    ? (userStats.completedTopics / userStats.totalTopics) * 100 
    : 0;

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Learning Dashboard
          </Typography>
          <Typography variant="body1" color="textSecondary" paragraph>
            Track your learning progress and discover new paths
          </Typography>
        </Box>
        
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
          {demoLoading ? 'Running Demo...' : '🚀 Run Full Demo'}
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

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={Assignment}
            title="Active Paths"
            value={userStats.totalPaths}
            subtitle="Learning paths"
            color="#667eea"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={CheckCircle}
            title="Completion Rate"
            value={`${completionRate.toFixed(1)}%`}
            subtitle={`${userStats.completedTopics}/${userStats.totalTopics} topics`}
            color="#66bb6a"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={TrendingUp}
            title="Avg Mastery"
            value={`${(userStats.avgMastery * 100).toFixed(0)}%`}
            subtitle="Across all topics"
            color="#ffa726"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={Timer}
            title="Learning Streak"
            value={`${userStats.learningStreak} days`}
            subtitle="Keep it up!"
            color="#ef5350"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Progress Chart */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Weekly Progress
              </Typography>
              <Box height={300}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={progressData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" />
                    <YAxis />
                    <Tooltip />
                    <Line 
                      type="monotone" 
                      dataKey="mastery" 
                      stroke="#667eea" 
                      strokeWidth={3}
                      dot={{ fill: '#667eea', strokeWidth: 2, r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Next Recommended Topics */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Next Recommended
              </Typography>
              <List>
                {nextTopics.map((topic, index) => (
                  <ListItem key={topic.topic_id} divider={index < nextTopics.length - 1}>
                    <ListItemText
                      primary={topic.name}
                      secondary={
                        <Box>
                          <Typography variant="body2" color="textSecondary">
                            {topic.estimated_duration} min
                          </Typography>
                          <Box display="flex" alignItems="center" mt={1}>
                            <Box flex={1} mr={1}>
                              <LinearProgress 
                                variant="determinate" 
                                value={topic.difficulty_level * 10} 
                                sx={{ height: 6, borderRadius: 3 }}
                              />
                            </Box>
                            <Typography variant="caption">
                              {topic.difficulty_level}/10
                            </Typography>
                          </Box>
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <IconButton edge="end" size="small" sx={{ color: '#667eea' }}>
                        <PlayArrow />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Learning Paths */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Learning Paths
              </Typography>
              <Grid container spacing={2}>
                {recentPaths.map((path) => (
                  <Grid item xs={12} sm={6} md={4} key={path.path_id}>
                    <Paper 
                      elevation={2} 
                      sx={{ 
                        p: 2, 
                        borderRadius: 2,
                        border: '1px solid',
                        borderColor: 'rgba(0,0,0,0.1)',
                        '&:hover': {
                          borderColor: '#667eea',
                          transform: 'translateY(-2px)',
                          transition: 'all 0.3s ease'
                        }
                      }}
                    >
                      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                        <Typography variant="subtitle1" fontWeight={600}>
                          {path.path_name}
                        </Typography>
                        <Chip 
                          label={path.is_active ? 'Active' : 'Completed'} 
                          size="small"
                          color={path.is_active ? 'primary' : 'default'}
                        />
                      </Box>
                      
                      <Typography variant="body2" color="textSecondary" mb={2}>
                        {path.topic_sequence.length} topics • {path.estimated_duration} min
                      </Typography>
                      
                      <Box>
                        <Box display="flex" justifyContent="space-between" mb={1}>
                          <Typography variant="body2">Progress</Typography>
                          <Typography variant="body2">{(path.completion_rate * 100).toFixed(0)}%</Typography>
                        </Box>
                        <LinearProgress 
                          variant="determinate" 
                          value={path.completion_rate * 100}
                          sx={{ height: 8, borderRadius: 4 }}
                        />
                      </Box>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
}

export default Dashboard;
