import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Dashboard } from './components/Dashboard'
import { QuizGenerator } from './components/quiz/QuizGenerator'
import { IntegrationStatus } from './components/common/IntegrationStatus'
import './App.css'

function App() {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="app">
        <header className="app-header">
          <h1>Quiz Platform - API Integration Layer</h1>
          <IntegrationStatus />
        </header>
        
        <main className="app-main">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/quiz" element={<QuizGenerator />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
