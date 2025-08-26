import axios from 'axios';
import ErrorHandler from './errorHandler';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    this.setupInterceptors();
  }
  
  setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add correlation ID for tracking
        config.headers['x-correlation-id'] = this.generateCorrelationId();
        return config;
      },
      (error) => Promise.reject(error)
    );
    
    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        ErrorHandler.handleError(error);
        return Promise.reject(error);
      }
    );
  }
  
  generateCorrelationId() {
    return 'req_' + Math.random().toString(36).substr(2, 9);
  }
  
  async generateQuiz(topic, difficulty = 'medium', count = 5) {
    return ErrorHandler.withRetry(async () => {
      const response = await this.client.post(`/api/quiz/generate?topic=${encodeURIComponent(topic)}&difficulty=${encodeURIComponent(difficulty)}&count=${count}`);
      return response.data;
    });
  }
  
  async submitQuiz(quizId, answers) {
    return ErrorHandler.withRetry(async () => {
      const response = await this.client.post('/api/quiz/submit', {
        quiz_id: quizId,
        answers
      });
      return response.data;
    });
  }
  
  async getHealthStatus() {
    const response = await this.client.get('/api/quiz/health');
    return response.data;
  }
}

export default new ApiService();
