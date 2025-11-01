import React from 'react';
import ErrorBoundary from './components/common/ErrorBoundary';
import QuizContainer from './components/quiz/QuizContainer';
import './App.css';

const QuizErrorFallback = ({ onRetry }) => (
  <div className="quiz-error-fallback">
    <h2>Quiz Temporarily Unavailable</h2>
    <p>We're having trouble loading your quiz. This might be due to:</p>
    <ul>
      <li>Temporary server issues</li>
      <li>Network connectivity problems</li>
      <li>High system load</li>
    </ul>
    <button onClick={onRetry} className="retry-button-large">
      Reload Quiz Platform
    </button>
  </div>
);

function App() {
  return (
    <div className="App">
      <header className="app-header">
        <h1>AI Quiz Platform</h1>
        <p>Test your knowledge with AI-generated questions</p>
      </header>
      
      <main className="app-main">
        <ErrorBoundary fallback={QuizErrorFallback}>
          <QuizContainer topic="JavaScript" difficulty="medium" />
        </ErrorBoundary>
      </main>
    </div>
  );
}

export default App;
