import React from 'react';
import { CheckCircle, XCircle, Trophy, RotateCcw } from 'lucide-react';

const QuizResults = ({ quiz, answers, onRetakeQuiz }) => {
  if (!quiz || !answers || answers.length === 0) {
    return null;
  }

  // Calculate score
  const correctAnswers = answers.filter(a => a.correct).length;
  const totalQuestions = quiz.questions.length;
  const score = answers.reduce((sum, a) => sum + (a.score || 0), 0);
  const percentage = Math.round((correctAnswers / totalQuestions) * 100);
  
  // Determine performance message
  let performanceMessage = '';
  let performanceColor = '';
  if (percentage >= 90) {
    performanceMessage = 'Outstanding! You\'re a master!';
    performanceColor = '#10b981'; // green
  } else if (percentage >= 70) {
    performanceMessage = 'Great job! Well done!';
    performanceColor = '#3b82f6'; // blue
  } else if (percentage >= 50) {
    performanceMessage = 'Good effort! Keep practicing!';
    performanceColor = '#f59e0b'; // orange
  } else {
    performanceMessage = 'Keep learning! You\'ll improve!';
    performanceColor = '#ef4444'; // red
  }

  return (
    <div className="quiz-results">
      <div className="results-header">
        <div className="results-icon" style={{ color: performanceColor }}>
          <Trophy size={64} />
        </div>
        <h2>Quiz Complete!</h2>
        <p className="results-topic">{quiz.topic} Quiz - {quiz.difficulty}</p>
      </div>

      <div className="results-score">
        <div className="score-circle" style={{ borderColor: performanceColor }}>
          <div className="score-number" style={{ color: performanceColor }}>
            {percentage}%
          </div>
          <div className="score-label">Score</div>
        </div>
        <div className="score-details">
          <div className="score-stat">
            <CheckCircle size={20} className="stat-icon correct" />
            <span className="stat-value">{correctAnswers}</span>
            <span className="stat-label">Correct</span>
          </div>
          <div className="score-stat">
            <XCircle size={20} className="stat-icon incorrect" />
            <span className="stat-value">{totalQuestions - correctAnswers}</span>
            <span className="stat-label">Incorrect</span>
          </div>
          <div className="score-stat">
            <Trophy size={20} className="stat-icon score" />
            <span className="stat-value">{score}</span>
            <span className="stat-label">Points</span>
          </div>
        </div>
      </div>

      <div className="results-message" style={{ backgroundColor: `${performanceColor}15`, borderColor: `${performanceColor}40` }}>
        <p style={{ color: performanceColor }}>{performanceMessage}</p>
      </div>

      <div className="results-breakdown">
        <h3>Question Breakdown</h3>
        <div className="questions-list">
          {quiz.questions.map((question, index) => {
            const answer = answers.find(a => a.questionIndex === index);
            const isCorrect = answer?.correct || false;
            const selectedOption = answer?.selectedAnswer;
            const correctOption = question.correct_answer;
            
            return (
              <div 
                key={index} 
                className={`question-result ${isCorrect ? 'correct' : 'incorrect'}`}
              >
                <div className="question-result-header">
                  <div className="question-number">Question {index + 1}</div>
                  <div className="question-status">
                    {isCorrect ? (
                      <CheckCircle size={20} className="status-icon correct" />
                    ) : (
                      <XCircle size={20} className="status-icon incorrect" />
                    )}
                  </div>
                </div>
                <div className="question-result-text">{question.question}</div>
                <div className="question-result-answers">
                  <div className={`answer-detail ${isCorrect ? 'correct-answer' : 'selected-wrong'}`}>
                    <span className="answer-label">Your Answer:</span>
                    <span className="answer-text">
                      {String.fromCharCode(65 + selectedOption)}. {question.options[selectedOption]}
                    </span>
                  </div>
                  {!isCorrect && (
                    <div className="answer-detail correct-answer">
                      <span className="answer-label">Correct Answer:</span>
                      <span className="answer-text">
                        {String.fromCharCode(65 + correctOption)}. {question.options[correctOption]}
                      </span>
                    </div>
                  )}
                  {(answer?.explanation || question.explanation) && (
                    <div className="answer-explanation">
                      <strong>Explanation:</strong> {answer?.explanation || question.explanation}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="results-actions">
        <button 
          onClick={onRetakeQuiz}
          className="retake-button"
        >
          <RotateCcw size={18} />
          Take Another Quiz
        </button>
      </div>
    </div>
  );
};

export default QuizResults;

