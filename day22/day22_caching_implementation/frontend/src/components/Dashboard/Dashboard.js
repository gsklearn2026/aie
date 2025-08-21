import React, { useState, useEffect } from 'react';
import { quizAPI } from '../../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const [quizData, setQuizData] = useState(null);
  const [progress, setProgress] = useState(null);
  const [leaderboard, setLeaderboard] = useState(null);
  const [loading, setLoading] = useState(false);
  const [requestTimes, setRequestTimes] = useState([]);

  const DEMO_QUIZ_ID = "javascript-basics";
  const DEMO_USER_ID = "demo-user";

  const measureRequestTime = async (requestFunc) => {
    const startTime = performance.now();
    const result = await requestFunc();
    const endTime = performance.now();
    const responseTime = Math.round(endTime - startTime);
    
    setRequestTimes(prev => [...prev.slice(-9), responseTime]); // Keep last 10 times
    return result;
  };

  const loadQuizData = async () => {
    setLoading(true);
    try {
      const [quizResponse, progressResponse, leaderboardResponse] = await Promise.all([
        measureRequestTime(() => quizAPI.getQuiz(DEMO_QUIZ_ID)),
        measureRequestTime(() => quizAPI.getUserProgress(DEMO_QUIZ_ID, DEMO_USER_ID)),
        measureRequestTime(() => quizAPI.getLeaderboard(DEMO_QUIZ_ID))
      ]);

      setQuizData(quizResponse.data);
      setProgress(progressResponse.data);
      setLeaderboard(leaderboardResponse.data);
    } catch (error) {
      console.error('Error loading quiz data:', error);
    } finally {
      setLoading(false);
    }
  };

  const invalidateCache = async () => {
    try {
      await quizAPI.invalidateQuizCache(DEMO_QUIZ_ID);
      alert('Cache invalidated! Try loading data again to see cache miss.');
    } catch (error) {
      console.error('Error invalidating cache:', error);
    }
  };

  const getAIExplanation = async () => {
    try {
      const response = await measureRequestTime(() => 
        quizAPI.getAIExplanation(DEMO_QUIZ_ID, "caching")
      );
      alert(`AI Explanation: ${response.data.explanation}`);
    } catch (error) {
      console.error('Error getting AI explanation:', error);
    }
  };

  useEffect(() => {
    loadQuizData();
  }, []);

  const averageResponseTime = requestTimes.length > 0 
    ? Math.round(requestTimes.reduce((a, b) => a + b, 0) / requestTimes.length)
    : 0;

  return (
    <div className="dashboard">
      <div className="performance-metrics">
        <div className="metric-card">
          <h3>Response Time</h3>
          <div className="metric-value">{averageResponseTime}ms</div>
          <div className="metric-detail">Average of last {requestTimes.length} requests</div>
        </div>
        
        <div className="metric-card">
          <h3>Cache Benefits</h3>
          <div className="metric-value">
            {averageResponseTime < 100 ? '🟢 Fast' : averageResponseTime < 300 ? '🟡 Moderate' : '🔴 Slow'}
          </div>
          <div className="metric-detail">
            {averageResponseTime < 100 ? 'Cache hits working!' : 'Possible cache misses'}
          </div>
        </div>
      </div>

      <div className="action-buttons">
        <button onClick={loadQuizData} disabled={loading}>
          {loading ? 'Loading...' : '🔄 Load Quiz Data'}
        </button>
        <button onClick={invalidateCache} className="danger">
          🗑️ Clear Cache
        </button>
        <button onClick={getAIExplanation}>
          🤖 Get AI Explanation
        </button>
      </div>

      <div className="data-display">
        {quizData && (
          <div className="data-card">
            <h3>📝 Quiz Data</h3>
            <p><strong>Title:</strong> {quizData.title}</p>
            <p><strong>Questions:</strong> {quizData.questions?.length || 0}</p>
            <p><strong>Cached:</strong> Response time indicates cache usage</p>
          </div>
        )}

        {progress && (
          <div className="data-card">
            <h3>📊 User Progress</h3>
            <p><strong>Score:</strong> {progress.score}%</p>
            <p><strong>Completed:</strong> {progress.completed ? 'Yes' : 'No'}</p>
            <p><strong>Time Spent:</strong> {progress.time_spent}s</p>
          </div>
        )}

        {leaderboard && (
          <div className="data-card">
            <h3>🏆 Leaderboard</h3>
            {leaderboard.leaderboard?.map((entry, index) => (
              <div key={index} className="leaderboard-entry">
                {index + 1}. {entry.user_id}: {entry.score}% ({entry.time}s)
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="response-times">
        <h3>📈 Response Time History</h3>
        <div className="time-bars">
          {requestTimes.map((time, index) => (
            <div 
              key={index} 
              className="time-bar" 
              style={{height: `${Math.min(time / 5, 50)}px`}}
              title={`${time}ms`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
