import React, { useState } from 'react';
import axios from 'axios';
import { Play, RefreshCw } from 'lucide-react';

const API_BASE = 'http://localhost:8000/api/v1';

function DifficultySimulator({ onUpdate }) {
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState(null);
  const [scenario, setScenario] = useState('balanced');

  const scenarios = {
    balanced: {
      name: 'Balanced Performance',
      responses: [
        { correct: true, time: 15000, confidence: 0.8 },
        { correct: true, time: 12000, confidence: 0.9 },
        { correct: false, time: 25000, confidence: 0.4 },
        { correct: true, time: 18000, confidence: 0.7 },
        { correct: true, time: 14000, confidence: 0.85 }
      ]
    },
    struggling: {
      name: 'Struggling Student',
      responses: [
        { correct: false, time: 35000, confidence: 0.3 },
        { correct: false, time: 40000, confidence: 0.2 },
        { correct: true, time: 30000, confidence: 0.4 },
        { correct: false, time: 38000, confidence: 0.25 },
        { correct: false, time: 42000, confidence: 0.3 }
      ]
    },
    excelling: {
      name: 'Excelling Student',
      responses: [
        { correct: true, time: 8000, confidence: 0.95 },
        { correct: true, time: 7000, confidence: 0.92 },
        { correct: true, time: 9000, confidence: 0.88 },
        { correct: true, time: 6000, confidence: 0.98 },
        { correct: true, time: 8500, confidence: 0.94 }
      ]
    },
    inconsistent: {
      name: 'Inconsistent Performance',
      responses: [
        { correct: true, time: 10000, confidence: 0.9 },
        { correct: false, time: 35000, confidence: 0.3 },
        { correct: true, time: 12000, confidence: 0.8 },
        { correct: false, time: 40000, confidence: 0.2 },
        { correct: true, time: 15000, confidence: 0.7 }
      ]
    }
  };

  const runSimulation = async () => {
    setIsRunning(true);
    setResults(null);

    try {
      const scenarioData = scenarios[scenario];
      const responses = scenarioData.responses.map((r, index) => ({
        question_id: `sim_q_${index + 1}`,
        is_correct: r.correct,
        response_time_ms: r.time,
        confidence_score: r.confidence,
        attempts: 1,
        timestamp: new Date().toISOString()
      }));

      const sessionData = {
        session_id: `sim_session_${Date.now()}`,
        start_time: new Date(Date.now() - 600000).toISOString(),
        questions_answered: responses.length,
        current_streak: responses.filter(r => r.is_correct).length,
        session_duration_ms: 600000
      };

      const request = {
        user_id: 'simulator_user',
        recent_performance: responses,
        session_data: sessionData,
        subject_area: 'simulation'
      };

      const response = await axios.post(`${API_BASE}/difficulty/next`, request);
      setResults(response.data);
      
      // Update parent component
      if (onUpdate) {
        onUpdate({
          scenario: scenarioData.name,
          responses: responses,
          recommendation: response.data,
          timestamp: new Date()
        });
      }

    } catch (error) {
      console.error('Simulation error:', error);
      setResults({ error: 'Simulation failed. Make sure the backend is running.' });
    } finally {
      setIsRunning(false);
    }
  };

  const resetSimulation = () => {
    setResults(null);
  };

  return (
    <div className="space-y-4">
      {/* Scenario Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Performance Scenario
        </label>
        <select 
          value={scenario}
          onChange={(e) => setScenario(e.target.value)}
          className="form-select w-full rounded-md border-gray-300"
          disabled={isRunning}
        >
          {Object.entries(scenarios).map(([key, scenario]) => (
            <option key={key} value={key}>{scenario.name}</option>
          ))}
        </select>
      </div>

      {/* Scenario Preview */}
      <div className="bg-gray-50 p-3 rounded-lg">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Scenario Preview:</h4>
        <div className="grid grid-cols-5 gap-2">
          {scenarios[scenario].responses.map((response, index) => (
            <div 
              key={index}
              className={`p-2 rounded text-center text-xs ${
                response.correct 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}
            >
              <div className="font-medium">Q{index + 1}</div>
              <div>{response.correct ? '✓' : '✗'}</div>
              <div>{(response.time / 1000).toFixed(1)}s</div>
              <div>{(response.confidence * 100).toFixed(0)}%</div>
            </div>
          ))}
        </div>
      </div>

      {/* Controls */}
      <div className="flex space-x-2">
        <button
          onClick={runSimulation}
          disabled={isRunning}
          className="btn btn-blue flex items-center space-x-2"
        >
          <Play className="h-4 w-4" />
          <span>{isRunning ? 'Running...' : 'Run Simulation'}</span>
        </button>
        <button
          onClick={resetSimulation}
          className="btn btn-outline-gray flex items-center space-x-2"
        >
          <RefreshCw className="h-4 w-4" />
          <span>Reset</span>
        </button>
      </div>

      {/* Results */}
      {results && (
        <div className="mt-4 p-4 bg-white border border-gray-200 rounded-lg">
          {results.error ? (
            <div className="text-red-600">
              <strong>Error:</strong> {results.error}
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="font-medium text-gray-900">Algorithm Recommendation</h4>
                <span className="text-sm text-gray-500">
                  Confidence: {(results.confidence * 100).toFixed(1)}%
                </span>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-600">Recommended Difficulty</div>
                  <div className="font-semibold text-lg capitalize text-blue-600">
                    {results.recommended_difficulty}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Learning State</div>
                  <div className="font-semibold text-lg capitalize text-purple-600">
                    {results.user_state?.replace('_', ' ')}
                  </div>
                </div>
              </div>

              <div>
                <div className="text-sm text-gray-600 mb-1">Algorithm Reasoning</div>
                <div className="text-sm bg-gray-50 p-2 rounded italic">
                  "{results.reasoning}"
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-xs">
                <div>
                  <div className="text-gray-600">Performance Metrics</div>
                  <div className="mt-1 space-y-1">
                    <div>Accuracy: {(results.adjustment_factors.accuracy * 100).toFixed(1)}%</div>
                    <div>Avg Response: {(results.adjustment_factors.response_time / 1000).toFixed(1)}s</div>
                    <div>Consistency: {(results.adjustment_factors.consistency * 100).toFixed(1)}%</div>
                    <div>Trend: {(results.adjustment_factors.trend * 100).toFixed(1)}%</div>
                  </div>
                </div>
                <div>
                  <div className="text-gray-600">Next Question Criteria</div>
                  <div className="mt-1 space-y-1">
                    <div>Difficulty Range: {results.next_question_criteria.difficulty_range.min.toFixed(2)} - {results.next_question_criteria.difficulty_range.max.toFixed(2)}</div>
                    <div>Focus: {results.next_question_criteria.subject_focus}</div>
                    <div>Types: {results.next_question_criteria.question_types.slice(0, 2).join(', ')}</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default DifficultySimulator;
