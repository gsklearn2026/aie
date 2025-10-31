import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard/Dashboard';
import QuizView from './components/Quiz/QuizView';
import CacheMonitor from './components/Dashboard/CacheMonitor';
import './styles/App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="app-header">
          <h1>🚀 Quiz Platform - Day 22: Caching Demo</h1>
          <nav>
            <a href="/">Dashboard</a>
            <a href="/cache">Cache Monitor</a>
          </nav>
        </header>
        
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/quiz/:quizId" element={<QuizView />} />
            <Route path="/cache" element={<CacheMonitor />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
