import React, { useState, useEffect } from 'react';
import {
  Container, Typography, Box, Card, CardContent, Button,
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Select, MenuItem, FormControl, InputLabel,
  List, ListItem, ListItemText, ListItemSecondaryAction,
  IconButton, Chip, Alert, Grid
} from '@mui/material';
import { Add, Visibility, Check, Close } from '@mui/icons-material';
import TopicGraph from './TopicGraph';
import { relationshipService } from '../services/api';

const RelationshipManager = () => {
  const [topics, setTopics] = useState([]);
  const [relationships, setRelationships] = useState([]);
  const [graphData, setGraphData] = useState(null);
  const [statistics, setStatistics] = useState({});
  
  // Dialog states
  const [topicDialog, setTopicDialog] = useState(false);
  const [relationshipDialog, setRelationshipDialog] = useState(false);
  const [discoveryDialog, setDiscoveryDialog] = useState(false);
  
  // Form states
  const [newTopic, setNewTopic] = useState({
    name: '', description: '', category: '', difficulty_level: 1
  });
  const [newRelationship, setNewRelationship] = useState({
    source_topic_id: '', target_topic_id: '', relationship_type: 'similar', strength: 0.5
  });
  const [selectedTopics, setSelectedTopics] = useState([]);
  
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState(null);

  const relationshipTypes = [
    'prerequisite', 'corequisite', 'similar', 'builds_on', 'applies_to'
  ];

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [topicsRes, graphRes, statsRes] = await Promise.all([
        relationshipService.getTopics(),
        relationshipService.getGraphVisualization(),
        relationshipService.getStatistics()
      ]);
      
      setTopics(topicsRes.data);
      setGraphData(graphRes.data);
      setStatistics(statsRes.data);
    } catch (error) {
      setAlert({ severity: 'error', message: 'Failed to load data' });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTopic = async () => {
    try {
      await relationshipService.createTopic(newTopic);
      setTopicDialog(false);
      setNewTopic({ name: '', description: '', category: '', difficulty_level: 1 });
      loadData();
      setAlert({ severity: 'success', message: 'Topic created successfully' });
    } catch (error) {
      setAlert({ severity: 'error', message: 'Failed to create topic' });
    }
  };

  const handleCreateRelationship = async () => {
    try {
      await relationshipService.createRelationship(newRelationship);
      setRelationshipDialog(false);
      setNewRelationship({
        source_topic_id: '', target_topic_id: '', relationship_type: 'similar', strength: 0.5
      });
      loadData();
      setAlert({ severity: 'success', message: 'Relationship created successfully' });
    } catch (error) {
      setAlert({ severity: 'error', message: 'Failed to create relationship' });
    }
  };

  const handleDiscoverRelationships = async () => {
    if (selectedTopics.length < 2) {
      setAlert({ severity: 'warning', message: 'Select at least 2 topics for discovery' });
      return;
    }

    try {
      setLoading(true);
      const response = await relationshipService.discoverRelationships({
        topic_ids: selectedTopics,
        max_relationships: 20
      });
      
      setDiscoveryDialog(false);
      loadData();
      setAlert({ 
        severity: 'success', 
        message: `Discovered ${response.data.count} new relationships` 
      });
    } catch (error) {
      setAlert({ severity: 'error', message: 'Failed to discover relationships' });
    } finally {
      setLoading(false);
    }
  };

  const handleRunFullDemo = async () => {
    try {
      setLoading(true);
      setAlert({ severity: 'info', message: 'Running full demo... This may take a moment.' });
      
      // Demo topics with comprehensive coverage
      const demoTopics = [
        { name: 'Mathematics Fundamentals', description: 'Core mathematical concepts', category: 'Mathematics', difficulty_level: 1 },
        { name: 'Calculus', description: 'Differential and integral calculus', category: 'Mathematics', difficulty_level: 3 },
        { name: 'Probability Theory', description: 'Probability and random variables', category: 'Mathematics', difficulty_level: 3 },
        { name: 'Linear Algebra', description: 'Vectors, matrices, and transformations', category: 'Mathematics', difficulty_level: 3 },
        { name: 'Statistics', description: 'Statistical analysis and inference', category: 'Mathematics', difficulty_level: 2 },
        { name: 'Python Basics', description: 'Python programming fundamentals', category: 'Programming', difficulty_level: 1 },
        { name: 'Data Structures', description: 'Arrays, lists, trees, graphs', category: 'Computer Science', difficulty_level: 2 },
        { name: 'Algorithms', description: 'Algorithm design and analysis', category: 'Computer Science', difficulty_level: 3 },
        { name: 'Object-Oriented Programming', description: 'OOP principles and patterns', category: 'Programming', difficulty_level: 2 },
        { name: 'Database Design', description: 'Database modeling and SQL', category: 'Computer Science', difficulty_level: 2 },
        { name: 'Machine Learning', description: 'ML algorithms and concepts', category: 'AI', difficulty_level: 4 },
        { name: 'Deep Learning', description: 'Neural networks and deep learning', category: 'AI', difficulty_level: 5 },
        { name: 'Computer Vision', description: 'Image processing and recognition', category: 'AI', difficulty_level: 4 },
        { name: 'Natural Language Processing', description: 'Text processing and language models', category: 'AI', difficulty_level: 4 },
        { name: 'Data Science', description: 'Data analysis and visualization', category: 'Data Science', difficulty_level: 3 },
        { name: 'Big Data', description: 'Large-scale data processing', category: 'Data Science', difficulty_level: 4 },
        { name: 'Cloud Computing', description: 'Cloud platforms and services', category: 'Technology', difficulty_level: 3 },
        { name: 'DevOps', description: 'Development and operations practices', category: 'Technology', difficulty_level: 3 },
        { name: 'Software Engineering', description: 'Software development methodologies', category: 'Technology', difficulty_level: 3 },
        { name: 'Cybersecurity', description: 'Security principles and practices', category: 'Technology', difficulty_level: 4 },
        { name: 'Blockchain', description: 'Distributed ledger technology', category: 'Technology', difficulty_level: 4 }
      ];

      // Create all demo topics
      const createdTopics = [];
      for (const topicData of demoTopics) {
        try {
          const response = await relationshipService.createTopic(topicData);
          createdTopics.push(response.data);
        } catch (error) {
          console.log(`Topic ${topicData.name} already exists or failed to create`);
        }
      }

      // Create demo relationships
      const demoRelationships = [
        { source_topic_id: 1, target_topic_id: 2, relationship_type: 'prerequisite', strength: 0.9 }, // Math Fundamentals -> Calculus
        { source_topic_id: 1, target_topic_id: 3, relationship_type: 'prerequisite', strength: 0.8 }, // Math Fundamentals -> Probability
        { source_topic_id: 1, target_topic_id: 4, relationship_type: 'prerequisite', strength: 0.8 }, // Math Fundamentals -> Linear Algebra
        { source_topic_id: 2, target_topic_id: 11, relationship_type: 'prerequisite', strength: 0.7 }, // Calculus -> Machine Learning
        { source_topic_id: 4, target_topic_id: 11, relationship_type: 'prerequisite', strength: 0.9 }, // Linear Algebra -> Machine Learning
        { source_topic_id: 3, target_topic_id: 5, relationship_type: 'builds_on', strength: 0.8 }, // Probability -> Statistics
        { source_topic_id: 5, target_topic_id: 11, relationship_type: 'prerequisite', strength: 0.8 }, // Statistics -> Machine Learning
        { source_topic_id: 6, target_topic_id: 7, relationship_type: 'prerequisite', strength: 0.7 }, // Python Basics -> Data Structures
        { source_topic_id: 6, target_topic_id: 8, relationship_type: 'prerequisite', strength: 0.7 }, // Python Basics -> Algorithms
        { source_topic_id: 7, target_topic_id: 8, relationship_type: 'corequisite', strength: 0.8 }, // Data Structures <-> Algorithms
        { source_topic_id: 6, target_topic_id: 9, relationship_type: 'prerequisite', strength: 0.6 }, // Python Basics -> OOP
        { source_topic_id: 9, target_topic_id: 10, relationship_type: 'applies_to', strength: 0.7 }, // OOP -> Database Design
        { source_topic_id: 11, target_topic_id: 12, relationship_type: 'prerequisite', strength: 0.9 }, // Machine Learning -> Deep Learning
        { source_topic_id: 12, target_topic_id: 13, relationship_type: 'applies_to', strength: 0.8 }, // Deep Learning -> Computer Vision
        { source_topic_id: 12, target_topic_id: 14, relationship_type: 'applies_to', strength: 0.8 }, // Deep Learning -> NLP
        { source_topic_id: 5, target_topic_id: 15, relationship_type: 'applies_to', strength: 0.8 }, // Statistics -> Data Science
        { source_topic_id: 15, target_topic_id: 16, relationship_type: 'builds_on', strength: 0.7 }, // Data Science -> Big Data
        { source_topic_id: 10, target_topic_id: 16, relationship_type: 'applies_to', strength: 0.6 }, // Database Design -> Big Data
        { source_topic_id: 16, target_topic_id: 17, relationship_type: 'applies_to', strength: 0.7 }, // Big Data -> Cloud Computing
        { source_topic_id: 9, target_topic_id: 18, relationship_type: 'applies_to', strength: 0.7 }, // OOP -> Software Engineering
        { source_topic_id: 18, target_topic_id: 19, relationship_type: 'applies_to', strength: 0.6 }, // Software Engineering -> DevOps
        { source_topic_id: 19, target_topic_id: 20, relationship_type: 'applies_to', strength: 0.6 }, // DevOps -> Cybersecurity
        { source_topic_id: 20, target_topic_id: 21, relationship_type: 'applies_to', strength: 0.5 }, // Cybersecurity -> Blockchain
        { source_topic_id: 8, target_topic_id: 21, relationship_type: 'applies_to', strength: 0.6 }, // Algorithms -> Blockchain
        { source_topic_id: 11, target_topic_id: 15, relationship_type: 'applies_to', strength: 0.8 }, // Machine Learning -> Data Science
        { source_topic_id: 13, target_topic_id: 14, relationship_type: 'similar', strength: 0.6 }, // Computer Vision <-> NLP
        { source_topic_id: 17, target_topic_id: 18, relationship_type: 'applies_to', strength: 0.6 }  // Cloud Computing -> Software Engineering
      ];

      // Create relationships (using topic names to find IDs)
      for (const relData of demoRelationships) {
        try {
          const sourceTopic = createdTopics.find(t => t.id === relData.source_topic_id);
          const targetTopic = createdTopics.find(t => t.id === relData.target_topic_id);
          
          if (sourceTopic && targetTopic) {
            await relationshipService.createRelationship({
              source_topic_id: sourceTopic.id,
              target_topic_id: targetTopic.id,
              relationship_type: relData.relationship_type,
              strength: relData.strength
            });
          }
        } catch (error) {
          console.log(`Relationship creation failed: ${error.message}`);
        }
      }

      // Reload data to show the new content
      await loadData();
      
      setAlert({ 
        severity: 'success', 
        message: `Demo completed! Created ${createdTopics.length} topics and ${demoRelationships.length} relationships.` 
      });
    } catch (error) {
      console.error('Demo error:', error);
      setAlert({ severity: 'error', message: 'Demo failed to complete. Check console for details.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Topic Relationship Manager
      </Typography>

      {alert && (
        <Alert 
          severity={alert.severity} 
          onClose={() => setAlert(null)}
          sx={{ mb: 2 }}
        >
          {alert.message}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Statistics */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>System Statistics</Typography>
              <Box sx={{ display: 'flex', gap: 4 }}>
                <Box>
                  <Typography variant="h4" color="primary">
                    {statistics.total_topics || 0}
                  </Typography>
                  <Typography variant="body2">Topics</Typography>
                </Box>
                <Box>
                  <Typography variant="h4" color="secondary">
                    {statistics.total_relationships || 0}
                  </Typography>
                  <Typography variant="body2">Relationships</Typography>
                </Box>
                <Box>
                  <Typography variant="h4" color="success.main">
                    {Math.round((statistics.average_connections || 0) * 10) / 10}
                  </Typography>
                  <Typography variant="body2">Avg Connections</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Actions */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
            <Button 
              variant="contained" 
              startIcon={<Add />}
              onClick={() => setTopicDialog(true)}
            >
              Add Topic
            </Button>
            <Button 
              variant="outlined" 
              onClick={() => setRelationshipDialog(true)}
            >
              Add Relationship
            </Button>
            <Button 
              variant="outlined" 
              color="secondary"
              onClick={() => setDiscoveryDialog(true)}
            >
              AI Discovery
            </Button>
            <Button 
              variant="contained" 
              color="success"
              onClick={handleRunFullDemo}
              disabled={loading}
              sx={{ 
                background: 'linear-gradient(45deg, #4CAF50 30%, #45a049 90%)',
                '&:hover': {
                  background: 'linear-gradient(45deg, #45a049 30%, #4CAF50 90%)',
                }
              }}
            >
              🚀 Run Full Demo
            </Button>
          </Box>
        </Grid>

        {/* Graph Visualization */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Knowledge Graph Visualization
              </Typography>
              {graphData && <TopicGraph data={graphData} />}
            </CardContent>
          </Card>
        </Grid>

        {/* Topics List */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Topics</Typography>
              <List sx={{ maxHeight: 400, overflow: 'auto' }}>
                {topics.map((topic) => (
                  <ListItem key={topic.id}>
                    <ListItemText
                      primary={topic.name}
                      secondary={`${topic.category} - Level ${topic.difficulty_level}`}
                    />
                    <ListItemSecondaryAction>
                      <Chip 
                        label={topic.category} 
                        size="small" 
                        variant="outlined" 
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Most Connected Topics */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Most Connected Topics</Typography>
              <List sx={{ maxHeight: 400, overflow: 'auto' }}>
                {(statistics.most_connected_topics || []).map((topic) => (
                  <ListItem key={topic.topic_id}>
                    <ListItemText
                      primary={topic.topic_name}
                      secondary={`${topic.connections} connections`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Add Topic Dialog */}
      <Dialog open={topicDialog} onClose={() => setTopicDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Topic</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Topic Name"
            value={newTopic.name}
            onChange={(e) => setNewTopic({...newTopic, name: e.target.value})}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Description"
            multiline
            rows={3}
            value={newTopic.description}
            onChange={(e) => setNewTopic({...newTopic, description: e.target.value})}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Category"
            value={newTopic.category}
            onChange={(e) => setNewTopic({...newTopic, category: e.target.value})}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Difficulty Level"
            type="number"
            inputProps={{ min: 1, max: 10 }}
            value={newTopic.difficulty_level}
            onChange={(e) => setNewTopic({...newTopic, difficulty_level: parseInt(e.target.value)})}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTopicDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateTopic} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>

      {/* Add Relationship Dialog */}
      <Dialog open={relationshipDialog} onClose={() => setRelationshipDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Relationship</DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin="normal">
            <InputLabel>Source Topic</InputLabel>
            <Select
              value={newRelationship.source_topic_id}
              onChange={(e) => setNewRelationship({...newRelationship, source_topic_id: e.target.value})}
            >
              {topics.map((topic) => (
                <MenuItem key={topic.id} value={topic.id}>{topic.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <FormControl fullWidth margin="normal">
            <InputLabel>Target Topic</InputLabel>
            <Select
              value={newRelationship.target_topic_id}
              onChange={(e) => setNewRelationship({...newRelationship, target_topic_id: e.target.value})}
            >
              {topics.map((topic) => (
                <MenuItem key={topic.id} value={topic.id}>{topic.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <FormControl fullWidth margin="normal">
            <InputLabel>Relationship Type</InputLabel>
            <Select
              value={newRelationship.relationship_type}
              onChange={(e) => setNewRelationship({...newRelationship, relationship_type: e.target.value})}
            >
              {relationshipTypes.map((type) => (
                <MenuItem key={type} value={type}>{type}</MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <TextField
            fullWidth
            label="Strength (0.0 - 1.0)"
            type="number"
            inputProps={{ min: 0, max: 1, step: 0.1 }}
            value={newRelationship.strength}
            onChange={(e) => setNewRelationship({...newRelationship, strength: parseFloat(e.target.value)})}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRelationshipDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateRelationship} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>

      {/* AI Discovery Dialog */}
      <Dialog open={discoveryDialog} onClose={() => setDiscoveryDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>AI Relationship Discovery</DialogTitle>
        <DialogContent>
          <Typography gutterBottom>
            Select topics for AI to analyze and discover relationships:
          </Typography>
          <FormControl fullWidth margin="normal">
            <InputLabel>Select Topics</InputLabel>
            <Select
              multiple
              value={selectedTopics}
              onChange={(e) => setSelectedTopics(e.target.value)}
              renderValue={(selected) => 
                selected.map(id => topics.find(t => t.id === id)?.name).join(', ')
              }
            >
              {topics.map((topic) => (
                <MenuItem key={topic.id} value={topic.id}>{topic.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDiscoveryDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleDiscoverRelationships} 
            variant="contained" 
            disabled={selectedTopics.length < 2}
          >
            Discover Relationships
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default RelationshipManager;
