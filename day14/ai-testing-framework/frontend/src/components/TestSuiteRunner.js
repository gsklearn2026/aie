import React, { useState } from 'react';

const TestSuiteRunner = ({ testSuites, onTestStart, onTestComplete }) => {
  const [selectedSuite, setSelectedSuite] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [customTestCases, setCustomTestCases] = useState('');

  const runTestSuite = async (suiteName, testCases) => {
    setIsRunning(true);
    
    try {
      // Start test suite
      const response = await fetch('/api/test/run-suite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          test_cases: testCases,
          suite_name: suiteName
        })
      });
      
      const { test_id } = await response.json();
      onTestStart(test_id, suiteName);
      
      // Poll for results
      const pollResults = async () => {
        try {
          const statusResponse = await fetch(`/api/test/status/${test_id}`);
          const status = await statusResponse.json();
          
          if (status.status === 'completed' || status.status === 'failed') {
            onTestComplete(test_id, status.results || { error: status.error });
            setIsRunning(false);
          } else {
            setTimeout(pollResults, 2000); // Poll every 2 seconds
          }
        } catch (error) {
          console.error('Error polling test status:', error);
          setIsRunning(false);
        }
      };
      
      pollResults();
      
    } catch (error) {
      console.error('Failed to start test suite:', error);
      setIsRunning(false);
    }
  };

  const handleRunPredefinedSuite = () => {
    if (!selectedSuite || !testSuites[selectedSuite]) return;
    
    const testCases = testSuites[selectedSuite];
    runTestSuite(selectedSuite, testCases);
  };

  const handleRunCustomSuite = () => {
    try {
      const testCases = JSON.parse(customTestCases);
      runTestSuite('custom_suite', testCases);
    } catch (error) {
      alert('Invalid JSON format for test cases');
    }
  };

  return (
    <div className="test-suite-runner">
      <div className="predefined-suites">
        <h3>Predefined Test Suites</h3>
        <select 
          value={selectedSuite} 
          onChange={(e) => setSelectedSuite(e.target.value)}
          disabled={isRunning}
        >
          <option value="">Select a test suite</option>
          {Object.keys(testSuites).map(suiteName => (
            <option key={suiteName} value={suiteName}>
              {suiteName.replace('_', ' ').toUpperCase()}
            </option>
          ))}
        </select>
        
        <button 
          onClick={handleRunPredefinedSuite}
          disabled={!selectedSuite || isRunning}
          className="run-button"
        >
          {isRunning ? 'Running...' : 'Run Suite'}
        </button>
      </div>

      <div className="custom-suite">
        <h3>Custom Test Cases</h3>
        <textarea
          value={customTestCases}
          onChange={(e) => setCustomTestCases(e.target.value)}
          placeholder='[{"name": "test1", "type": "generation", "prompt": "test prompt"}]'
          rows={6}
          disabled={isRunning}
        />
        
        <button 
          onClick={handleRunCustomSuite}
          disabled={!customTestCases.trim() || isRunning}
          className="run-button"
        >
          Run Custom Suite
        </button>
      </div>
    </div>
  );
};

export default TestSuiteRunner;
