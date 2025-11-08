import React, { useState } from 'react';
import './QuizPanel.css';

function getBackendBaseUrl() {
  const explicit = process.env.REACT_APP_BACKEND_BASE_URL;
  if (explicit) {
    return explicit.replace(/\/$/, '');
  }

  const protocol =
    process.env.REACT_APP_BACKEND_PROTOCOL ||
    (typeof window !== 'undefined' && window.location?.protocol === 'https:' ? 'https' : 'http');
  const host =
    process.env.REACT_APP_BACKEND_HOST ||
    (typeof window !== 'undefined' ? window.location?.hostname : 'localhost') ||
    'localhost';
  const port = process.env.REACT_APP_BACKEND_PORT ?? '8000';

  return `${protocol}://${host}${port ? `:${port}` : ''}`;
}

function QuizPanel() {
  const [topic, setTopic] = useState('Python Programming');
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [cached, setCached] = useState(false);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const generateQuiz = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${getBackendBaseUrl()}/api/quiz/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, num_questions: 5 })
      });
      const data = await response.json();
      const incomingQuestions = Array.isArray(data?.questions) ? data.questions : [];
      setQuestions(incomingQuestions);
      setCached(Boolean(data?.cached));
      setSelectedAnswers({});
      setShowResults(false);
      setSubmitted(false);
    } catch (error) {
      window.alert('Failed to generate quiz');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectOption = (questionIndex, optionIndex) => {
    if (showResults) return;
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionIndex]: optionIndex
    }));
  };

  const handleSubmit = () => {
    if (questions.length === 0) return;
    setShowResults(true);
    setSubmitted(true);
  };

  const allAnswered =
    questions.length > 0 &&
    questions.every((_, idx) => Number.isInteger(selectedAnswers[idx]));

  return (
    <div className="quiz-panel">
      <div className="quiz-generator">
        <h2>Generate Quiz</h2>
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter topic..."
        />
        <button onClick={generateQuiz} disabled={loading}>
          {loading ? 'Generating...' : '✨ Generate Quiz'}
        </button>
        {cached && <div className="cache-indicator">⚡ Loaded from cache</div>}
      </div>

      <div className="questions-list">
        {questions.map((q, idx) => (
          <div key={idx} className="question-card">
            <h3>Question {idx + 1}</h3>
            <p>{q.question}</p>
            <div className="options">
              {(Array.isArray(q.options) ? q.options : []).map((opt, i) => (
                <button
                  key={i}
                  type="button"
                  className={[
                    'option',
                    selectedAnswers[idx] === i ? 'selected' : '',
                    showResults && i === q.correct ? 'correct' : '',
                    showResults &&
                    selectedAnswers[idx] === i &&
                    i !== q.correct
                      ? 'incorrect'
                      : ''
                  ]
                    .filter(Boolean)
                    .join(' ')}
                  onClick={() => handleSelectOption(idx, i)}
                  disabled={showResults}
                >
                  {opt}
                </button>
              ))}
            </div>
            {showResults && (
              <div className="explanation">
                <strong>Your answer:</strong>{' '}
                {Number.isInteger(selectedAnswers[idx])
                  ? q.options[selectedAnswers[idx]]
                  : 'Not answered'}
                <br />
                <strong>Correct answer:</strong> {q.options[q.correct]}
                <br />
                <span>{q.explanation}</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {questions.length > 0 && (
        <div className="quiz-actions">
          <button
            className="submit-btn"
            onClick={handleSubmit}
            disabled={!allAnswered || submitted}
          >
            {submitted ? 'Submitted' : 'Submit Answers'}
          </button>
          {showResults && (
            <div className="score-summary">
              {(() => {
                const correctCount = questions.reduce(
                  (acc, q, index) =>
                    acc + (selectedAnswers[index] === q.correct ? 1 : 0),
                  0
                );
                return (
                  <span>
                    You scored {correctCount} / {questions.length}
                  </span>
                );
              })()}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default QuizPanel;
