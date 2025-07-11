import React, { useState } from 'react';

const TestResults = ({ testHistory }) => {
  const [selectedTest, setSelectedTest] = useState(null);

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#4caf50';
      case 'failed': return '#f44336';
      case 'running': return '#ff9800';
      default: return '#757575';
    }
  };

  const formatDuration = (seconds) => {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  };

  return (
    <div className="test-results">
      {testHistory.length === 0 ? (
        <p className="no-data">No test history available</p>
      ) : (
        <>
          <div className="results-list">
            {testHistory.map((test, index) => (
              <div 
                key={test.testId} 
                className={`result-item ${selectedTest?.testId === test.testId ? 'selected' : ''}`}
                onClick={() => setSelectedTest(test)}
              >
                <div className="result-header">
                  <span className="test-name">{test.testId}</span>
                  <span 
                    className="test-status"
                    style={{ color: getStatusColor(test.results?.status) }}
                  >
                    {test.results?.status || 'unknown'}
                  </span>
                </div>
                
                <div className="result-summary">
                  <span className="timestamp">
                    {new Date(test.timestamp).toLocaleString()}
                  </span>
                  
                  {test.summary && (
                    <div className="summary-stats">
                      <span className="stat passed">✓ {test.summary.passed}</span>
                      <span className="stat failed">✗ {test.summary.failed}</span>
                      <span className="stat duration">
                        ⏱ {formatDuration(test.summary.total_execution_time)}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {selectedTest && (
            <div className="result-details">
              <h3>Test Details: {selectedTest.testId}</h3>
              
              {selectedTest.summary && (
                <div className="summary-section">
                  <h4>Summary</h4>
                  <div className="summary-grid">
                    <div className="summary-item">
                      <span className="label">Total Tests:</span>
                      <span className="value">{selectedTest.summary.total}</span>
                    </div>
                    <div className="summary-item">
                      <span className="label">Passed:</span>
                      <span className="value passed">{selectedTest.summary.passed}</span>
                    </div>
                    <div className="summary-item">
                      <span className="label">Failed:</span>
                      <span className="value failed">{selectedTest.summary.failed}</span>
                    </div>
                    <div className="summary-item">
                      <span className="label">Success Rate:</span>
                      <span className="value">
                        {Math.round(selectedTest.summary.success_rate * 100)}%
                      </span>
                    </div>
                    <div className="summary-item">
                      <span className="label">Avg Time:</span>
                      <span className="value">
                        {Math.round(selectedTest.summary.average_test_time * 1000)}ms
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {selectedTest.results?.results && (
                <div className="individual-results">
                  <h4>Individual Test Results</h4>
                  {selectedTest.results.results.map((result, index) => (
                    <div key={index} className="individual-result">
                      <div className="result-name">
                        <span className={`status-dot ${result.status}`}></span>
                        {result.test_name}
                      </div>
                      <div className="result-details-content">
                        <div className="detail-item">
                          <span className="label">Execution Time:</span>
                          <span className="value">{Math.round(result.execution_time * 1000)}ms</span>
                        </div>
                        
                        {result.details && Object.keys(result.details).length > 0 && (
                          <div className="detail-item">
                            <span className="label">Details:</span>
                            <pre className="details-json">
                              {JSON.stringify(result.details, null, 2)}
                            </pre>
                          </div>
                        )}
                        
                        {result.error_message && (
                          <div className="detail-item error">
                            <span className="label">Error:</span>
                            <span className="value">{result.error_message}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default TestResults;
