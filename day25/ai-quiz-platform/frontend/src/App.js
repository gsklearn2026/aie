import React from 'react';
import { Toaster } from 'react-hot-toast';
import QuizDashboard from './components/QuizDashboard';
import ErrorBoundary from './components/ErrorBoundary';
import './App.css';

function App() {
  return (
    <ErrorBoundary>
      <div className="App">
        <QuizDashboard />
        <Toaster position="top-right" />
      </div>
    </ErrorBoundary>
  );
}

export default App;
