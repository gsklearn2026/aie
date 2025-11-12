import React, { useState } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

function QuizGenerator({ onQuizGenerated }) {
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('medium');
  const [loading, setLoading] = useState(false);
  const [quiz, setQuiz] = useState(null);
  const [selectedOptions, setSelectedOptions] = useState([]);
  const [submitted, setSubmitted] = useState(false);
  const [score, setScore] = useState(0);
  const [error, setError] = useState(null);

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setQuiz(null);
    setSelectedOptions([]);
    setSubmitted(false);
    setScore(0);

    try {
      const response = await axios.post(`${API_URL}/api/quiz/generate`, {
        topic,
        difficulty
      });

      const generatedQuiz = response.data.quiz;
      setQuiz(generatedQuiz);
      setSelectedOptions(new Array(generatedQuiz.questions.length).fill(null));
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate quiz');
    } finally {
      setLoading(false);
    }
  };

  const handleOptionChange = (questionIndex, option) => {
    const updatedSelections = [...selectedOptions];
    updatedSelections[questionIndex] = option;
    setSelectedOptions(updatedSelections);
  };

  const handleSubmit = () => {
    if (!quiz) return;
    let correctCount = 0;
    quiz.questions.forEach((question, index) => {
      if (selectedOptions[index] === question.correct_answer) {
        correctCount += 1;
      }
    });
    setScore(correctCount);
    setSubmitted(true);
    if (onQuizGenerated) onQuizGenerated();
  };

  const allAnswered = quiz && selectedOptions.every((option) => option !== null);

  return (
    <div className="quiz-generator">
      <h2>🎓 Generate New Quiz</h2>
      <form onSubmit={handleGenerate}>
        <div className="form-group">
          <label>Topic:</label>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g., Python Programming, World History"
            required
          />
        </div>

        <div className="form-group">
          <label>Difficulty:</label>
          <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
        </div>

        <button type="submit" className="generate-btn" disabled={loading}>
          {loading ? '⏳ Generating...' : '🚀 Generate Quiz'}
        </button>
      </form>

      {loading && <div className="loading">Generating quiz using connection pools...</div>}

      {error && <div className="error-message">❌ {error}</div>}

      {quiz && (
        <div className="quiz-result">
          <h3>✅ Quiz Ready! Answer all questions:</h3>
          <div className="quiz-questions">
            {quiz.questions.map((question, index) => (
              <div key={index} className={`quiz-question-card${submitted && selectedOptions[index] === question.correct_answer ? ' correct' : submitted ? ' incorrect' : ''}`}>
                <h4>Question {index + 1}</h4>
                <p>{question.question}</p>
                <ul className="options-list selectable">
                  {question.options.map((option, optionIdx) => {
                    const optionId = `question-${index}-option-${optionIdx}`;
                    const isSelected = selectedOptions[index] === option;
                    const isCorrect = question.correct_answer === option;
                    return (
                      <li key={optionIdx} className={submitted ? (isCorrect ? 'correct-option' : isSelected ? 'incorrect-option' : '') : ''}>
                        <label htmlFor={optionId}>
                          <input
                            type="radio"
                            id={optionId}
                            name={`question-${index}`}
                            value={option}
                            checked={isSelected}
                            disabled={submitted}
                            onChange={() => handleOptionChange(index, option)}
                          />
                          {option}
                        </label>
                      </li>
                    );
                  })}
                </ul>
                {submitted && (
                  <div className="correct-answer">
                    ✓ Correct Answer: {question.correct_answer}
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="quiz-actions">
            <button
              type="button"
              className="submit-btn"
              onClick={handleSubmit}
              disabled={!allAnswered || submitted}
            >
              {submitted ? 'Quiz Submitted' : 'Submit Answers'}
            </button>
            {submitted && (
              <div className="quiz-score">
                You answered {score} out of {quiz.questions.length} correctly.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default QuizGenerator;
