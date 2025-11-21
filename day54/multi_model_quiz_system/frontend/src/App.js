import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import GenerationForm from './components/GenerationForm';
import QuestionDisplay from './components/QuestionDisplay';
import MetricsDashboard from './components/MetricsDashboard';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [activeTab, setActiveTab] = useState('generate');
  const [generatedQuestion, setGeneratedQuestion] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [profiles, setProfiles] = useState({});

  useEffect(() => {
    fetchProfiles();
  }, []);

  const fetchProfiles = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/generation/profiles`);
      setProfiles(response.data);
    } catch (err) {
      console.error('Failed to fetch profiles:', err);
    }
  };

  const handleGenerate = async (formData) => {
    setLoading(true);
    setError(null);
    setGeneratedQuestion(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/generation/generate`, formData);
      setGeneratedQuestion(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Generation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🤖 Multi-Model Quiz Generation</h1>
        <p>Intelligent AI routing for optimal question generation</p>
      </header>

      <div className="tab-navigation">
        <button 
          className={activeTab === 'generate' ? 'active' : ''}
          onClick={() => setActiveTab('generate')}
        >
          Generate Questions
        </button>
        <button 
          className={activeTab === 'metrics' ? 'active' : ''}
          onClick={() => setActiveTab('metrics')}
        >
          Performance Metrics
        </button>
      </div>

      <div className="main-content">
        {activeTab === 'generate' && (
          <div className="generation-section">
            <GenerationForm onGenerate={handleGenerate} loading={loading} profiles={profiles} />
            
            {error && (
              <div className="error-message">
                <strong>Error:</strong> {error}
              </div>
            )}

            {loading && (
              <div className="loading-indicator">
                <div className="spinner"></div>
                <p>Generating question with optimal AI model...</p>
              </div>
            )}

            {generatedQuestion && !loading && (
              <QuestionDisplay question={generatedQuestion} />
            )}
          </div>
        )}

        {activeTab === 'metrics' && (
          <MetricsDashboard apiBaseUrl={API_BASE_URL} profiles={profiles} />
        )}
      </div>
    </div>
  );
}

export default App;
