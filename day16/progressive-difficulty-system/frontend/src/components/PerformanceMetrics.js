import React from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Target, Clock, Brain } from 'lucide-react';

function PerformanceMetrics({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <Brain className="h-12 w-12 mx-auto mb-4 text-gray-400" />
        <p>Run simulations to see performance metrics and algorithm decisions</p>
      </div>
    );
  }

  // Prepare chart data
  const chartData = data.map((item, index) => ({
    simulation: index + 1,
    scenario: item.scenario,
    accuracy: item.responses.filter(r => r.is_correct).length / item.responses.length * 100,
    avgResponseTime: item.responses.reduce((sum, r) => sum + r.response_time_ms, 0) / item.responses.length / 1000,
    avgConfidence: item.responses.reduce((sum, r) => sum + r.confidence_score, 0) / item.responses.length * 100,
    recommendedDifficulty: getDifficultyScore(item.recommendation.recommended_difficulty),
    userState: item.recommendation.user_state,
    confidence: item.recommendation.confidence * 100
  }));

  function getDifficultyScore(difficulty) {
    const scores = {
      'beginner': 1,
      'easy': 2,
      'medium': 3,
      'hard': 4,
      'expert': 5
    };
    return scores[difficulty] || 3;
  }

  const latest = data[data.length - 1];
  const latestMetrics = latest ? {
    accuracy: latest.responses.filter(r => r.is_correct).length / latest.responses.length,
    avgTime: latest.responses.reduce((sum, r) => sum + r.response_time_ms, 0) / latest.responses.length,
    avgConfidence: latest.responses.reduce((sum, r) => sum + r.confidence_score, 0) / latest.responses.length,
    consistency: 1 - (Math.sqrt(latest.responses.reduce((sum, r) => sum + Math.pow(r.response_time_ms - (latest.responses.reduce((s, resp) => s + resp.response_time_ms, 0) / latest.responses.length), 2), 0) / latest.responses.length) / (latest.responses.reduce((s, resp) => s + resp.response_time_ms, 0) / latest.responses.length))
  } : null;

  return (
    <div className="space-y-6">
      {/* Latest Metrics Summary */}
      {latestMetrics && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-blue-50 p-3 rounded-lg">
            <div className="flex items-center space-x-2 mb-1">
              <Target className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-800">Accuracy</span>
            </div>
            <div className="text-lg font-bold text-blue-900">
              {(latestMetrics.accuracy * 100).toFixed(1)}%
            </div>
          </div>
          <div className="bg-green-50 p-3 rounded-lg">
            <div className="flex items-center space-x-2 mb-1">
              <Clock className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium text-green-800">Avg Time</span>
            </div>
            <div className="text-lg font-bold text-green-900">
              {(latestMetrics.avgTime / 1000).toFixed(1)}s
            </div>
          </div>
        </div>
      )}

      {/* Accuracy vs Difficulty Trend */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 mb-3">Performance vs Difficulty Progression</h4>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="simulation" 
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => `Sim ${value}`}
            />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip 
              formatter={(value, name) => [
                `${value}${name.includes('accuracy') || name.includes('confidence') ? '%' : name.includes('Time') ? 's' : ''}`,
                name.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())
              ]}
              labelFormatter={(label) => `Simulation ${label}`}
            />
            <Line 
              type="monotone" 
              dataKey="accuracy" 
              stroke="#3b82f6" 
              strokeWidth={2}
              dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
              name="accuracy"
            />
            <Line 
              type="monotone" 
              dataKey="recommendedDifficulty" 
              stroke="#10b981" 
              strokeWidth={2}
              dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
              name="difficulty"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Algorithm Confidence Levels */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 mb-3">Algorithm Confidence in Recommendations</h4>
        <ResponsiveContainer width="100%" height={150}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="simulation" 
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => `S${value}`}
            />
            <YAxis tick={{ fontSize: 12 }} domain={[0, 100]} />
            <Tooltip 
              formatter={(value) => [`${value.toFixed(1)}%`, 'Algorithm Confidence']}
              labelFormatter={(label) => `Simulation ${label}`}
            />
            <Bar 
              dataKey="confidence" 
              fill="#8b5cf6"
              radius={[2, 2, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Recent Scenarios Summary */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 mb-3">Recent Simulations</h4>
        <div className="space-y-2">
          {data.slice(-3).map((item, index) => (
            <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
              <div className="flex items-center space-x-3">
                <div className="text-sm font-medium">{item.scenario}</div>
                <div className="text-xs text-gray-500">
                  {item.responses.filter(r => r.is_correct).length}/{item.responses.length} correct
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-medium capitalize text-blue-600">
                  {item.recommendation.recommended_difficulty}
                </div>
                <div className="text-xs text-gray-500 capitalize">
                  {item.recommendation.user_state.replace('_', ' ')}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default PerformanceMetrics;
