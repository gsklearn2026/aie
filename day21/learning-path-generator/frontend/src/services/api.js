import axios from 'axios';

const BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Learning Paths API
export const learningPathApi = {
  generatePath: async (request) => {
    const response = await api.post('/learning-paths/generate', request);
    return response.data;
  },

  getUserPaths: async (userId) => {
    const response = await api.get(`/learning-paths/${userId}`);
    return response.data;
  },

  updateProgress: async (userId, progressData) => {
    const response = await api.put(`/learning-paths/${userId}/progress`, progressData);
    return response.data;
  },

  getNextTopics: async (userId, count = 3) => {
    const response = await api.get(`/learning-paths/${userId}/next-topics?count=${count}`);
    return response.data;
  },

  deletePath: async (pathId) => {
    const response = await api.delete(`/learning-paths/${pathId}`);
    return response.data;
  },
};

// Topics API
export const topicsApi = {
  getTopics: async (skip = 0, limit = 100) => {
    const response = await api.get(`/topics?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  createTopic: async (topicData) => {
    const response = await api.post('/topics', topicData);
    return response.data;
  },

  getTopicRelationships: async (topicId) => {
    const response = await api.get(`/topics/${topicId}/relationships`);
    return response.data;
  },
};

// Users API
export const usersApi = {
  createUser: async (userData) => {
    const response = await api.post('/users', userData);
    return response.data;
  },

  getUser: async (userId) => {
    const response = await api.get(`/users/${userId}`);
    return response.data;
  },

  getUserProgress: async (userId) => {
    const response = await api.get(`/users/${userId}/progress`);
    return response.data;
  },
};

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    throw error;
  }
);

export default api;
