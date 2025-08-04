import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { ChartBarIcon, CogIcon, UserIcon } from '@heroicons/react/24/outline';
import { api } from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalScores: 0,
    averageScore: 0,
    activeStrategies: 4
  });

  const { data: strategies, isLoading: strategiesLoading } = useQuery(
    'strategies',
    () => api.getStrategies()
  );

  const performanceData = [
    { day: 'Mon', score: 85 },
    { day: 'Tue', score: 78 },
    { day: 'Wed', score: 92 },
    { day: 'Thu', score: 88 },
    { day: 'Fri', score: 95 },
    { day: 'Sat', score: 87 },
    { day: 'Sun', score: 91 }
  ];

  const strategyData = [
    { strategy: 'Basic', count: 45 },
    { strategy: 'Weighted', count: 78 },
    { strategy: 'Adaptive', count: 92 },
    { strategy: 'Confidence', count: 34 }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Quiz Scoring Engine Dashboard
        </h2>
        <p className="text-gray-600">
          Monitor scoring performance and system health
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center">
            <ChartBarIcon className="h-8 w-8 text-blue-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Scores</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalScores}</p>
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center">
            <UserIcon className="h-8 w-8 text-green-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Average Score</p>
              <p className="text-2xl font-bold text-gray-900">{stats.averageScore}%</p>
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center">
            <CogIcon className="h-8 w-8 text-purple-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Active Strategies</p>
              <p className="text-2xl font-bold text-gray-900">{stats.activeStrategies}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Trend */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Performance Trend
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="score" 
                stroke="#3B82F6" 
                strokeWidth={2}
                dot={{ fill: '#3B82F6' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Strategy Usage */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Strategy Usage
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={strategyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="strategy" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#10B981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Available Strategies */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Available Scoring Strategies
        </h3>
        {strategiesLoading ? (
          <p className="text-gray-500">Loading strategies...</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {strategies?.strategies?.map((strategy, index) => (
              <div key={index} className="border rounded-lg p-4">
                <h4 className="font-medium text-gray-900 capitalize">
                  {strategy.name}
                </h4>
                <p className="text-sm text-gray-600 mt-1">
                  {strategy.description}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
