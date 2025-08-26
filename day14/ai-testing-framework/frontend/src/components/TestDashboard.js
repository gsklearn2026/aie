import React, { useState, useEffect } from 'react';
import TestSuiteRunner from './TestSuiteRunner';
import TestResults from './TestResults';
import ProviderStatus from './ProviderStatus';

const TestDashboard = ({ systemHealth }) => {
  const [testSuites, setTestSuites] = useState({});
  const [activeTests, setActiveTests] = useState([]);
  const [testHistory, setTestHistory] = useState([]);

  useEffect(() => {
    loadPredefinedSuites();
    loadTestHistory();
  }, []);

  const loadPredefinedSuites = async () => {
    try {
      const response = await fetch('/api/test/predefined-suites');
      const data = await response.json();
      setTestSuites(data);
    } catch (error) {
      console.error('Failed to load test suites:', error);
    }
  };

  const loadTestHistory = () => {
    const history = JSON.parse(localStorage.getItem('testHistory') || '[]');
    setTestHistory(history.slice(-10)); // Keep last 10 test runs
  };

  const handleTestStart = (testId, suiteName) => {
    setActiveTests(prev => [...prev, { testId, suiteName, startTime: new Date() }]);
  };

  const handleTestComplete = (testId, results) => {
    setActiveTests(prev => prev.filter(test => test.testId !== testId));
    
    const testRecord = {
      testId,
      timestamp: new Date().toISOString(),
      results,
      summary: results.summary
    };
    
    const updatedHistory = [...testHistory, testRecord].slice(-10);
    setTestHistory(updatedHistory);
    localStorage.setItem('testHistory', JSON.stringify(updatedHistory));
  };

  return (
    <div className="test-dashboard">
      <div className="dashboard-grid">
        <div className="dashboard-section">
          <h2>System Status</h2>
          <ProviderStatus providers={systemHealth?.providers || []} />
        </div>

        <div className="dashboard-section">
          <h2>Test Suite Runner</h2>
          <TestSuiteRunner 
            testSuites={testSuites}
            onTestStart={handleTestStart}
            onTestComplete={handleTestComplete}
          />
        </div>

        <div className="dashboard-section full-width">
          <h2>Active Tests</h2>
          {activeTests.length === 0 ? (
            <p className="no-data">No active tests</p>
          ) : (
            <div className="active-tests">
              {activeTests.map(test => (
                <div key={test.testId} className="active-test">
                  <span className="test-name">{test.suiteName}</span>
                  <span className="test-status">Running...</span>
                  <span className="test-duration">
                    {Math.floor((new Date() - test.startTime) / 1000)}s
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="dashboard-section full-width">
          <h2>Test History</h2>
          <TestResults testHistory={testHistory} />
        </div>
      </div>
    </div>
  );
};

export default TestDashboard;
