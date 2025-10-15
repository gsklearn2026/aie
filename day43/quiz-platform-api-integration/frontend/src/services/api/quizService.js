/**
 * Quiz service with API integration
 */
import { apiClient } from './client'

export class QuizService {
  // Generate quiz questions
  static async generateQuiz(topic, difficulty = 'medium', count = 5) {
    try {
      const response = await apiClient.post('/quiz/generate', null, {
        params: { topic, difficulty, count }
      })
      
      if (response.data.success) {
        return response.data.data
      } else {
        throw new Error(response.data.error || 'Failed to generate quiz')
      }
    } catch (error) {
      console.error('Quiz generation error:', error)
      throw error
    }
  }
  
  // Submit quiz response
  static async submitResponse(questionId, selectedAnswer, userId) {
    try {
      const response = await apiClient.post('/quiz/submit', {
        question_id: questionId,
        selected_answer: selectedAnswer,
        user_id: userId,
        timestamp: new Date().toISOString()
      })
      
      if (response.data.success) {
        return response.data.data
      } else {
        throw new Error(response.data.error || 'Failed to submit response')
      }
    } catch (error) {
      console.error('Response submission error:', error)
      throw error
    }
  }
  
  // Get integration health
  static async getHealthStatus() {
    try {
      const response = await apiClient.get('/integration/health')
      return response.data
    } catch (error) {
      console.error('Health check error:', error)
      throw error
    }
  }
  
  // Get metrics
  static async getMetrics() {
    try {
      const response = await apiClient.get('/integration/metrics')
      return response.data
    } catch (error) {
      console.error('Metrics error:', error)
      throw error
    }
  }
  
  // Clear cache
  static async clearCache() {
    try {
      const response = await apiClient.post('/integration/cache/clear')
      return response.data
    } catch (error) {
      console.error('Cache clear error:', error)
      throw error
    }
  }
}
