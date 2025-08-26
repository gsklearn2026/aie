import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with interceptors for cache headers
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Add request interceptor to log cache-related headers
api.interceptors.response.use(
  (response) => {
    // Log cache performance data
    const cacheStrategy = response.headers['x-cache-strategy'];
    const processTime = response.headers['x-process-time'];
    
    if (cacheStrategy) {
      console.log(`Cache Strategy: ${cacheStrategy}, Process Time: ${processTime}ms`);
    }
    
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const quizAPI = {
  getQuiz: (quizId) => api.get(`/api/v1/quiz/${quizId}`),
  getUserProgress: (quizId, userId) => api.get(`/api/v1/quiz/${quizId}/progress/${userId}`),
  getLeaderboard: (quizId) => api.get(`/api/v1/quiz/${quizId}/leaderboard`),
  getAIExplanation: (quizId, topic) => api.get(`/api/v1/quiz/${quizId}/explanation/${topic}`),
  invalidateQuizCache: (quizId) => api.post(`/api/v1/quiz/${quizId}/invalidate`),
};

export const cacheAPI = {
  getStats: () => api.get('/api/v1/cache/stats'),
  flushCache: () => api.post('/api/v1/cache/flush'),
  getCacheKeys: (pattern = '*') => api.get(`/api/v1/cache/keys/${pattern}`),
};

export default api;
