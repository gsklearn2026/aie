import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ExportDashboard from './components/ExportDashboard/ExportDashboard';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="bg-blue-600 text-white p-4">
          <h1 className="text-2xl font-bold">AI Quiz Platform - Export Service</h1>
        </header>
        <main className="min-h-screen bg-gray-50">
          <Routes>
            <Route path="/" element={<ExportDashboard />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
