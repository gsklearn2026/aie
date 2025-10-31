import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
});

// Dashboard APIs
export const fetchDashboardOverview = () => api.get('/api/dashboard/overview');
export const fetchPerformanceTrends = () => api.get('/api/dashboard/charts/performance-trends');
export const fetchScoreDistribution = () => api.get('/api/dashboard/charts/score-distribution');
export const fetchTopPerformers = () => api.get('/api/dashboard/top-performers');
export const fetchRealtimeDashboard = () => api.get('/api/analytics/dashboard/realtime');

// Analytics APIs
export const fetchUserPerformance = (userId) => api.get(`/api/analytics/user/${userId}/performance`);
export const fetchQuizAnalytics = (quizId) => api.get(`/api/analytics/quiz/${quizId}`);
export const fetchLearningProgress = (userId, days = 30) => 
  api.get(`/api/analytics/user/${userId}/progress?days=${days}`);

// Auth APIs
export const registerUser = (userData) => api.post('/api/auth/register', userData);
export const fetchUsers = () => api.get('/api/auth/users');

export default api;
