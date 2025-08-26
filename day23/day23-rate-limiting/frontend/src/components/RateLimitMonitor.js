import React, { useState, useEffect } from 'react';
import { 
  ClockIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon 
} from '@heroicons/react/24/outline';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import toast from 'react-hot-toast';
import { getRateLimitStatus, upgradeTier } from '../services/api';

const RateLimitMonitor = () => {
  const [rateLimits, setRateLimits] = useState(null);
  const [loading, setLoading] = useState(true);
  const [userId, setUserId] = useState('user123');

  useEffect(() => {
    fetchRateLimitStatus();
    const interval = setInterval(fetchRateLimitStatus, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchRateLimitStatus = async () => {
    try {
      const data = await getRateLimitStatus(userId);
      setRateLimits(data.rate_limits);
    } catch (error) {
      console.error('Failed to fetch rate limit status:', error);
      toast.error('Failed to fetch rate limit status');
    } finally {
      setLoading(false);
    }
  };

  const handleUpgradeTier = async (tier) => {
    try {
      await upgradeTier(userId, tier);
      toast.success(`Upgraded to ${tier} tier!`);
      fetchRateLimitStatus();
    } catch (error) {
      console.error('Failed to upgrade tier:', error);
      toast.error('Failed to upgrade tier');
    }
  };

  const formatChartData = () => {
    if (!rateLimits) return [];
    
    return Object.entries(rateLimits).map(([endpoint, data]) => ({
      endpoint: endpoint.replace('_', ' ').toUpperCase(),
      remaining: data.tokens_remaining || 0,
      limit: data.tier_limit || 100,
      usage: (data.tier_limit || 100) - (data.tokens_remaining || 0)
    }));
  };

  const getStatusColor = (remaining, limit) => {
    const percentage = (remaining / limit) * 100;
    if (percentage > 50) return 'text-green-600';
    if (percentage > 20) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getStatusIcon = (remaining, limit) => {
    const percentage = (remaining / limit) * 100;
    if (percentage > 50) return CheckCircleIcon;
    if (percentage > 20) return ExclamationTriangleIcon;
    return ClockIcon;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const chartData = formatChartData();

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Rate Limit Monitor</h1>
        <div className="flex space-x-2">
          <button
            onClick={() => handleUpgradeTier('premium')}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Upgrade to Premium
          </button>
          <button
            onClick={() => handleUpgradeTier('admin')}
            className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
          >
            Admin Access
          </button>
        </div>
      </div>

      {/* User Info */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">User Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">User ID</label>
            <input
              type="text"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Current Tier</label>
            <p className="mt-1 text-lg font-semibold text-indigo-600">
              {rateLimits?.general?.tier || 'Free'}
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Window</label>
            <p className="mt-1 text-sm text-gray-600">
              {rateLimits?.general?.window ? `${rateLimits.general.window}s` : 'N/A'}
            </p>
          </div>
        </div>
      </div>

      {/* Rate Limit Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {rateLimits && Object.entries(rateLimits).map(([endpoint, data]) => {
          const StatusIcon = getStatusIcon(data.tokens_remaining || 0, data.tier_limit || 100);
          return (
            <div key={endpoint} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 capitalize">
                    {endpoint.replace('_', ' ')}
                  </p>
                  <p className="text-2xl font-bold text-gray-900">
                    {data.tokens_remaining || 0}
                  </p>
                  <p className="text-sm text-gray-500">
                    of {data.tier_limit || 100} remaining
                  </p>
                </div>
                <StatusIcon 
                  className={`h-8 w-8 ${getStatusColor(
                    data.tokens_remaining || 0, 
                    data.tier_limit || 100
                  )}`} 
                />
              </div>
              {data.reset_time && (
                <div className="mt-4 text-xs text-gray-500">
                  Resets: {new Date(data.reset_time * 1000).toLocaleTimeString()}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Usage Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">API Usage Overview</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="endpoint" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="usage" name="Used">
                {chartData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={entry.usage / entry.limit > 0.8 ? '#EF4444' : 
                         entry.usage / entry.limit > 0.5 ? '#F59E0B' : '#10B981'} 
                  />
                ))}
              </Bar>
              <Bar dataKey="remaining" name="Remaining" fill="#E5E7EB" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default RateLimitMonitor;
