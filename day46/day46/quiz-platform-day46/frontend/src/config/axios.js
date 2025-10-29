import axios from 'axios';

// Determine the correct API base URL
// Always use the backend directly since we're in Docker
const getBaseURL = () => {
  // If running in Docker or with explicit config, use backend URL
  // In browser, localhost:8000 is the backend (mapped from Docker)
  return 'http://localhost:8000';
};

// Create axios instance with base URL
const api = axios.create({
  baseURL: getBaseURL(),
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method.toUpperCase()} request to: ${config.url} (baseURL: ${config.baseURL})`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.message);
    if (error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
    }
    return Promise.reject(error);
  }
);

export default api;

