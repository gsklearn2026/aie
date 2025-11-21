import React, { useState } from 'react';
import './QuestionDisplay.css';

function QuestionDisplay({ question }) {
  const { metadata, quality_score } = question;
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleAnswerSelect = (answer) => {
    if (!isSubmitted) {
      setSelectedAnswer(answer);
    }
  };

  const handleSubmit = () => {
    if (selectedAnswer !== null) {
      setIsSubmitted(true);
    }
  };

  const isCorrect = (answer) => {
    if (question.question_type === 'multiple_choice') {
      return answer.startsWith(question.correct_answer);
    } else if (question.question_type === 'true_false') {
      return answer.toLowerCase() === question.correct_answer.toLowerCase();
    }
    return false;
  };

  const renderQuestion = () => {
    switch (question.question_type) {
      case 'multiple_choice':
        return (
          <>
            <div className="question-text">{question.question}</div>
            <div className="options">
              {question.options && question.options.map((option, idx) => {
                const optionLetter = option.split(')')[0];
                const isSelected = selectedAnswer === option;
                const isCorrectAnswer = option.startsWith(question.correct_answer);
                const showResult = isSubmitted && (isSelected || isCorrectAnswer);
                
                let optionClass = 'option';
                if (isSelected) optionClass += ' selected';
                if (showResult && isCorrectAnswer) optionClass += ' correct';
                if (showResult && isSelected && !isCorrectAnswer) optionClass += ' incorrect';
                
                return (
                  <div 
                    key={idx} 
                    className={optionClass}
                    onClick={() => handleAnswerSelect(option)}
                  >
                    {option}
                    {showResult && isCorrectAnswer && <span className="result-badge correct-badge">✓ Correct</span>}
                    {showResult && isSelected && !isCorrectAnswer && <span className="result-badge incorrect-badge">✗ Incorrect</span>}
                  </div>
                );
              })}
            </div>
            {!isSubmitted && (
              <button 
                className="submit-button" 
                onClick={handleSubmit}
                disabled={selectedAnswer === null}
              >
                Submit Answer
              </button>
            )}
            {isSubmitted && (
              <div className="result-section">
                <div className={`result-message ${isCorrect(selectedAnswer) ? 'correct' : 'incorrect'}`}>
                  {isCorrect(selectedAnswer) ? (
                    <span>✓ Correct! Well done!</span>
                  ) : (
                    <span>✗ Incorrect. The correct answer is {question.correct_answer}.</span>
                  )}
                </div>
                <div className="explanation">
                  <strong>Explanation:</strong> {question.explanation}
                </div>
              </div>
            )}
          </>
        );
      
      case 'true_false':
        return (
          <>
            <div className="question-text">{question.question}</div>
            <div className="options">
              <div 
                className={`option ${selectedAnswer === 'true' ? 'selected' : ''} ${isSubmitted && question.correct_answer.toLowerCase() === 'true' ? 'correct' : ''} ${isSubmitted && selectedAnswer === 'true' && question.correct_answer.toLowerCase() !== 'true' ? 'incorrect' : ''}`}
                onClick={() => handleAnswerSelect('true')}
              >
                True
                {isSubmitted && question.correct_answer.toLowerCase() === 'true' && <span className="result-badge correct-badge">✓ Correct</span>}
                {isSubmitted && selectedAnswer === 'true' && question.correct_answer.toLowerCase() !== 'true' && <span className="result-badge incorrect-badge">✗ Incorrect</span>}
              </div>
              <div 
                className={`option ${selectedAnswer === 'false' ? 'selected' : ''} ${isSubmitted && question.correct_answer.toLowerCase() === 'false' ? 'correct' : ''} ${isSubmitted && selectedAnswer === 'false' && question.correct_answer.toLowerCase() !== 'false' ? 'incorrect' : ''}`}
                onClick={() => handleAnswerSelect('false')}
              >
                False
                {isSubmitted && question.correct_answer.toLowerCase() === 'false' && <span className="result-badge correct-badge">✓ Correct</span>}
                {isSubmitted && selectedAnswer === 'false' && question.correct_answer.toLowerCase() !== 'false' && <span className="result-badge incorrect-badge">✗ Incorrect</span>}
              </div>
            </div>
            {!isSubmitted && (
              <button 
                className="submit-button" 
                onClick={handleSubmit}
                disabled={selectedAnswer === null}
              >
                Submit Answer
              </button>
            )}
            {isSubmitted && (
              <div className="result-section">
                <div className={`result-message ${isCorrect(selectedAnswer) ? 'correct' : 'incorrect'}`}>
                  {isCorrect(selectedAnswer) ? (
                    <span>✓ Correct! Well done!</span>
                  ) : (
                    <span>✗ Incorrect. The correct answer is {question.correct_answer}.</span>
                  )}
                </div>
                <div className="explanation">
                  <strong>Explanation:</strong> {question.explanation}
                </div>
              </div>
            )}
          </>
        );
      
      case 'short_answer':
        return (
          <>
            <div className="question-text">{question.question}</div>
            <div className="answer-section">
              <strong>Expected Answer:</strong>
              <div className="answer-text">{question.correct_answer}</div>
            </div>
            {question.explanation && (
              <div className="explanation">
                <strong>Explanation:</strong> {question.explanation}
              </div>
            )}
          </>
        );
      
      case 'essay':
        return (
          <>
            <div className="question-text">{question.question}</div>
            {question.guidance && (
              <div className="guidance-section">
                <strong>Guidance:</strong> {question.guidance}
              </div>
            )}
            {question.rubric && (
              <div className="rubric-section">
                <strong>Evaluation Rubric:</strong> {question.rubric}
              </div>
            )}
          </>
        );
      
      case 'coding':
        return (
          <>
            <div className="question-text">{question.question}</div>
            {question.requirements && (
              <div className="requirements-section">
                <strong>Requirements:</strong>
                <ul>
                  {question.requirements.map((req, idx) => (
                    <li key={idx}>{req}</li>
                  ))}
                </ul>
              </div>
            )}
            {question.test_cases && (
              <div className="test-cases-section">
                <strong>Test Cases:</strong>
                {question.test_cases.map((tc, idx) => (
                  <div key={idx} className="test-case">
                    <div>Input: {tc.input}</div>
                    <div>Output: {tc.output}</div>
                  </div>
                ))}
              </div>
            )}
          </>
        );
      
      default:
        return <div className="question-text">{JSON.stringify(question, null, 2)}</div>;
    }
  };

  return (
    <div className="question-display">
      <div className="question-header">
        <h2>Generated Question</h2>
        <div className="quality-indicator">
          <span className="quality-label">Quality Score:</span>
          <span className={`quality-score ${quality_score >= 4 ? 'excellent' : quality_score >= 3 ? 'good' : 'fair'}`}>
            {quality_score?.toFixed(1)}/5.0
          </span>
        </div>
      </div>

      <div className="question-content">
        {renderQuestion()}
      </div>

      <div className="metadata-section">
        <h3>Generation Metadata</h3>
        <div className="metadata-grid">
          <div className="metadata-item">
            <span className="metadata-label">AI Profile:</span>
            <span className="metadata-value">{metadata?.profile_used}</span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Latency:</span>
            <span className="metadata-value">{metadata?.latency_ms?.toFixed(0)}ms</span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Fallbacks:</span>
            <span className="metadata-value">{metadata?.fallback_count || 0}</span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Generated:</span>
            <span className="metadata-value">
              {metadata?.generated_at && new Date(metadata.generated_at).toLocaleTimeString()}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default QuestionDisplay;
