import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Trophy, CheckCircle, XCircle, RotateCcw, Home } from 'lucide-react';
import axios from '../config/axios';

const QuizResults = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await axios.get(`/api/quiz/session/${sessionId}/results`);
        setResults(response.data);
      } catch (error) {
        console.error('Failed to fetch results:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading results...</p>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
          <p className="text-red-600">Results not found.</p>
        </div>
      </div>
    );
  }

  const getScoreColor = (percentage) => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreGrade = (percentage) => {
    if (percentage >= 90) return 'A+';
    if (percentage >= 80) return 'A';
    if (percentage >= 70) return 'B';
    if (percentage >= 60) return 'C';
    return 'D';
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Score Summary */}
      <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-8 text-center">
          <Trophy className="h-16 w-16 mx-auto mb-4" />
          <h1 className="text-3xl font-bold mb-2">Quiz Completed!</h1>
          <p className="text-lg opacity-90">Great job on finishing the quiz</p>
        </div>
        
        <div className="p-8">
          <div className="grid md:grid-cols-3 gap-8 text-center">
            <div>
              <div className={`text-6xl font-bold ${getScoreColor(results.score.score_percentage)} mb-2`}>
                {results.score.score_percentage}%
              </div>
              <p className="text-gray-600">Overall Score</p>
            </div>
            <div>
              <div className="text-6xl font-bold text-blue-600 mb-2">
                {getScoreGrade(results.score.score_percentage)}
              </div>
              <p className="text-gray-600">Grade</p>
            </div>
            <div>
              <div className="text-6xl font-bold text-purple-600 mb-2">
                {results.score.correct_answers}/{results.score.total_questions}
              </div>
              <p className="text-gray-600">Correct Answers</p>
            </div>
          </div>
        </div>
      </div>

      {/* AI Feedback */}
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center space-x-2">
          <span>🤖</span>
          <span>AI Feedback</span>
        </h2>
        <div className="bg-blue-50 border-l-4 border-blue-500 p-6 rounded-r-lg">
          <p className="text-gray-700 leading-relaxed text-lg">
            {results.feedback}
          </p>
        </div>
      </div>

      {/* Detailed Answers */}
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Detailed Review</h2>
        <div className="space-y-6">
          {results.detailed_answers.map((item, index) => (
            <div 
              key={index}
              className={`border-l-4 p-6 rounded-r-lg ${
                item.is_correct 
                  ? 'border-green-500 bg-green-50' 
                  : 'border-red-500 bg-red-50'
              }`}
            >
              <div className="flex items-start space-x-3 mb-4">
                {item.is_correct ? (
                  <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0 mt-1" />
                ) : (
                  <XCircle className="h-6 w-6 text-red-600 flex-shrink-0 mt-1" />
                )}
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-800 mb-2 text-lg">
                    Question {index + 1}
                  </h3>
                  <p className="text-gray-700 mb-4">{item.question}</p>
                </div>
              </div>
              
              <div className="ml-9 space-y-3">
                <div>
                  <span className="font-medium text-gray-600">Your Answer: </span>
                  <span className={item.is_correct ? 'text-green-700' : 'text-red-700'}>
                    {item.user_answer}
                  </span>
                </div>
                
                {!item.is_correct && (
                  <div>
                    <span className="font-medium text-gray-600">Correct Answer: </span>
                    <span className="text-green-700">{item.correct_answer}</span>
                  </div>
                )}
                
                <div className="bg-white bg-opacity-70 p-4 rounded-lg">
                  <span className="font-medium text-gray-600">Explanation: </span>
                  <span className="text-gray-700">{item.explanation}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-center space-x-4">
        <button
          onClick={() => navigate('/')}
          className="flex items-center space-x-2 bg-gradient-to-r from-gray-600 to-gray-700 text-white px-6 py-3 rounded-xl font-semibold transition-all duration-300 hover:from-gray-700 hover:to-gray-800"
        >
          <Home className="h-5 w-5" />
          <span>Back to Quizzes</span>
        </button>
        
        <button
          onClick={() => window.location.reload()}
          className="flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-xl font-semibold transition-all duration-300 hover:from-blue-700 hover:to-purple-700"
        >
          <RotateCcw className="h-5 w-5" />
          <span>Try Again</span>
        </button>
      </div>
    </div>
  );
};

export default QuizResults;
