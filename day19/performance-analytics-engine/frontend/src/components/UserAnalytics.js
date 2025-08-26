import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { analyticsService } from '../services/analyticsService';

const UserAnalytics = () => {
  const { userId } = useParams();
  const [performanceData, setPerformanceData] = useState(null);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUserData();
  }, [userId]);

  const loadUserData = async () => {
    try {
      setLoading(true);
      const [performance, userInsights] = await Promise.all([
        analyticsService.getUserPerformance(userId),
        analyticsService.getUserInsights(userId)
      ]);
      setPerformanceData(performance);
      setInsights(userInsights);
    } catch (error) {
      console.error('Error loading user data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateDemoData = async () => {
    const topics = ['mathematics', 'science', 'history', 'literature', 'programming'];
    
    for (let i = 0; i < 10; i++) {
      const topic = topics[Math.floor(Math.random() * topics.length)];
      const score = Math.floor(Math.random() * 40) + 60; // 60-100
      const maxScore = 100;
      
      await analyticsService.simulateQuizCompletion(
        userId,
        `quiz-${i}`,
        topic,
        score,
        maxScore
      );
    }
    
    // Reload data after generating
    setTimeout(() => loadUserData(), 2000);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading user analytics...</p>
      </div>
    );
  }

  if (!performanceData || performanceData.summary.total_attempts === 0) {
    return (
      <div className="no-data-container">
        <h2>User Analytics - {userId}</h2>
        <p>No performance data available for this user.</p>
        <button onClick={generateDemoData} className="demo-button">
          Generate Demo Data
        </button>
      </div>
    );
  }

  // Prepare radar chart data
  const radarData = Object.entries(performanceData.topic_performance).map(([topic, data]) => ({
    topic: topic.charAt(0).toUpperCase() + topic.slice(1),
    score: data.average_percentage
  }));

  return (
    <div className="user-analytics">
      <h1>User Analytics - {userId}</h1>
      
      <div className="user-summary">
        <div className="summary-card">
          <h3>Performance Summary</h3>
          <div className="summary-stats">
            <div className="stat">
              <span className="stat-value">{performanceData.summary.total_attempts}</span>
              <span className="stat-label">Total Attempts</span>
            </div>
            <div className="stat">
              <span className="stat-value">{performanceData.summary.average_score_percentage.toFixed(1)}%</span>
              <span className="stat-label">Average Score</span>
            </div>
            <div className="stat">
              <span className="stat-value">{performanceData.summary.topics_attempted}</span>
              <span className="stat-label">Topics Attempted</span>
            </div>
          </div>
        </div>
      </div>

      <div className="charts-section">
        <div className="chart-container">
          <h3>Topic Performance Radar</h3>
          <RadarChart width={400} height={300} data={radarData}>
            <PolarGrid />
            <PolarAngleAxis dataKey="topic" />
            <PolarRadiusAxis angle={90} domain={[0, 100]} />
            <Radar name="Score %" dataKey="score" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
            <Tooltip />
          </RadarChart>
        </div>

        <div className="topic-breakdown">
          <h3>Topic Breakdown</h3>
          {Object.entries(performanceData.topic_performance).map(([topic, data]) => (
            <div key={topic} className="topic-item">
              <div className="topic-header">
                <span className="topic-name">{topic.charAt(0).toUpperCase() + topic.slice(1)}</span>
                <span className="topic-score">{data.average_percentage.toFixed(1)}%</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${data.average_percentage}%` }}
                ></div>
              </div>
              <div className="topic-details">
                {data.attempts} attempts • Avg time: {(data.avg_time_per_attempt / 60).toFixed(1)} min
              </div>
            </div>
          ))}
        </div>
      </div>

      {insights && insights.fresh_insights && insights.fresh_insights.length > 0 && (
        <div className="insights-section">
          <h3>AI-Generated Insights</h3>
          <div className="insights-grid">
            {insights.fresh_insights.map((insight, index) => (
              <div key={index} className={`insight-card ${insight.type}`}>
                <h4>{insight.title}</h4>
                <p>{insight.description}</p>
                <div className="confidence-score">
                  Confidence: {(insight.confidence * 100).toFixed(0)}%
                </div>
                {insight.action_items && insight.action_items.length > 0 && (
                  <div className="action-items">
                    <strong>Recommended Actions:</strong>
                    <ul>
                      {insight.action_items.map((action, actionIndex) => (
                        <li key={actionIndex}>{action}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="actions-section">
        <button onClick={generateDemoData} className="demo-button">
          Generate More Demo Data
        </button>
        <button onClick={loadUserData} className="refresh-button">
          Refresh Analytics
        </button>
      </div>
    </div>
  );
};

export default UserAnalytics;
