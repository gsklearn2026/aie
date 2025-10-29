import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Clock, CheckCircle } from 'lucide-react';
import axios from '../config/axios';

const QuizTaking = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  
  const [session, setSession] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);

  const fetchSession = useCallback(async () => {
    try {
      const response = await axios.get(`/api/quiz/session/${sessionId}`);
      setSession(response.data);
      setCurrentQuestion(response.data.current_question);
      setTimeRemaining(Math.floor(response.data.time_remaining));
      
      if (response.data.status === 'completed') {
        navigate(`/results/${sessionId}`);
      }
    } catch (error) {
      console.error('Failed to fetch session:', error);
    } finally {
      setLoading(false);
    }
  }, [sessionId, navigate]);

  useEffect(() => {
    fetchSession();
  }, [fetchSession]);

  // Timer effect
  useEffect(() => {
    if (timeRemaining > 0) {
      const timer = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            // Auto-submit when time runs out
            submitAnswer();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [timeRemaining]);

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const submitAnswer = async () => {
    if (!selectedAnswer || submitting) return;

    setSubmitting(true);
    try {
      const response = await axios.post(`/api/quiz/session/${sessionId}/answer`, {
        question_id: currentQuestion.id,
        answer: selectedAnswer,
        time_taken: 30 // Could track actual time taken
      });

      if (response.data.is_complete) {
        navigate(`/results/${sessionId}`);
      } else {
        // Reset for next question
        setSelectedAnswer('');
        await fetchSession();
      }
    } catch (error) {
      console.error('Failed to submit answer:', error);
      alert('Failed to submit answer. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading quiz...</p>
        </div>
      </div>
    );
  }

  if (!session || !currentQuestion) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
          <p className="text-red-600">Quiz session not found or completed.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
          <div className="flex justify-between items-center">
            <div className="text-sm opacity-90">
              Question {session.current_question_index + 1} of {session.total_questions}
            </div>
            <div className="flex items-center space-x-2 bg-white bg-opacity-20 px-4 py-2 rounded-full">
              <Clock className="h-4 w-4" />
              <span className="font-semibold">{formatTime(timeRemaining)}</span>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="mt-4 bg-white bg-opacity-20 rounded-full h-2">
            <div 
              className="bg-white h-2 rounded-full transition-all duration-500"
              style={{ width: `${session.progress}%` }}
            ></div>
          </div>
        </div>

        {/* Question Content */}
        <div className="p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-8 leading-relaxed">
            {currentQuestion.question}
          </h2>

          <div className="space-y-4 mb-8">
            {currentQuestion.options.map((option, index) => (
              <button
                key={index}
                onClick={() => setSelectedAnswer(option)}
                className={`w-full text-left p-6 rounded-xl border-2 transition-all duration-200 ${
                  selectedAnswer === option
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center space-x-4">
                  <div className={`w-6 h-6 rounded-full border-2 flex-shrink-0 ${
                    selectedAnswer === option
                      ? 'border-blue-500 bg-blue-500'
                      : 'border-gray-300'
                  }`}>
                    {selectedAnswer === option && (
                      <CheckCircle className="h-6 w-6 text-white" />
                    )}
                  </div>
                  <span className="text-lg">{option}</span>
                </div>
              </button>
            ))}
          </div>

          <div className="flex justify-end">
            <button
              onClick={submitAnswer}
              disabled={!selectedAnswer || submitting}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300 hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {submitting ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Submitting...</span>
                </>
              ) : (
                <span>Submit Answer</span>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuizTaking;
