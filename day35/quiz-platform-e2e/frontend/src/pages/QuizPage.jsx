import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

function QuizPage() {
  const { type } = useParams();
  const [currentQuestion, setCurrentQuestion] = useState(1);
  const [quizComplete, setQuizComplete] = useState(false);
  const [score, setScore] = useState(0);
  const [question, setQuestion] = useState(null);

  useEffect(() => {
    // Simulate AI question generation
    generateQuestion();
  }, [currentQuestion, type]);

  const generateQuestion = () => {
    // Simulate AI-generated questions for E2E testing
    const sampleQuestions = {
      science: {
        text: "What is the chemical symbol for water?",
        options: ["H2O", "CO2", "NaCl", "O2"]
      },
      history: {
        text: "Who was the first President of the United States?",
        options: ["George Washington", "John Adams", "Thomas Jefferson", "Benjamin Franklin"]
      },
      mathematics: {
        text: "What is 15 × 12?",
        options: ["180", "160", "200", "150"]
      },
      literature: {
        text: "Who wrote 'Romeo and Juliet'?",
        options: ["William Shakespeare", "Charles Dickens", "Jane Austen", "Mark Twain"]
      }
    };

    setTimeout(() => {
      setQuestion(sampleQuestions[type] || sampleQuestions.science);
    }, 1000); // Simulate AI response time
  };

  const handleAnswer = (optionIndex) => {
    if (currentQuestion >= 5) {
      setQuizComplete(true);
      setScore(Math.floor(Math.random() * 5) + 1); // Random score for demo
    } else {
      setCurrentQuestion(curr => curr + 1);
      setQuestion(null); // Reset question for loading state
    }
  };

  if (quizComplete) {
    return (
      <div className="page" data-testid="quiz-results">
        <div className="card">
          <h2 data-testid="quiz-complete-message">Quiz Complete!</h2>
          <div data-testid="final-score">Score: {score}/5</div>
          <Link to="/dashboard">
            <button>Back to Dashboard</button>
          </Link>
        </div>
      </div>
    );
  }

  if (!question) {
    return (
      <div className="page">
        <div className="card">
          <div data-testid="ai-loading">Generating question...</div>
          <button data-testid="retry-button" onClick={generateQuestion}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="quiz-container">
        <div className="card">
          <div data-testid="question-number">Question {currentQuestion} of 5</div>
          <div data-testid="question-container">
            <h3 data-testid="question-text">{question.text}</h3>
            <div>
              {question.options.map((option, index) => (
                <button
                  key={index}
                  data-testid={`option-${index}`}
                  className="quiz-option"
                  onClick={() => handleAnswer(index)}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default QuizPage;
