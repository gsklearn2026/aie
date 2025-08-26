import React, { useState } from 'react';

const PerformanceMonitor = () => {
  const [testConfig, setTestConfig] = useState({
    concurrent_users: 5,
    requests_per_user: 3,
    prompt: 'Performance test prompt for load testing',
    max_response_time: 3000,
    min_success_rate: 0.9
  });
  
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState(null);

  const runPerformanceTest = async () => {
    setIsRunning(true);
    setResults(null);
    
    try {
      const response = await fetch('/api/validate/performance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testConfig)
      });
      
      const data = await response.json();
      setResults(data);
      
    } catch (error) {
      console.error('Performance test failed:', error);
      setResults({ error: error.message });
    } finally {
      setIsRunning(false);
    }
  };

  const updateConfig = (field, value) => {
    setTestConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="performance-monitor">
      <div className="test-configuration">
        <h2>Performance Test Configuration</h2>
        
        <div className="config-grid">
          <div className="config-item">
            <label>Concurrent Users:</label>
            <input
              type="number"
              value={testConfig.concurrent_users}
              onChange={(e) => updateConfig('concurrent_users', parseInt(e.target.value))}
              min="1"
              max="20"
              disabled={isRunning}
            />
          </div>
          
          <div className="config-item">
            <label>Requests per User:</label>
            <input
              type="number"
              value={testConfig.requests_per_user}
              onChange={(e) => updateConfig('requests_per_user', parseInt(e.target.value))}
              min="1"
              max="10"
              disabled={isRunning}
            />
          </div>
          
          <div className="config-item">
            <label>Max Response Time (ms):</label>
            <input
              type="number"
              value={testConfig.max_response_time}
              onChange={(e) => updateConfig('max_response_time', parseInt(e.target.value))}
              min="100"
              max="10000"
              step="100"
              disabled={isRunning}
            />
          </div>
          
          <div className="config-item">
            <label>Min Success Rate:</label>
            <input
              type="number"
              value={testConfig.min_success_rate}
              onChange={(e) => updateConfig('min_success_rate', parseFloat(e.target.value))}
              min="0"
              max="1"
              step="0.1"
              disabled={isRunning}
            />
          </div>
        </div>
        
        <div className="config-item full-width">
          <label>Test Prompt:</label>
          <textarea
            value={testConfig.prompt}
            onChange={(e) => updateConfig('prompt', e.target.value)}
            rows={3}
            disabled={isRunning}
          />
        </div>
        
        <button 
          onClick={runPerformanceTest}
          disabled={isRunning}
          className="run-test-button"
        >
          {isRunning ? 'Running Performance Test...' : 'Run Performance Test'}
        </button>
      </div>

      {results && (
        <div className="test-results">
          <h2>Performance Test Results</h2>
          
          {results.error ? (
            <div className="error-message">
              Error: {results.error}
            </div>
          ) : (
            <>
              <div className={`overall-status ${results.passed ? 'passed' : 'failed'}`}>
                <span className="status-icon">
                  {results.passed ? '✅' : '❌'}
                </span>
                <span className="status-text">
                  {results.passed ? 'Performance test passed' : 'Performance test failed'}
                </span>
              </div>
              
              <div className="metrics-grid">
                <div className="metric-card">
                  <div className="metric-value">
                    {Math.round(results.metrics.avg_response_time)}ms
                  </div>
                  <div className="metric-label">Average Response Time</div>
                </div>
                
                <div className="metric-card">
                  <div className="metric-value">
                    {Math.round(results.metrics.p95_response_time)}ms
                  </div>
                  <div className="metric-label">95th Percentile</div>
                </div>
                
                <div className="metric-card">
                  <div className="metric-value">
                    {Math.round(results.metrics.success_rate * 100)}%
                  </div>
                  <div className="metric-label">Success Rate</div>
                </div>
                
                <div className="metric-card">
                  <div className="metric-value">
                    {Math.round(results.metrics.throughput * 10) / 10}
                  </div>
                  <div className="metric-label">Requests/Second</div>
                </div>
                
                <div className="metric-card">
                  <div className="metric-value">
                    {results.metrics.total_requests}
                  </div>
                  <div className="metric-label">Total Requests</div>
                </div>
                
                <div className="metric-card">
                  <div className="metric-value">
                    {results.metrics.error_count}
                  </div>
                  <div className="metric-label">Errors</div>
                </div>
              </div>
              
              <div className="validation-results">
                <h3>Validation Results</h3>
                <div className="validation-grid">
                  {Object.entries(results.validation).map(([key, value]) => {
                    if (key === 'overall_passed') return null;
                    
                    return (
                      <div key={key} className={`validation-item ${value ? 'passed' : 'failed'}`}>
                        <span className="validation-icon">
                          {value ? '✅' : '❌'}
                        </span>
                        <span className="validation-name">
                          {key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default PerformanceMonitor;
