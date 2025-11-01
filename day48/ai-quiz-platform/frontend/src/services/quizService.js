import axios from 'axios';

class QuizService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 120000, // 120 second timeout (2 minutes) - Gemini API can be slow with retries
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Request interceptor for logging
    this.client.interceptors.request.use(
      (config) => {
        console.log(`Making request to ${config.url}`);
        return config;
      },
      (error) => {
        console.error('Request error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        return this.handleError(error);
      }
    );
  }

  handleError(error) {
    console.error('API Error:', error);

    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      const err = new Error('Request timed out. The AI service may be taking longer than usual. Please try again.');
      err.error_code = 'TIMEOUT';
      err.type = 'network';
      throw err;
    }

    if (!error.response) {
      const err = new Error('Unable to connect to server. Please check your internet connection.');
      err.error_code = 'NETWORK_ERROR';
      err.type = 'network';
      throw err;
    }

    const { status, data } = error.response;

    switch (status) {
      case 400:
        const validationErr = new Error(data?.message || data?.detail || 'Invalid request data');
        validationErr.error_code = 'VALIDATION_ERROR';
        validationErr.type = 'validation';
        throw validationErr;
      
      case 429:
        const rateLimitErr = new Error('Too many requests. Please wait a moment before trying again.');
        rateLimitErr.error_code = 'RATE_LIMIT';
        rateLimitErr.type = 'rate_limit';
        throw rateLimitErr;
      
      case 500:
        const serverErr = new Error(data?.message || data?.detail || 'Server error occurred. Please try again later.');
        serverErr.error_code = 'SERVER_ERROR';
        serverErr.type = 'server';
        throw serverErr;
      
      case 502:
        const aiServiceErr = new Error(data?.message || data?.detail || 'AI service temporarily unavailable. Please try again.');
        aiServiceErr.error_code = 'AI_SERVICE_ERROR';
        aiServiceErr.type = 'ai_service';
        throw aiServiceErr;
      
      default:
        const httpErr = new Error(data?.message || data?.detail || 'An unexpected error occurred');
        httpErr.error_code = `HTTP_${status}`;
        httpErr.type = 'http';
        throw httpErr;
    }
  }

  async generateQuiz(params) {
    try {
      const response = await this.client.post('/api/generate-quiz', params);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async submitAnswer(answerData) {
    try {
      const response = await this.client.post('/api/submit-answer', answerData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getAnalytics(quizId) {
    try {
      const response = await this.client.get(`/api/analytics/${quizId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async healthCheck() {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      throw error;
    }
  }
}

export const quizService = new QuizService();
