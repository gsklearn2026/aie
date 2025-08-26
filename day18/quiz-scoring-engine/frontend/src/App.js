import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import Dashboard from './components/Dashboard';
import ScoringDemo from './components/ScoringDemo';
import UserMetrics from './components/UserMetrics';
import './App.css';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="App min-h-screen bg-gray-50">
        <Router>
          <nav className="bg-white shadow-sm border-b">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex items-center">
                  <h1 className="text-xl font-bold text-gray-900">
                    Quiz Scoring Engine
                  </h1>
                </div>
                <div className="flex items-center space-x-4">
                  <a href="/" className="text-gray-600 hover:text-gray-900">Dashboard</a>
                  <a href="/demo" className="text-gray-600 hover:text-gray-900">Demo</a>
                  <a href="/metrics" className="text-gray-600 hover:text-gray-900">Metrics</a>
                </div>
              </div>
            </div>
          </nav>
          
          <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/demo" element={<ScoringDemo />} />
              <Route path="/metrics" element={<UserMetrics />} />
            </Routes>
          </main>
        </Router>
      </div>
    </QueryClientProvider>
  );
}

export default App;
