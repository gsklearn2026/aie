import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './QuizList.css';

const API_URL = 'http://localhost:8000';

function QuizList() {
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadTime, setLoadTime] = useState(0);

  const fetchQuizzes = async () => {
    setLoading(true);
    const startTime = performance.now();
    
    try {
      const response = await axios.get(`${API_URL}/api/quizzes/`);
      const endTime = performance.now();
      
      setQuizzes(response.data);
      setLoadTime(endTime - startTime);
    } catch (error) {
      console.error('Error fetching quizzes:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuizzes();
  }, []);

  return (
    <div className="quiz-list-container">
      <div className="quiz-list-header">
        <h2>Available Quizzes</h2>
        <div className="load-time">
          Load Time: <strong>{loadTime.toFixed(2)}ms</strong>
          <span className={loadTime < 100 ? 'badge-success' : 'badge-warning'}>
            {loadTime < 100 ? '✓ Optimized' : '⚠ Needs Optimization'}
          </span>
        </div>
      </div>

      {loading ? (
        <div className="loading">Loading quizzes...</div>
      ) : (
        <div className="quiz-grid">
          {quizzes.map(quiz => (
            <div key={quiz.id} className="quiz-card">
              <div className="quiz-category">{quiz.category}</div>
              <h3>{quiz.title}</h3>
              <p>{quiz.description}</p>
              <div className="quiz-meta">
                <span className="difficulty">{quiz.difficulty}</span>
                <span className="question-count">{quiz.question_count} questions</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default QuizList;
