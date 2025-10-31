import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import BackupStatus from './components/BackupStatus';
import RecoveryConsole from './components/RecoveryConsole';
import Metrics from './components/Metrics';
import './App.css';

function App() {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="App">
        <header className="app-header">
          <h1>Quiz Platform - Backup & Recovery Console</h1>
          <nav className="main-nav">
            <a href="/">Dashboard</a>
            <a href="/backups">Backups</a>
            <a href="/recovery">Recovery</a>
            <a href="/metrics">Metrics</a>
          </nav>
        </header>
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/backups" element={<BackupStatus />} />
            <Route path="/recovery" element={<RecoveryConsole />} />
            <Route path="/metrics" element={<Metrics />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
