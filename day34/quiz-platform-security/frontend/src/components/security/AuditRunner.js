import React, { useState } from 'react';
import { PlayIcon, StopIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import axios from 'axios';

const AuditRunner = () => {
  const [auditRunning, setAuditRunning] = useState(false);
  const [auditId, setAuditId] = useState(null);
  const [results, setResults] = useState(null);
  const [progress, setProgress] = useState(0);
  const [config, setConfig] = useState({
    includeAuth: true,
    includeAuthz: true,
    includeVuln: true,
    targetUrl: 'http://localhost:8000'
  });

  const startAudit = async () => {
    setAuditRunning(true);
    setResults(null);
    setProgress(0);
    
    try {
      const auditData = {};
      
      if (config.includeAuth) {
        auditData.auth_test_data = {
          passwords: ['password123', '12345678', 'Password123!', 'weak'],
          tokens: ['eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test'],
          session_tokens: ['abcd1234567890abcd1234567890abcd'],
          test_username: 'testuser@example.com'
        };
      }
      
      if (config.includeAuthz) {
        auditData.authz_scenarios = [
          { user_role: 'student', user_id: 'user1', target_user_id: 'user2' },
          { user_role: 'teacher', user_id: 'teacher1', target_user_id: 'student1' },
          { user_role: 'admin', user_id: 'admin1', target_user_id: 'user1' }
        ];
      }
      
      const response = await axios.post('/api/security/audit/run', auditData);
      setAuditId(response.data.audit_id);
      
      // Poll for results
      pollForResults(response.data.audit_id);
      
    } catch (error) {
      console.error('Failed to start audit:', error);
      setAuditRunning(false);
    }
  };

  const pollForResults = async (id) => {
    const maxAttempts = 120; // 4 minutes max (2 minutes of actual testing)
    let attempts = 0;
    
    const poll = async () => {
      try {
        const response = await axios.get(`/api/security/audit/${id}`);
        const data = response.data;
        
        if (data.status === 'completed') {
          setResults(data);
          setAuditRunning(false);
          setProgress(100);
          return;
        }
        
        if (data.status === 'failed') {
          console.error('Audit failed:', data.error);
          setAuditRunning(false);
          setProgress(0);
          return;
        }
        
        // Update progress based on attempts (simulate progress)
        const progressPercent = Math.min(90, (attempts / maxAttempts) * 100);
        setProgress(progressPercent);
        
        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(poll, 2000); // Poll every 2 seconds instead of 5
        } else {
          console.error('Audit timed out');
          setAuditRunning(false);
          setProgress(0);
        }
      } catch (error) {
        console.error('Failed to poll results:', error);
        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(poll, 2000);
        } else {
          setAuditRunning(false);
          setProgress(0);
        }
      }
    };
    
    setTimeout(poll, 1000); // Start polling after 1 second
  };

  const getSeverityColor = (level) => {
    switch (level) {
      case 'EXCELLENT': return 'bg-green-100 text-green-800';
      case 'GOOD': return 'bg-blue-100 text-blue-800';
      case 'MODERATE': return 'bg-yellow-100 text-yellow-800';
      case 'POOR': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Security Audit Runner</h1>
        <p className="mt-2 text-gray-600">Run comprehensive security audits on your Quiz Platform</p>
      </div>

      {/* Configuration Panel */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Audit Configuration</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Test Categories
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={config.includeAuth}
                  onChange={(e) => setConfig({...config, includeAuth: e.target.checked})}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-900">Authentication Testing</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={config.includeAuthz}
                  onChange={(e) => setConfig({...config, includeAuthz: e.target.checked})}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-900">Authorization Testing</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={config.includeVuln}
                  onChange={(e) => setConfig({...config, includeVuln: e.target.checked})}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-900">Vulnerability Scanning</span>
              </label>
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target URL
            </label>
            <input
              type="text"
              value={config.targetUrl}
              onChange={(e) => setConfig({...config, targetUrl: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="http://localhost:8000"
            />
          </div>
        </div>

        <div className="mt-6">
          <button
            onClick={startAudit}
            disabled={auditRunning}
            className={`inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
              auditRunning
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
            }`}
          >
            {auditRunning ? (
              <>
                <StopIcon className="h-4 w-4 mr-2 animate-spin" />
                Running Audit...
              </>
            ) : (
              <>
                <PlayIcon className="h-4 w-4 mr-2" />
                Start Security Audit
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results Panel */}
      {results && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Audit Results</h2>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSeverityColor(results.security_level)}`}>
              {results.security_level}
            </span>
          </div>

          {/* Overall Score */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Overall Security Score</span>
              <span className="text-2xl font-bold text-blue-600">{results.overall_security_score}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${results.overall_security_score}%` }}
              ></div>
            </div>
          </div>

          {/* Test Results Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            {results.authentication_report && (
              <div className="border rounded-lg p-4">
                <h3 className="text-sm font-semibold text-gray-900 mb-2">Authentication Tests</h3>
                <div className="text-2xl font-bold text-blue-600 mb-1">
                  {results.authentication_report.pass_rate?.toFixed(1) || 0}%
                </div>
                <div className="text-sm text-gray-600">
                  {results.authentication_report.passed_tests || 0} of {results.authentication_report.total_tests || 0} passed
                </div>
              </div>
            )}

            {results.authorization_report && (
              <div className="border rounded-lg p-4">
                <h3 className="text-sm font-semibold text-gray-900 mb-2">Authorization Tests</h3>
                <div className="text-2xl font-bold text-green-600 mb-1">
                  {results.authorization_report.pass_rate?.toFixed(1) || 0}%
                </div>
                <div className="text-sm text-gray-600">
                  {results.authorization_report.passed_tests || 0} of {results.authorization_report.total_tests || 0} passed
                </div>
              </div>
            )}

            {results.vulnerability_report && (
              <div className="border rounded-lg p-4">
                <h3 className="text-sm font-semibold text-gray-900 mb-2">Vulnerability Scan</h3>
                <div className="text-2xl font-bold text-purple-600 mb-1">
                  {results.vulnerability_report.security_score || 0}%
                </div>
                <div className="text-sm text-gray-600">
                  {results.vulnerability_report.total_vulnerabilities || 0} vulnerabilities found
                </div>
              </div>
            )}
          </div>

          {/* Recommendations */}
          {results.recommendations && results.recommendations.length > 0 && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Security Recommendations</h3>
              <ul className="space-y-2">
                {results.recommendations.map((recommendation, index) => (
                  <li key={index} className="flex items-start">
                    <DocumentTextIcon className="h-5 w-5 text-blue-600 mt-0.5 mr-2 flex-shrink-0" />
                    <span className="text-sm text-gray-700">{recommendation}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Loading State */}
      {auditRunning && !results && (
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Running Security Audit</h3>
          <p className="text-gray-600 mb-4">
            This may take a few minutes. We're testing authentication, authorization, and scanning for vulnerabilities.
          </p>
          
          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
            <div 
              className="bg-blue-600 h-2.5 rounded-full transition-all duration-300 ease-out" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-500 mb-2">{Math.round(progress)}% Complete</p>
          
          {auditId && (
            <p className="text-sm text-gray-500 mt-2">Audit ID: {auditId}</p>
          )}
        </div>
      )}
    </div>
  );
};

export default AuditRunner;
