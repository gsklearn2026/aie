import React from 'react';
import { Link } from 'react-router-dom';
import { 
  PuzzlePieceIcon, 
  ChartBarIcon,
  ShieldCheckIcon,
  ClockIcon 
} from '@heroicons/react/24/outline';

const Dashboard = () => {
  const features = [
    {
      title: 'AI Quiz Generator',
      description: 'Generate custom quizzes using AI with rate limiting protection',
      icon: PuzzlePieceIcon,
      link: '/quiz',
      color: 'bg-blue-500'
    },
    {
      title: 'Rate Limit Monitor',
      description: 'Monitor API usage and rate limit status in real-time',
      icon: ChartBarIcon,
      link: '/rate-limits',
      color: 'bg-green-500'
    },
    {
      title: 'API Protection',
      description: 'Secure endpoints with tiered rate limiting',
      icon: ShieldCheckIcon,
      link: '/rate-limits',
      color: 'bg-purple-500'
    },
    {
      title: 'Request Throttling',
      description: 'Intelligent request management and throttling',
      icon: ClockIcon,
      link: '/rate-limits',
      color: 'bg-orange-500'
    }
  ];

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">
          Day 23: Rate Limiting & Request Throttling
        </h1>
        <p className="mt-4 text-lg text-gray-600">
          Learn how to protect your APIs and manage resources with intelligent rate limiting
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {features.map((feature) => {
          const Icon = feature.icon;
          return (
            <Link
              key={feature.title}
              to={feature.link}
              className="block bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6"
            >
              <div className="flex items-center space-x-4">
                <div className={`${feature.color} p-3 rounded-lg`}>
                  <Icon className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {feature.description}
                  </p>
                </div>
              </div>
            </Link>
          );
        })}
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Today's Learning Objectives
        </h2>
        <ul className="space-y-3 text-gray-600">
          <li className="flex items-start">
            <span className="text-green-500 mr-2">✓</span>
            Implement token bucket algorithm for rate limiting
          </li>
          <li className="flex items-start">
            <span className="text-green-500 mr-2">✓</span>
            Create tiered rate limits for different user types
          </li>
          <li className="flex items-start">
            <span className="text-green-500 mr-2">✓</span>
            Build real-time rate limit monitoring dashboard
          </li>
          <li className="flex items-start">
            <span className="text-green-500 mr-2">✓</span>
            Integrate with Redis for distributed rate limiting
          </li>
        </ul>
      </div>
    </div>
  );
};

export default Dashboard;
