import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import UserAnalytics from './components/UserAnalytics';
import TopicAnalytics from './components/TopicAnalytics';
import Navigation from './components/Navigation';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/user/:userId" element={<UserAnalytics />} />
            <Route path="/topic/:topicId" element={<TopicAnalytics />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
