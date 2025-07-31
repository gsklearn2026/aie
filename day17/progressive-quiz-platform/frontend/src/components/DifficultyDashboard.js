import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { TrendingUp, TrendingDown, Brain, Clock, Target, Activity, Eye, EyeOff } from 'lucide-react';
import './DifficultyDashboard.css';

const DifficultyDashboard = ({ userId, sessionId }) => {
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [userAnswer, setUserAnswer] = useState('');
  const [isAnswering, setIsAnswering] = useState(false);
  const [startTime, setStartTime] = useState(null);
  const [performanceHistory, setPerformanceHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAnswer, setShowAnswer] = useState(false);
  const [correctAnswer, setCorrectAnswer] = useState(null);

  useEffect(() => {
    fetchNextQuestion();
  }, []);

  const fetchNextQuestion = async (lastResponse = null) => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/difficulty/next-question`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          session_id: sessionId,
          last_response: lastResponse
        })
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to fetch question');
      }
      
      setCurrentQuestion(data.question);
      setAnalytics(data.performance_analytics || {});
      setUserAnswer('');
      setIsAnswering(false);
      setStartTime(Date.now());
      setShowAnswer(false);
      setCorrectAnswer(null);
      
      // Update performance history for visualization
      if (data.performance_analytics && data.performance_analytics.recent_performance) {
        const history = data.performance_analytics.recent_performance.map((correct, index) => ({
          question: index + 1,
          success: correct ? 1 : 0,
          difficulty: data.target_difficulty
        }));
        setPerformanceHistory(history);
      } else {
        setPerformanceHistory([]);
      }
    } catch (error) {
      console.error('Error fetching next question:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnswer = async (questionId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/difficulty/question/${questionId}/answer`);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to fetch answer');
      }
      
      setCorrectAnswer(data.correct_answer);
      setShowAnswer(true);
    } catch (error) {
      console.error('Error fetching answer:', error);
    }
  };

  const submitAnswer = async () => {
    if (!currentQuestion || !userAnswer.trim()) return;

    setIsAnswering(true);
    const responseTime = Date.now() - startTime;
    
    // Get the correct answer to check if user is correct
    let isCorrect = false;
    if (correctAnswer) {
      isCorrect = userAnswer.toLowerCase().trim() === correctAnswer.toLowerCase().trim();
    } else {
      // Fallback: fetch answer to check correctness
      try {
        const answerResponse = await fetch(`http://localhost:8000/api/difficulty/question/${currentQuestion.id}/answer`);
        const answerData = await answerResponse.json();
        isCorrect = userAnswer.toLowerCase().trim() === answerData.correct_answer.toLowerCase().trim();
        setCorrectAnswer(answerData.correct_answer);
        setShowAnswer(true);
      } catch (error) {
        console.error('Error checking answer:', error);
        isCorrect = false;
      }
    }

    try {
      // Submit response
      await fetch(`http://localhost:8000/api/difficulty/submit-response`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          session_id: sessionId,
          question_id: currentQuestion.id,
          user_answer: userAnswer,
          is_correct: isCorrect,
          response_time_ms: responseTime
        })
      });

      // Fetch next question with last response data
      setTimeout(() => {
        fetchNextQuestion({
          question_id: currentQuestion.id,
          user_answer: userAnswer,
          is_correct: isCorrect,
          response_time_ms: responseTime,
          difficulty_at_time: currentQuestion.difficulty_score
        });
      }, 1500);

    } catch (error) {
      console.error('Error submitting answer:', error);
      setIsAnswering(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading progressive difficulty engine...</p>
      </div>
    );
  }

  return (
    <div className="difficulty-dashboard">
      <header className="dashboard-header">
        <h1><Brain size={28} /> Progressive Quiz Platform</h1>
        <div className="session-info">
          <span>Session: {sessionId.slice(0, 8)}</span>
          <span>User: {userId}</span>
        </div>
      </header>

      <div className="dashboard-grid">
        {/* Performance Analytics */}
        <div className="analytics-panel">
          <h3><Activity size={20} /> Performance Analytics</h3>
          {analytics && (
            <div className="analytics-grid">
              <div className="metric-card">
                <div className="metric-icon">
                  <Target size={24} />
                </div>
                <div className="metric-content">
                  <span className="metric-label">Current Difficulty</span>
                  <span className="metric-value">{analytics.current_difficulty.toFixed(2)}</span>
                </div>
              </div>
              
              <div className="metric-card">
                <div className="metric-icon">
                  {analytics.momentum >= 0 ? <TrendingUp size={24} /> : <TrendingDown size={24} />}
                </div>
                <div className="metric-content">
                  <span className="metric-label">Success Rate</span>
                  <span className="metric-value">{(analytics.success_rate * 100).toFixed(1)}%</span>
                </div>
              </div>
              
              <div className="metric-card">
                <div className="metric-icon">
                  <Clock size={24} />
                </div>
                <div className="metric-content">
                  <span className="metric-label">Avg Response Time</span>
                  <span className="metric-value">{(analytics.avg_response_time / 1000).toFixed(1)}s</span>
                </div>
              </div>
              
              <div className="metric-card momentum">
                <div className="metric-icon">
                  {analytics.momentum >= 0 ? <TrendingUp size={24} /> : <TrendingDown size={24} />}
                </div>
                <div className="metric-content">
                  <span className="metric-label">Momentum</span>
                  <span className={`metric-value ${analytics.momentum >= 0 ? 'positive' : 'negative'}`}>
                    {analytics.momentum >= 0 ? '+' : ''}{(analytics.momentum * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Performance Chart */}
        {performanceHistory.length > 0 && (
          <div className="chart-panel">
            <h3>Performance Trend</h3>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={performanceHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="question" />
                <YAxis domain={[0, 1]} />
                <Tooltip 
                  formatter={(value, name) => [
                    name === 'success' ? (value ? 'Correct' : 'Incorrect') : value.toFixed(2),
                    name === 'success' ? 'Result' : 'Difficulty'
                  ]}
                />
                <Area type="monotone" dataKey="success" stroke="#22c55e" fill="#22c55e" fillOpacity={0.3} />
                <Line type="monotone" dataKey="difficulty" stroke="#3b82f6" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Question Panel */}
        <div className="question-panel">
          <h3>Current Question</h3>
          {currentQuestion && (
            <div className="question-container">
              <div className="question-header">
                <span className="difficulty-badge">
                  Difficulty: {currentQuestion.difficulty_score.toFixed(1)}
                </span>
                <span className="category-badge">
                  {currentQuestion.category || 'General'}
                </span>
              </div>
              
              <div className="question-content">
                <p>{currentQuestion.content}</p>
              </div>
              
              {/* Answer Display */}
              {showAnswer && correctAnswer && (
                <div className="answer-display">
                  <h4>Correct Answer:</h4>
                  <p className="correct-answer">{correctAnswer}</p>
                </div>
              )}
              
              <div className="answer-section">
                <input
                  type="text"
                  value={userAnswer}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  placeholder="Enter your answer..."
                  disabled={isAnswering}
                  className="answer-input"
                  onKeyPress={(e) => e.key === 'Enter' && submitAnswer()}
                />
                <div className="button-group">
                  <button
                    onClick={() => fetchAnswer(currentQuestion.id)}
                    disabled={isAnswering || showAnswer}
                    className="view-answer-button"
                  >
                    {showAnswer ? <EyeOff size={16} /> : <Eye size={16} />}
                    {showAnswer ? 'Hide Answer' : 'View Answer'}
                  </button>
                  <button
                    onClick={submitAnswer}
                    disabled={isAnswering || !userAnswer.trim()}
                    className={`submit-button ${isAnswering ? 'submitting' : ''}`}
                  >
                    {isAnswering ? 'Submitting...' : 'Submit Answer'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DifficultyDashboard;
