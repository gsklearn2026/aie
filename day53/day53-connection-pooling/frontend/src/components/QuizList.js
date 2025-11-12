import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

function QuizList() {
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchQuizzes = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/quiz/list`);
        const normalized = response.data.quizzes.map((quiz) => ({
          ...quiz,
          questions: Array.isArray(quiz.questions) ? quiz.questions : []
        }));
        setQuizzes(normalized);
        setError(null);
      } catch (err) {
        setError('Failed to fetch quizzes');
      } finally {
        setLoading(false);
      }
    };

    fetchQuizzes();
  }, []);

  if (loading) return <div className="loading">Loading quizzes...</div>;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div className="quiz-history">
      <h2>📚 Quiz History ({quizzes.length})</h2>
      {quizzes.length === 0 ? (
        <p>No quizzes generated yet. Start by generating your first quiz!</p>
      ) : (
        quizzes.map((quiz) => (
          <div key={quiz.id} className="quiz-item">
            <h4>Topic: {quiz.topic} ({quiz.difficulty})</h4>
            <p className="quiz-question">Questions: {quiz.questions.length}</p>
            <ul>
              {quiz.questions.map((question, index) => (
                <li key={index}>
                  <strong>Q{index + 1}:</strong> {question.question}
                </li>
              ))}
            </ul>
            <div className="quiz-meta">
              <span>ID: {quiz.id}</span>
              <span>Created: {quiz.created_at ? new Date(quiz.created_at).toLocaleString() : 'N/A'}</span>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

export default QuizList;
