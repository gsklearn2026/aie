import React, { useState, useEffect } from 'react';
import SwaggerUI from 'swagger-ui-react';
import 'swagger-ui-react/swagger-ui.css';
import './App.css';

function App() {
  const [apiSpec, setApiSpec] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:5000/swagger.json')
      .then(response => response.json())
      .then(data => {
        setApiSpec(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error loading API spec:', error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="loading-container">
        <h2>Loading API Documentation...</h2>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Quiz Platform API Documentation</h1>
        <p>Interactive API testing and exploration interface</p>
      </header>
      
      <div className="swagger-container">
        {apiSpec ? (
          <SwaggerUI 
            spec={apiSpec}
            url="http://localhost:5000/swagger.json"
            requestInterceptor={(request) => {
              console.log('API Request:', request);
              // Ensure requests go to the correct port
              if (request.url.startsWith('/api/')) {
                request.url = `http://localhost:5000${request.url}`;
              }
              return request;
            }}
            responseInterceptor={(response) => {
              console.log('API Response:', response);
              return response;
            }}
            docExpansion="list"
            defaultModelsExpandDepth={1}
            defaultModelExpandDepth={1}
            tryItOutEnabled={true}
            supportedSubmitMethods={['get', 'post', 'put', 'delete', 'patch']}
            onComplete={() => {
              // Suppress React strict mode warnings from Swagger UI
              const originalWarn = console.warn;
              console.warn = (message) => {
                if (typeof message === 'string' && 
                    (message.includes('UNSAFE_componentWillReceiveProps') || 
                     message.includes('componentWillReceiveProps'))) {
                  return;
                }
                originalWarn(message);
              };
            }}
          />
        ) : (
          <div className="error-message">
            <h3>Unable to load API specification</h3>
            <p>Please ensure the backend server is running on localhost:5000</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
