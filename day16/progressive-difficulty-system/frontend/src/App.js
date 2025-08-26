import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { Brain, TrendingUp, Target, Clock, Award, AlertCircle } from 'lucide-react';
import DifficultySimulator from './components/DifficultySimulator';
import PerformanceMetrics from './components/PerformanceMetrics';
import './styles/cloudskills.css';

const API_BASE = 'http://localhost:8000/api/v1';

function App() {
  const [userState, setUserState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [simulationData, setSimulationData] = useState([]);
  const [currentUser, setCurrentUser] = useState('demo_user_123');

  const fetchUserState = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/user/${currentUser}/state`);
      setUserState(response.data);
    } catch (error) {
      console.error('Error fetching user state:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUserState();
  }, [currentUser]);

  const handleSimulationUpdate = (newData) => {
    setSimulationData(prev => [...prev, newData]);
  };

  const getStateColor = (state) => {
    switch (state) {
      case 'warming_up': return 'bg-blue-100 text-blue-800';
      case 'optimal_challenge': return 'bg-green-100 text-green-800';
      case 'struggling': return 'bg-red-100 text-red-800';
      case 'mastery': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-500';
      case 'easy': return 'bg-blue-500';
      case 'medium': return 'bg-yellow-500';
      case 'hard': return 'bg-orange-500';
      case 'expert': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header - Google Cloud Skills Boost Style */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Brain className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-xl font-semibold text-gray-900">Progressive Difficulty Engine</h1>
                <p className="text-sm text-gray-500">Adaptive Learning Algorithm Dashboard</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <select 
                value={currentUser} 
                onChange={(e) => setCurrentUser(e.target.value)}
                className="form-select rounded-md border-gray-300 text-sm"
              >
                <option value="demo_user_123">Demo User 123</option>
                <option value="demo_user_456">Demo User 456</option>
                <option value="demo_user_789">Demo User 789</option>
              </select>
              <button 
                onClick={fetchUserState}
                className="btn btn-outline-blue"
                disabled={loading}
              >
                {loading ? 'Loading...' : 'Refresh'}
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Status Overview */}
        {userState && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="card">
              <div className="card-header">
                <div className="flex items-center space-x-2">
                  <Target className="h-5 w-5 text-blue-600" />
                  <h3 className="card-title">Learning State</h3>
                </div>
              </div>
              <div className="card-content">
                <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${getStateColor(userState.current_state)}`}>
                  {userState.current_state?.replace('_', ' ').toUpperCase()}
                </span>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                  <h3 className="card-title">Current Accuracy</h3>
                </div>
              </div>
              <div className="card-content">
                <div className="text-2xl font-bold text-gray-900">
                  {(userState.current_accuracy * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <div className="flex items-center space-x-2">
                  <Award className="h-5 w-5 text-purple-600" />
                  <h3 className="card-title">Difficulty Level</h3>
                </div>
              </div>
              <div className="card-content">
                <div className="flex items-center space-x-2">
                  <div className={`w-4 h-4 rounded ${getDifficultyColor(userState.difficulty_level)}`}></div>
                  <span className="text-lg font-semibold capitalize">{userState.difficulty_level}</span>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <div className="flex items-center space-x-2">
                  <Clock className="h-5 w-5 text-orange-600" />
                  <h3 className="card-title">Sessions Completed</h3>
                </div>
              </div>
              <div className="card-content">
                <div className="text-2xl font-bold text-gray-900">
                  {userState.sessions_completed}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Difficulty Simulator */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Interactive Difficulty Simulator</h3>
              <p className="text-sm text-gray-600">Test how the algorithm responds to different performance patterns</p>
            </div>
            <div className="card-content">
              <DifficultySimulator onUpdate={handleSimulationUpdate} />
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Performance Metrics</h3>
              <p className="text-sm text-gray-600">Real-time algorithm decision visualization</p>
            </div>
            <div className="card-content">
              <PerformanceMetrics data={simulationData} />
            </div>
          </div>
        </div>

        {/* Algorithm Insights */}
        <div className="mt-8 card">
          <div className="card-header">
            <h3 className="card-title">Algorithm Insights</h3>
            <p className="text-sm text-gray-600">Understanding the progressive difficulty decision process</p>
          </div>
          <div className="card-content">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <Brain className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                <h4 className="font-semibold text-gray-900">Adaptive Learning</h4>
                <p className="text-sm text-gray-600 mt-1">
                  Algorithm maintains 85% target success rate for optimal challenge
                </p>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <TrendingUp className="h-8 w-8 text-green-600 mx-auto mb-2" />
                <h4 className="font-semibold text-gray-900">Performance Tracking</h4>
                <p className="text-sm text-gray-600 mt-1">
                  Monitors accuracy, response time, and confidence patterns
                </p>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <Target className="h-8 w-8 text-purple-600 mx-auto mb-2" />
                <h4 className="font-semibold text-gray-900">State Management</h4>
                <p className="text-sm text-gray-600 mt-1">
                  Four learning states: Warming Up, Optimal, Struggling, Mastery
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
