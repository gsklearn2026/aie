import React, { useState } from 'react';
import { useMutation, useQuery } from 'react-query';
import { api } from '../services/api';
import { PlayIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

const ScoringDemo = () => {
  const [selectedStrategy, setSelectedStrategy] = useState('weighted');
  const [scoreResult, setScoreResult] = useState(null);

  const { data: sampleQuiz } = useQuery(
    'sample-quiz',
    () => api.getSampleQuiz()
  );

  const { data: strategies } = useQuery(
    'strategies',
    () => api.getStrategies()
  );

  const scoreMutation = useMutation(
    (submission) => api.calculateScore(submission),
    {
      onSuccess: (data) => {
        setScoreResult(data);
      }
    }
  );

  const handleRunDemo = async () => {
    if (!sampleQuiz) return;
    
    const submission = {
      ...sampleQuiz,
      strategy: selectedStrategy
    };

    scoreMutation.mutate(submission);
  };

  const resetDemo = () => {
    setScoreResult(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Scoring Engine Demo
        </h2>
        <p className="text-gray-600">
          Test different scoring strategies with sample quiz data
        </p>
      </div>

      {/* Demo Controls */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Demo Configuration
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Strategy Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Scoring Strategy
            </label>
            <select
              value={selectedStrategy}
              onChange={(e) => setSelectedStrategy(e.target.value)}
              className="block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {strategies?.strategies?.map((strategy) => (
                <option key={strategy.name} value={strategy.name}>
                  {strategy.name.charAt(0).toUpperCase() + strategy.name.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Control Buttons */}
          <div className="flex items-end space-x-3">
            <button
              onClick={handleRunDemo}
              disabled={scoreMutation.isLoading}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              <PlayIcon className="h-4 w-4 mr-2" />
              {scoreMutation.isLoading ? 'Running...' : 'Run Demo'}
            </button>
            
            <button
              onClick={resetDemo}
              className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
            >
              <ArrowPathIcon className="h-4 w-4 mr-2" />
              Reset
            </button>
          </div>
        </div>
      </div>

      {/* Sample Quiz Data */}
      {sampleQuiz && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Sample Quiz Data
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Quiz Info</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>Quiz ID: {sampleQuiz.quiz_id}</li>
                <li>User ID: {sampleQuiz.user_id}</li>
                <li>Total Time: {sampleQuiz.total_time}s</li>
                <li>Questions: {sampleQuiz.answers.length}</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Question Breakdown</h4>
              <div className="space-y-2">
                {sampleQuiz.answers.map((answer, index) => (
                  <div key={index} className="text-sm">
                    <span className={`inline-block w-3 h-3 rounded-full mr-2 ${
                      answer.is_correct ? 'bg-green-500' : 'bg-red-500'
                    }`}></span>
                    Q{index + 1}: Difficulty {answer.difficulty}, Weight {answer.weight}
                    {answer.confidence && `, Confidence ${answer.confidence}`}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Score Results */}
      {scoreResult && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Scoring Results
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-blue-600">
                {scoreResult.raw_score.toFixed(1)}
              </p>
              <p className="text-sm text-gray-500">Raw Score</p>
            </div>
            
            <div className="text-center">
              <p className="text-3xl font-bold text-green-600">
                {scoreResult.normalized_score.toFixed(1)}
              </p>
              <p className="text-sm text-gray-500">Normalized Score</p>
            </div>
            
            <div className="text-center">
              <p className="text-3xl font-bold text-purple-600">
                {scoreResult.percentile_rank ? scoreResult.percentile_rank.toFixed(1) : 'N/A'}
              </p>
              <p className="text-sm text-gray-500">Percentile Rank</p>
            </div>
          </div>

          {/* Score Breakdown */}
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Score Breakdown</h4>
            <div className="bg-gray-50 rounded-lg p-4">
              <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                {JSON.stringify(scoreResult.breakdown, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {scoreMutation.isError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">
            Error: {scoreMutation.error?.message || 'Failed to calculate score'}
          </p>
        </div>
      )}
    </div>
  );
};

export default ScoringDemo;
