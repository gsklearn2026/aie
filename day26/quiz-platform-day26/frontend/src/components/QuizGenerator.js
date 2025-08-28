import React, { useState } from 'react';
import { Play, List, Upload } from 'lucide-react';
import JobStatus from './JobStatus';

const QuizGenerator = () => {
  const [activeTab, setActiveTab] = useState('single');
  const [singleForm, setSingleForm] = useState({
    topic: '',
    num_questions: 5,
    difficulty: 'medium'
  });
  const [batchForm, setBatchForm] = useState({
    topics: '',
    num_questions_per_topic: 5
  });
  const [currentJob, setCurrentJob] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSingleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResults(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/jobs/generate-quiz', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(singleForm),
      });

      const data = await response.json();
      setCurrentJob(data.job_id);
    } catch (error) {
      console.error('Error creating job:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBatchSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResults(null);

    const topics = batchForm.topics.split('\n').filter(topic => topic.trim());

    try {
      const response = await fetch('http://localhost:8000/api/v1/jobs/batch-quiz', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topics,
          num_questions_per_topic: batchForm.num_questions_per_topic
        }),
      });

      const data = await response.json();
      setCurrentJob(data.job_id);
    } catch (error) {
      console.error('Error creating batch job:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleJobComplete = (jobData) => {
    if (jobData.status === 'completed') {
      setResults(jobData.result_data);
    }
    // Reset current job to stop polling
    setCurrentJob(null);
  };

  const renderQuestions = (questions) => {
    return questions.map((q, index) => (
      <div key={index} className="p-4 border rounded-lg bg-white">
        <div className="font-medium mb-2">{index + 1}. {q.question}</div>
        <div className="space-y-1 mb-2">
          {q.options.map((option, optIndex) => (
            <div
              key={optIndex}
              className={`p-2 rounded text-sm ${
                optIndex === q.correct_answer
                  ? 'bg-green-100 text-green-800 font-medium'
                  : 'bg-gray-50'
              }`}
            >
              {String.fromCharCode(65 + optIndex)}. {option}
            </div>
          ))}
        </div>
        <div className="text-sm text-gray-600 italic">
          <strong>Explanation:</strong> {q.explanation}
        </div>
      </div>
    ));
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg">
        <div className="border-b border-gray-200">
          <nav className="flex">
            <button
              onClick={() => setActiveTab('single')}
              className={`py-4 px-6 text-sm font-medium ${
                activeTab === 'single'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Play className="w-4 h-4 inline mr-2" />
              Single Quiz
            </button>
            <button
              onClick={() => setActiveTab('batch')}
              className={`py-4 px-6 text-sm font-medium ${
                activeTab === 'batch'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <List className="w-4 h-4 inline mr-2" />
              Batch Quiz
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'single' && (
            <form onSubmit={handleSingleSubmit} className="space-y-4">
              <h3 className="text-lg font-medium mb-4">Generate Single Quiz</h3>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Topic
                </label>
                <input
                  type="text"
                  value={singleForm.topic}
                  onChange={(e) => setSingleForm({...singleForm, topic: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter quiz topic (e.g., Python Programming)"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Number of Questions
                  </label>
                  <select
                    value={singleForm.num_questions}
                    onChange={(e) => setSingleForm({...singleForm, num_questions: parseInt(e.target.value)})}
                    className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value={5}>5 Questions</option>
                    <option value={10}>10 Questions</option>
                    <option value={15}>15 Questions</option>
                    <option value={20}>20 Questions</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Difficulty
                  </label>
                  <select
                    value={singleForm.difficulty}
                    onChange={(e) => setSingleForm({...singleForm, difficulty: e.target.value})}
                    className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Creating Job...' : 'Generate Quiz'}
              </button>
            </form>
          )}

          {activeTab === 'batch' && (
            <form onSubmit={handleBatchSubmit} className="space-y-4">
              <h3 className="text-lg font-medium mb-4">Generate Batch Quizzes</h3>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Topics (one per line)
                </label>
                <textarea
                  value={batchForm.topics}
                  onChange={(e) => setBatchForm({...batchForm, topics: e.target.value})}
                  rows={6}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  placeholder="JavaScript Fundamentals&#10;React Hooks&#10;Node.js Basics&#10;MongoDB Operations"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Questions per Topic
                </label>
                <select
                  value={batchForm.num_questions_per_topic}
                  onChange={(e) => setBatchForm({...batchForm, num_questions_per_topic: parseInt(e.target.value)})}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value={3}>3 Questions</option>
                  <option value={5}>5 Questions</option>
                  <option value={10}>10 Questions</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Creating Batch Job...' : 'Generate Batch Quizzes'}
              </button>
            </form>
          )}

          {currentJob && (
            <div className="mt-6">
              <h4 className="text-md font-medium mb-3">Job Status</h4>
              <JobStatus jobId={currentJob} onJobComplete={handleJobComplete} />
            </div>
          )}

          {results && (
            <div className="mt-6">
              <h4 className="text-lg font-medium mb-4">Generated Questions</h4>
              
              {results.questions && (
                <div className="space-y-4">
                  {renderQuestions(results.questions)}
                </div>
              )}

              {results.batch_results && (
                <div className="space-y-6">
                  {results.batch_results.map((batch, index) => (
                    <div key={index} className="border-l-4 border-blue-500 pl-4">
                      <h5 className="text-md font-medium mb-3 text-blue-700">
                        {batch.topic}
                      </h5>
                      <div className="space-y-3">
                        {renderQuestions(batch.questions)}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default QuizGenerator;
