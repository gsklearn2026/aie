import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import QuizSelection from './pages/QuizSelection';
import QuizTaking from './pages/QuizTaking';
import QuizResults from './pages/QuizResults';
import Layout from './components/layout/Layout';
import './App.css';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<QuizSelection />} />
          <Route path="/quiz/:sessionId" element={<QuizTaking />} />
          <Route path="/results/:sessionId" element={<QuizResults />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
