import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SecurityDashboard from './components/security/SecurityDashboard';
import AuditRunner from './components/security/AuditRunner';
import VulnerabilityScanner from './components/security/VulnerabilityScanner';
import Navigation from './components/common/Navigation';
import './App.css';

function App() {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="App">
        <Navigation />
        <main className="min-h-screen bg-gray-50">
          <Routes>
            <Route path="/" element={<SecurityDashboard />} />
            <Route path="/audit" element={<AuditRunner />} />
            <Route path="/scanner" element={<VulnerabilityScanner />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
