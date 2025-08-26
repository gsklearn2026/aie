import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include user ID
api.interceptors.request.use((config) => {
  const userId = localStorage.getItem('userId') || 'user123';
  config.headers['X-User-ID'] = userId;
  return config;
});

// Add response interceptor to handle rate limiting
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after'];
      throw new Error(`Rate limit exceeded. Try again in ${retryAfter} seconds.`);
    }
    throw error;
  }
);

export const generateQuiz = async (topic, difficulty, numQuestions) => {
  const response = await api.post('/quiz/generate', {
    topic,
    difficulty,
    num_questions: numQuestions,
  });
  return response.data;
};

export const submitQuiz = async (quizId, answers) => {
  const response = await api.post('/quiz/submit', {
    quiz_id: quizId,
    answers,
  });
  return response.data;
};

export const listQuizzes = async () => {
  const response = await api.get('/quiz/list');
  return response.data;
};

export const getRateLimitStatus = async (userId) => {
  const response = await api.get('/rate-limit/status', {
    headers: { 'X-User-ID': userId }
  });
  return response.data;
};

export const upgradeTier = async (userId, tier) => {
  const response = await api.post('/rate-limit/upgrade-tier', {
    user_id: userId,
    tier,
  });
  return response.data;
};

export default api;
