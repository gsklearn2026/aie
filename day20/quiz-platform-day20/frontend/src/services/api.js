import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const relationshipService = {
  // Topics
  getTopics: () => api.get('/relationships/topics/'),
  getTopic: (id) => api.get(`/relationships/topics/${id}`),
  createTopic: (data) => api.post('/relationships/topics/', data),
  
  // Relationships
  createRelationship: (data) => api.post('/relationships/', data),
  getRelatedTopics: (topicId, params = {}) => 
    api.get(`/relationships/topics/${topicId}/related`, { params }),
  
  // AI Discovery
  discoverRelationships: (data) => api.post('/relationships/discover', data),
  validateRelationship: (relationshipId, data) => 
    api.post(`/relationships/validate/${relationshipId}`, data),
  
  // Analysis
  getLearningPath: (startId, endId) => 
    api.get('/relationships/learning-path', { 
      params: { start_topic_id: startId, end_topic_id: endId } 
    }),
  getClusters: () => api.get('/relationships/clusters'),
  getGraphVisualization: () => api.get('/relationships/visualization'),
  getStatistics: () => api.get('/relationships/statistics'),
};

export default api;
