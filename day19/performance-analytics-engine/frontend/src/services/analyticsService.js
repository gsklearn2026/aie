import axios from 'axios';

const API_BASE_URL = '/api/v1/analytics';

class AnalyticsService {
  async createEvent(eventData) {
    try {
      const response = await axios.post(`${API_BASE_URL}/events`, eventData);
      return response.data;
    } catch (error) {
      console.error('Error creating analytics event:', error);
      throw error;
    }
  }

  async getUserPerformance(userId, days = 30) {
    try {
      const response = await axios.get(`${API_BASE_URL}/user/${userId}/performance`, {
        params: { days }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching user performance:', error);
      throw error;
    }
  }

  async getUserInsights(userId) {
    try {
      const response = await axios.get(`${API_BASE_URL}/user/${userId}/insights`);
      return response.data;
    } catch (error) {
      console.error('Error fetching user insights:', error);
      throw error;
    }
  }

  async getDashboardMetrics(days = 7) {
    try {
      const response = await axios.get(`${API_BASE_URL}/dashboard`, {
        params: { days }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard metrics:', error);
      throw error;
    }
  }

  async getTopicAnalytics(topicId, days = 30) {
    try {
      const response = await axios.get(`${API_BASE_URL}/topics/${topicId}/analytics`, {
        params: { days }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching topic analytics:', error);
      throw error;
    }
  }

  // Simulate quiz completion for demo
  async simulateQuizCompletion(userId, quizId, topicId, score, maxScore) {
    const eventData = {
      event_type: 'quiz_completed',
      user_id: userId,
      quiz_id: quizId,
      topic_id: topicId,
      data: {
        score: score,
        max_score: maxScore,
        time_spent: Math.floor(Math.random() * 600) + 60, // 1-10 minutes
        timestamp: new Date().toISOString()
      }
    };
    
    return await this.createEvent(eventData);
  }
}

export const analyticsService = new AnalyticsService();
