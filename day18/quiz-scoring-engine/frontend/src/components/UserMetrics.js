import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { api } from '../services/api';

const UserMetrics = () => {
  const [userId, setUserId] = useState('demo-user-123');

  const { data: metrics, isLoading, error } = useQuery(
    ['user-metrics', userId],
    () => api.getUserMetrics(userId),
    { enabled: !!userId }
  );

  const performanceTrendData = metrics?.performance_trend?.map((score, index) => ({
    quiz: index + 1,
    score: score
  })) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          User Performance Metrics
        </h2>
        <p className="text-gray-600">
          Analyze individual user performance and trends
        </p>
      </div>

      {/* User Selection */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Select User
        </h3>
        <div className="max-w-md">
          <input
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="Enter User ID"
            className="block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="bg-white shadow rounded-lg p-6">
          <p className="text-gray-500">Loading user metrics...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">
            Error loading metrics: {error.message}
          </p>
        </div>
      )}

      {/* Metrics Display */}
      {metrics && (
        <>
          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Average Score
              </h3>
              <p className="text-3xl font-bold text-blue-600">
                {metrics.average_score.toFixed(1)}%
              </p>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Total Quizzes
              </h3>
              <p className="text-3xl font-bold text-green-600">
                {metrics.total_quizzes}
              </p>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Performance Trend
              </h3>
              <p className="text-3xl font-bold text-purple-600">
                {metrics.performance_trend.length > 1 ? (
                  metrics.performance_trend[metrics.performance_trend.length - 1] > 
                  metrics.performance_trend[metrics.performance_trend.length - 2] ? '↗️' : '↘️'
                ) : '📊'}
              </p>
            </div>
          </div>

          {/* Performance Chart */}
          {performanceTrendData.length > 0 && (
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Performance Over Time
              </h3>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={performanceTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="quiz" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip 
                    formatter={(value) => [`${value.toFixed(1)}%`, 'Score']}
                    labelFormatter={(label) => `Quiz ${label}`}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="score" 
                    stroke="#3B82F6" 
                    strokeWidth={2}
                    dot={{ fill: '#3B82F6', strokeWidth: 2 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Difficulty Preferences */}
          {Object.keys(metrics.difficulty_preferences).length > 0 && (
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Difficulty Preferences
              </h3>
              <div className="space-y-2">
                {Object.entries(metrics.difficulty_preferences).map(([difficulty, score]) => (
                  <div key={difficulty} className="flex justify-between items-center">
                    <span className="text-gray-700">Difficulty {difficulty}</span>
                    <span className="font-medium">{score.toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default UserMetrics;
