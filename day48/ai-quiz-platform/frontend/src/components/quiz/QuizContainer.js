import React, { useState, useEffect } from 'react';
import { useQuiz } from '../../hooks/useQuiz';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorDisplay from '../common/ErrorDisplay';
import QuizResults from './QuizResults';
import { ChevronRight, Clock } from 'lucide-react';

const QuizContainer = ({ topic = "JavaScript", difficulty = "medium" }) => {
  const {
    quiz,
    currentQuestion,
    loading,
    error,
    answers,
    submitAnswer,
    generateQuiz,
    retry
  } = useQuiz();
  
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  useEffect(() => {
    generateQuiz(topic, difficulty);
  }, [topic, difficulty]);

  const handleSubmitAnswer = async () => {
    if (selectedAnswer === null) return;
    
    setSubmitting(true);
    setSubmitError(null);
    
    try {
      await submitAnswer(quiz.quiz_id, currentQuestion, selectedAnswer);
      setSelectedAnswer(null);
      // Note: Quiz completion is checked automatically via answers.length
    } catch (err) {
      setSubmitError(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleRetry = () => {
    setSubmitError(null);
    retry();
  };

  if (loading) {
    return (
      <LoadingSpinner 
        message="Generating your personalized quiz..."
        fullScreen={true}
      />
    );
  }

  if (error) {
    return (
      <ErrorDisplay 
        error={error}
        onRetry={handleRetry}
        title="Failed to Load Quiz"
      />
    );
  }

  if (!quiz || !quiz.questions || quiz.questions.length === 0) {
    return (
      <ErrorDisplay 
        error="No quiz questions available"
        onRetry={handleRetry}
        title="Quiz Not Available"
      />
    );
  }

  // Check if quiz is complete (all questions answered)
  const isQuizComplete = answers.length === quiz.questions.length;

  // Show results if quiz is complete
  if (isQuizComplete) {
    return (
      <QuizResults 
        quiz={quiz}
        answers={answers}
        onRetakeQuiz={() => {
          generateQuiz(topic, difficulty);
        }}
      />
    );
  }

  const question = quiz.questions[currentQuestion];
  const progress = ((currentQuestion + 1) / quiz.questions.length) * 100;

  return (
    <div className="quiz-container">
      <div className="quiz-header">
        <h2>{quiz.topic} Quiz</h2>
        <div className="quiz-progress">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            />
          </div>
          <span className="progress-text">
            Question {currentQuestion + 1} of {quiz.questions.length}
          </span>
        </div>
      </div>

      <div className="question-container">
        <h3 className="question-text">{question.question}</h3>
        
        <div className="options-container">
          {question.options.map((option, index) => (
            <button
              key={index}
              onClick={() => setSelectedAnswer(index)}
              className={`option-button ${
                selectedAnswer === index ? 'selected' : ''
              }`}
              disabled={submitting}
            >
              <span className="option-letter">
                {String.fromCharCode(65 + index)}
              </span>
              <span className="option-text">{option}</span>
            </button>
          ))}
        </div>

        {submitError && (
          <ErrorDisplay 
            error={submitError}
            onRetry={() => setSubmitError(null)}
            title="Failed to Submit Answer"
          />
        )}

        <div className="quiz-actions">
          <button
            onClick={handleSubmitAnswer}
            disabled={selectedAnswer === null || submitting}
            className="submit-button"
          >
            {submitting ? (
              <>
                <LoadingSpinner type="pulse" size={8} />
                Submitting...
              </>
            ) : (
              <>
                Submit Answer
                <ChevronRight size={16} />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default QuizContainer;
