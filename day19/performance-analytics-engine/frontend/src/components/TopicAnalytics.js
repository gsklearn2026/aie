import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { analyticsService } from '../services/analyticsService';

const TopicAnalytics = () => {
  const { topicId } = useParams();
  const [topicData, setTopicData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTopicData();
  }, [topicId]);

  const loadTopicData = async () => {
    try {
      setLoading(true);
      const data = await analyticsService.getTopicAnalytics(topicId);
      setTopicData(data);
    } catch (error) {
      console.error('Error loading topic data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading topic analytics...</p>
      </div>
    );
  }

  if (!topicData) {
    return <div className="error-message">Failed to load topic data</div>;
  }

  return (
    <div className="topic-analytics">
      <h1>Topic Analytics - {topicId.charAt(0).toUpperCase() + topicId.slice(1)}</h1>
      
      <div className="topic-summary">
        <div className="summary-cards">
          <div className="summary-card">
            <h3>Total Attempts</h3>
            <div className="metric-value">{topicData.statistics.total_attempts}</div>
          </div>
          <div className="summary-card">
            <h3>Average Score</h3>
            <div className="metric-value">{topicData.statistics.average_score_percentage.toFixed(1)}%</div>
          </div>
          <div className="summary-card">
            <h3>Average Time</h3>
            <div className="metric-value">{topicData.statistics.average_time_minutes.toFixed(1)} min</div>
          </div>
          <div className="summary-card">
            <h3>Unique Learners</h3>
            <div className="metric-value">{topicData.statistics.unique_learners}</div>
          </div>
        </div>
      </div>

      <div className="chart-section">
        <h3>Score Distribution</h3>
        <BarChart width={600} height={300} data={topicData.score_distribution}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="score_range" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="count" fill="#8884d8" />
        </BarChart>
      </div>

      <div className="topic-insights">
        <h3>Topic Insights</h3>
        <div className="insights-grid">
          {topicData.statistics.average_score_percentage < 60 && (
            <div className="insight-card warning">
              <h4>⚠️ Low Performance Alert</h4>
              <p>This topic has a below-average performance rate of {topicData.statistics.average_score_percentage.toFixed(1)}%</p>
              <p>Consider reviewing content difficulty or providing additional learning resources.</p>
            </div>
          )}
          
          {topicData.statistics.average_time_minutes > 10 && (
            <div className="insight-card info">
              <h4>⏱️ High Time Investment</h4>
              <p>Learners spend an average of {topicData.statistics.average_time_minutes.toFixed(1)} minutes on this topic</p>
              <p>This indicates either high engagement or content complexity.</p>
            </div>
          )}
          
          {topicData.statistics.total_attempts > 100 && (
            <div className="insight-card success">
              <h4>🔥 Popular Topic</h4>
              <p>This topic has {topicData.statistics.total_attempts} attempts from {topicData.statistics.unique_learners} learners</p>
              <p>High engagement suggests strong learner interest.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TopicAnalytics;
