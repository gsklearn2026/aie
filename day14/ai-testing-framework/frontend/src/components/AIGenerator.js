import React, { useState } from 'react';

const AIGenerator = () => {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [validationResult, setValidationResult] = useState(null);

  const generateText = async () => {
    if (!prompt.trim()) return;
    
    setIsLoading(true);
    setResponse(null);
    setValidationResult(null);
    
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      
      const data = await response.json();
      setResponse(data);
      
      // Auto-validate the response
      await validateContent(data.content);
      
    } catch (error) {
      console.error('Generation failed:', error);
      setResponse({ error: error.message });
    } finally {
      setIsLoading(false);
    }
  };

  const validateContent = async (content) => {
    try {
      const response = await fetch('/api/validate/content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          content,
          criteria: {
            min_words: 10,
            max_words: 500,
            required_keywords: prompt.split(' ').slice(0, 3), // Use first 3 words as keywords
            min_score: 0.6
          }
        })
      });
      
      const validation = await response.json();
      setValidationResult(validation);
      
    } catch (error) {
      console.error('Validation failed:', error);
    }
  };

  return (
    <div className="ai-generator">
      <div className="generator-form">
        <h2>AI Text Generator</h2>
        
        <div className="form-group">
          <label htmlFor="prompt">Enter your prompt:</label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ask the AI to generate content..."
            rows={4}
            disabled={isLoading}
          />
        </div>
        
        <button 
          onClick={generateText}
          disabled={!prompt.trim() || isLoading}
          className="generate-button"
        >
          {isLoading ? 'Generating...' : 'Generate Text'}
        </button>
      </div>

      {response && (
        <div className="response-section">
          <h3>Generated Response</h3>
          
          {response.error ? (
            <div className="error-message">
              Error: {response.error}
            </div>
          ) : (
            <>
              <div className="response-content">
                {response.content}
              </div>
              
              <div className="response-metadata">
                <div className="metadata-grid">
                  <div className="metadata-item">
                    <span className="label">Provider:</span>
                    <span className="value">{response.provider}</span>
                  </div>
                  <div className="metadata-item">
                    <span className="label">Model:</span>
                    <span className="value">{response.model}</span>
                  </div>
                  <div className="metadata-item">
                    <span className="label">Tokens Used:</span>
                    <span className="value">{response.tokens_used}</span>
                  </div>
                  <div className="metadata-item">
                    <span className="label">Response Time:</span>
                    <span className="value">{response.response_time}ms</span>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {validationResult && (
        <div className="validation-section">
          <h3>Content Validation</h3>
          
          <div className={`validation-status ${validationResult.is_valid ? 'valid' : 'invalid'}`}>
            <span className="status-icon">
              {validationResult.is_valid ? '✅' : '❌'}
            </span>
            <span className="status-text">
              {validationResult.is_valid ? 'Content is valid' : 'Content validation failed'}
            </span>
            <span className="score">
              Score: {Math.round(validationResult.score * 100)}%
            </span>
          </div>
          
          <div className="validation-details">
            <div className="details-grid">
              <div className="detail-item">
                <span className="label">Word Count:</span>
                <span className="value">{validationResult.details.word_count}</span>
              </div>
              <div className="detail-item">
                <span className="label">Keyword Coverage:</span>
                <span className="value">
                  {Math.round(validationResult.details.keyword_coverage * 100)}%
                </span>
              </div>
              <div className="detail-item">
                <span className="label">Coherence Score:</span>
                <span className="value">
                  {Math.round(validationResult.details.coherence_score * 100)}%
                </span>
              </div>
            </div>
            
            {validationResult.errors && validationResult.errors.length > 0 && (
              <div className="validation-errors">
                <h4>Validation Errors:</h4>
                <ul>
                  {validationResult.errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AIGenerator;
