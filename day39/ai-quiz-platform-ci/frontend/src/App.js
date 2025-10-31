import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [healthStatus, setHealthStatus] = useState('checking...');
  const [quizTopic, setQuizTopic] = useState('');
  const [difficulty, setDifficulty] = useState('medium');
  const [questionCount, setQuestionCount] = useState(3);
  const [loading, setLoading] = useState(false);
  const [quizData, setQuizData] = useState(null);

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const response = await axios.get(`${API_URL}/health`);
      setHealthStatus('healthy');
    } catch (error) {
      setHealthStatus('unhealthy');
    }
  };

  const generateQuiz = async () => {
    if (!quizTopic.trim()) return;
    
    setLoading(true);
    setQuizData(null); // Clear previous results
    try {
      const response = await axios.post(`${API_URL}/quiz/generate`, null, {
        params: {
          topic: quizTopic,
          difficulty: difficulty,
          questions_count: questionCount
        },
        timeout: 30000 // 30 second timeout
      });
      setQuizData(response.data);
    } catch (error) {
      console.error('Quiz generation failed:', error);
      let errorMessage = 'Failed to generate quiz';
      
      if (error.code === 'ECONNABORTED') {
        errorMessage = 'Request timed out. Try with fewer questions or easier difficulty.';
      } else if (error.response?.status === 503) {
        errorMessage = 'AI service not configured. Please check the API key.';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }
      
      setQuizData({ error: errorMessage });
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🧠 AI Quiz Platform</h1>
        <div className="status">
          API Status: <span className={`status-${healthStatus}`}>
            {healthStatus}
          </span>
        </div>
      </header>
      
      <main className="App-main">
        <div className="quiz-generator">
          <h2>Generate a Quiz</h2>
          <div className="form-group">
            <input
              type="text"
              placeholder="Enter quiz topic (e.g., Python, History)"
              value={quizTopic}
              onChange={(e) => setQuizTopic(e.target.value)}
              className="topic-input"
            />
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              className="difficulty-select"
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
            <select
              value={questionCount}
              onChange={(e) => setQuestionCount(parseInt(e.target.value))}
              className="difficulty-select"
            >
              <option value={2}>2 Questions</option>
              <option value={3}>3 Questions</option>
              <option value={5}>5 Questions</option>
              <option value={10}>10 Questions</option>
            </select>
            <button 
              onClick={generateQuiz}
              disabled={loading || !quizTopic.trim()}
              className="generate-btn"
            >
              {loading ? 'Generating...' : 'Generate Quiz'}
            </button>
          </div>
        </div>
        
        {quizData && (
          <div className="quiz-result">
            <h3>Quiz Generated!</h3>
            {quizData.error ? (
              <p className="error">{quizData.error}</p>
            ) : (
              <div className="quiz-info">
                <p><strong>Topic:</strong> {quizData.topic}</p>
                <p><strong>Difficulty:</strong> {quizData.difficulty}</p>
                <p><strong>Questions:</strong> {questionCount}</p>
                <p><strong>Status:</strong> {quizData.status}</p>
                {quizData.questions && (
                  <div style={{ marginTop: '20px', textAlign: 'left' }}>
                    <h4>Generated Questions:</h4>
                    <pre style={{ 
                      background: '#f8f9fa', 
                      padding: '15px', 
                      borderRadius: '8px', 
                      overflow: 'auto',
                      fontSize: '14px',
                      whiteSpace: 'pre-wrap'
                    }}>
                      {quizData.questions}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
