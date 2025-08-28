import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export const jobsAPI = {
  // Create quiz generation job
  createQuizJob: async (data) => {
    const response = await api.post('/jobs/generate-quiz', data);
    return response.data;
  },

  // Create batch quiz job
  createBatchJob: async (data) => {
    const response = await api.post('/jobs/batch-quiz', data);
    return response.data;
  },

  // Get job status
  getJobStatus: async (jobId) => {
    const response = await api.get(`/jobs/${jobId}`);
    return response.data;
  },

  // List recent jobs
  listJobs: async (limit = 20) => {
    const response = await api.get(`/jobs?limit=${limit}`);
    return response.data;
  },

  // Get job statistics
  getJobStats: async () => {
    const response = await api.get('/jobs/stats/summary');
    return response.data;
  }
};

export default api;
