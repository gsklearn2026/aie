import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, Clock, BookOpen } from 'lucide-react';
import axios from '../config/axios';

const QuizSelection = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const quizzes = [
    {
      id: 'ai-fundamentals',
      title: 'AI Engineering Fundamentals',
      description: 'Test your knowledge of core AI engineering concepts, algorithms, and best practices.',
      duration: 30,
      questions: 5,
      difficulty: 'Medium'
    },
    {
      id: 'react-state-management',
      title: 'React State Management',
      description: 'Explore React hooks, state management patterns, and component lifecycle.',
      duration: 25,
      questions: 5,
      difficulty: 'Intermediate'
    },
    {
      id: 'system-design',
      title: 'Distributed Systems Design',
      description: 'Challenge yourself with system architecture and scalability questions.',
      duration: 35,
      questions: 5,
      difficulty: 'Advanced'
    }
  ];

  const startQuiz = async (quiz) => {
    setLoading(true);
    try {
      const response = await axios.post('/api/quiz/start', {
        quiz_id: quiz.id,
        user_id: 'student_' + Date.now(),
        quiz_title: quiz.title
      });
      
      navigate(`/quiz/${response.data.session_id}`);
    } catch (error) {
      console.error('Failed to start quiz:', error);
      alert('Failed to start quiz. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">
          Choose Your Quiz Challenge
        </h1>
        <p className="text-xl text-gray-600">
          Test your AI engineering knowledge with interactive quizzes
        </p>
      </div>

      <div className="grid md:grid-cols-1 lg:grid-cols-1 gap-8">
        {quizzes.map((quiz) => (
          <div 
            key={quiz.id} 
            className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100"
          >
            <div className="p-8">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-2xl font-bold text-gray-800">{quiz.title}</h3>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  quiz.difficulty === 'Medium' ? 'bg-amber-100 text-amber-800' :
                  quiz.difficulty === 'Intermediate' ? 'bg-teal-100 text-teal-800' :
                  'bg-orange-100 text-orange-800'
                }`}>
                  {quiz.difficulty}
                </span>
              </div>
              
              <p className="text-gray-600 mb-6 leading-relaxed">
                {quiz.description}
              </p>
              
              <div className="flex items-center space-x-6 mb-6 text-sm text-gray-500">
                <div className="flex items-center space-x-2">
                  <Clock className="h-4 w-4" />
                  <span>{quiz.duration} minutes</span>
                </div>
                <div className="flex items-center space-x-2">
                  <BookOpen className="h-4 w-4" />
                  <span>{quiz.questions} questions</span>
                </div>
              </div>
              
              <button
                onClick={() => startQuiz(quiz)}
                disabled={loading}
                className="w-full bg-gradient-to-r from-emerald-500 to-teal-600 text-white py-4 px-6 rounded-xl font-semibold text-lg transition-all duration-300 hover:from-emerald-600 hover:to-teal-700 hover:transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                ) : (
                  <>
                    <Play className="h-5 w-5" />
                    <span>Start Quiz</span>
                  </>
                )}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default QuizSelection;
