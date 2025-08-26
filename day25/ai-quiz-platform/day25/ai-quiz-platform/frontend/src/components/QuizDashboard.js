import React, { useState, useEffect } from 'react';
import ErrorBoundary from './ErrorBoundary';
import ApiService from '../services/api';
import toast from 'react-hot-toast';

const QuizDashboard = () => {
  const [loading, setLoading] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [healthStatus, setHealthStatus] = useState(null);
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('medium');

  useEffect(() => {
    checkHealthStatus();
    const interval = setInterval(checkHealthStatus, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const checkHealthStatus = async () => {
    try {
      const status = await ApiService.getHealthStatus();
      setHealthStatus(status);
    } catch (error) {
      console.error('Health check failed:', error);
    }
  };

  const generateQuiz = async () => {
    if (!topic.trim()) {
      toast.error('Please enter a topic for your quiz');
      return;
    }

    setLoading(true);
    try {
      const result = await ApiService.generateQuiz(topic, difficulty, 5);
      if (result.success) {
        setQuestions(result.data.questions);
        setCurrentQuestion(0);
        setAnswers({});
        toast.success('Quiz generated successfully!');
      }
    } catch (error) {
      console.error('Failed to generate quiz:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSelect = (questionIndex, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionIndex]: answer
    }));
  };

  const submitQuiz = async () => {
    try {
      const quizAnswers = Object.entries(answers).map(([index, answer]) => ({
        question_index: parseInt(index),
        selected_answer: answer
      }));

      const result = await ApiService.submitQuiz('quiz_123', quizAnswers);
      if (result.success) {
        toast.success(`Quiz completed! Score: ${result.data.percentage.toFixed(1)}%`);
      }
    } catch (error) {
      console.error('Failed to submit quiz:', error);
    }
  };

  const getServiceStatusColor = (status) => {
    switch (status) {
      case 'up': return 'text-green-600 bg-green-100';
      case 'degraded': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-red-600 bg-red-100';
    }
  };

  return (
    <ErrorBoundary fallbackMessage="The quiz component encountered an error. Please try refreshing.">
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <div className="flex justify-between items-center">
              <h1 className="text-2xl font-bold text-gray-900">AI Quiz Platform</h1>
              
              {/* Service Status */}
              {healthStatus && (
                <div className="flex items-center space-x-4">
                  <div className="text-sm">
                    <span className="text-gray-500">AI Service: </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getServiceStatusColor(healthStatus.services.ai_service.status)}`}>
                      {healthStatus.services.ai_service.status}
                    </span>
                  </div>
                  <div className="text-sm">
                    <span className="text-gray-500">Circuit Breaker: </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      healthStatus.services.ai_service.circuit_breaker.state === 'closed' 
                        ? 'text-green-600 bg-green-100' 
                        : 'text-red-600 bg-red-100'
                    }`}>
                      {healthStatus.services.ai_service.circuit_breaker.state}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Quiz Generation */}
          {questions.length === 0 && (
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Generate New Quiz</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Topic</label>
                  <input
                    type="text"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    placeholder="e.g., Machine Learning, Python, Data Science"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
                  <select
                    value={difficulty}
                    onChange={(e) => setDifficulty(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>
                
                <div className="flex items-end">
                  <button
                    onClick={generateQuiz}
                    disabled={loading}
                    className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium py-2 px-4 rounded-md transition-colors"
                  >
                    {loading ? 'Generating...' : 'Generate Quiz'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Quiz Questions */}
          {questions.length > 0 && (
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-lg font-medium text-gray-900">
                  Question {currentQuestion + 1} of {questions.length}
                </h2>
                <button
                  onClick={() => {
                    setQuestions([]);
                    setAnswers({});
                    setCurrentQuestion(0);
                  }}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Start New Quiz
                </button>
              </div>

              {questions[currentQuestion] && (
                <div className="space-y-4">
                  <h3 className="text-xl font-medium text-gray-800">
                    {questions[currentQuestion].question}
                  </h3>
                  
                  <div className="space-y-2">
                    {questions[currentQuestion].options.map((option, index) => (
                      <label key={index} className="flex items-center p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                        <input
                          type="radio"
                          name={`question-${currentQuestion}`}
                          value={option}
                          checked={answers[currentQuestion] === option}
                          onChange={() => handleAnswerSelect(currentQuestion, option)}
                          className="mr-3"
                        />
                        <span className="text-gray-700">{option}</span>
                      </label>
                    ))}
                  </div>

                  <div className="flex justify-between pt-4">
                    <button
                      onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                      disabled={currentQuestion === 0}
                      className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                    >
                      Previous
                    </button>
                    
                    {currentQuestion < questions.length - 1 ? (
                      <button
                        onClick={() => setCurrentQuestion(currentQuestion + 1)}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                      >
                        Next
                      </button>
                    ) : (
                      <button
                        onClick={submitQuiz}
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                      >
                        Submit Quiz
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </ErrorBoundary>
  );
};

export default QuizDashboard;
