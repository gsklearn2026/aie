import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: async (userData) => {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  },
  
  login: async (email, password) => {
    const response = await api.post('/api/auth/login', { email, password });
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  }
};

// Quiz API
export const quizAPI = {
  generateQuiz: async (quizData) => {
    const response = await api.post('/api/quizzes/generate', quizData);
    return response.data;
  },
  
  getQuizzes: async () => {
    const response = await api.get('/api/quizzes');
    return response.data;
  },
  
  getQuiz: async (quizId) => {
    const response = await api.get(`/api/quizzes/${quizId}`);
    return response.data;
  },
  
  submitQuizAttempt: async (quizId, answers) => {
    const response = await api.post(`/api/quizzes/${quizId}/attempt`, { 
      quiz_id: quizId, 
      answers 
    });
    return response.data;
  }
};

// Health check API
export const healthAPI = {
  check: async () => {
    const response = await api.get('/api/health');
    return response.data;
  }
};

export default api;
