import axios from 'axios';
import config from '../config';

const api = axios.create({
  baseURL: config.apiUrl,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Log error details for debugging
      const errorData = error.response.data;
      if (errorData?.detail) {
        console.error('API Error:', errorData.detail);
      } else {
        console.error('API Error:', errorData);
      }
    } else if (error.request) {
      console.error('Network Error:', error.message);
    } else {
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export const quizService = {
  generateQuiz: async (data) => {
    const response = await api.post('/api/v1/quizzes/generate', data);
    return response.data;
  },
  
  getQuiz: async (id) => {
    const response = await api.get(`/api/v1/quizzes/${id}`);
    return response.data;
  },
  
  listQuizzes: async (params = {}) => {
    const response = await api.get('/api/v1/quizzes/', { params });
    return response.data;
  }
};

export const healthService = {
  checkHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  },
  
  checkReadiness: async () => {
    const response = await api.get('/health/ready');
    return response.data;
  }
};

export default api;
