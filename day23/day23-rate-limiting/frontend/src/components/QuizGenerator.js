import React, { useState } from 'react';
import { generateQuiz, submitQuiz } from '../services/api';
import toast from 'react-hot-toast';

const QuizGenerator = () => {
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(false);
  const [answers, setAnswers] = useState([]);
  const [result, setResult] = useState(null);
  const [formData, setFormData] = useState({
    topic: 'JavaScript',
    difficulty: 'medium',
    numQuestions: 5
  });

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const response = await generateQuiz(
        formData.topic,
        formData.difficulty,
        formData.numQuestions
      );
      
      if (response.success) {
        setQuiz(response.quiz);
        setAnswers(new Array(response.quiz.questions.length).fill(null));
        setResult(null);
        toast.success('Quiz generated successfully!');
      }
    } catch (error) {
      console.error('Quiz generation failed:', error);
      toast.error(error.message || 'Failed to generate quiz');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionIndex, answerIndex) => {
    const newAnswers = [...answers];
    newAnswers[questionIndex] = answerIndex;
    setAnswers(newAnswers);
  };

  const handleSubmit = async () => {
    if (answers.some(answer => answer === null)) {
      toast.error('Please answer all questions');
      return;
    }

    try {
      const response = await submitQuiz(quiz.quiz_id, answers);
      if (response.success) {
        setResult(response.result);
        toast.success(`Quiz completed! Score: ${response.result.percentage}`);
      }
    } catch (error) {
      console.error('Quiz submission failed:', error);
      toast.error(error.message || 'Failed to submit quiz');
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">AI Quiz Generator</h1>
      
      {/* Quiz Generation Form */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Generate New Quiz</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Topic</label>
            <input
              type="text"
              value={formData.topic}
              onChange={(e) => setFormData({...formData, topic: e.target.value})}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm px-3 py-2"
              placeholder="e.g., JavaScript, Python, React"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Difficulty</label>
            <select
              value={formData.difficulty}
              onChange={(e) => setFormData({...formData, difficulty: e.target.value})}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm px-3 py-2"
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Questions</label>
            <select
              value={formData.numQuestions}
              onChange={(e) => setFormData({...formData, numQuestions: parseInt(e.target.value)})}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm px-3 py-2"
            >
              <option value={3}>3 Questions</option>
              <option value={5}>5 Questions</option>
              <option value={10}>10 Questions</option>
            </select>
          </div>
        </div>
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? 'Generating...' : 'Generate Quiz'}
        </button>
      </div>

      {/* Quiz Display */}
      {quiz && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">{quiz.title}</h2>
          <p className="text-sm text-gray-600 mb-6">
            Difficulty: {quiz.difficulty} | Questions: {quiz.questions.length}
          </p>
          
          <div className="space-y-6">
            {quiz.questions.map((question, qIndex) => (
              <div key={question.id} className="border-b border-gray-200 pb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-3">
                  {qIndex + 1}. {question.question}
                </h3>
                <div className="space-y-2">
                  {question.options.map((option, oIndex) => (
                    <label key={oIndex} className="flex items-center">
                      <input
                        type="radio"
                        name={`question-${qIndex}`}
                        value={oIndex}
                        checked={answers[qIndex] === oIndex}
                        onChange={() => handleAnswerChange(qIndex, oIndex)}
                        className="mr-3"
                      />
                      <span>{option}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>
          
          <button
            onClick={handleSubmit}
            className="mt-6 px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
          >
            Submit Quiz
          </button>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quiz Results</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-green-600">{result.percentage}</p>
              <p className="text-sm text-gray-600">Final Score</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-blue-600">{result.correct_answers}</p>
              <p className="text-sm text-gray-600">Correct Answers</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-gray-600">{result.total_questions}</p>
              <p className="text-sm text-gray-600">Total Questions</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QuizGenerator;
