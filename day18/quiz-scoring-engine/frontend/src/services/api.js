import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Scoring endpoints
  calculateScore: async (submission) => {
    const response = await api.post('/scoring/calculate', submission);
    return response.data;
  },

  getUserMetrics: async (userId) => {
    const response = await api.get(`/scoring/user/${userId}/metrics`);
    return response.data;
  },

  getStrategies: async () => {
    const response = await api.get('/scoring/strategies');
    return response.data;
  },

  getSampleQuiz: async () => {
    const response = await api.post('/scoring/demo/sample-quiz');
    return response.data;
  },
};

export { apiService as api };
