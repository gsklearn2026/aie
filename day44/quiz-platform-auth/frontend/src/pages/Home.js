import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Home = () => {
  const { isAuthenticated, user } = useAuth();

  return (
    <div className="home-container">
      <div className="hero-section">
        <h1>AI Quiz Platform</h1>
        <p>Learn and test your knowledge with AI-powered quizzes</p>
        
        {isAuthenticated ? (
          <div className="authenticated-home">
            <h2>Welcome back, {user?.full_name || user?.username}!</h2>
            <Link to="/dashboard" className="cta-button">
              Go to Dashboard
            </Link>
          </div>
        ) : (
          <div className="auth-buttons">
            <Link to="/login" className="cta-button primary">
              Sign In
            </Link>
            <Link to="/register" className="cta-button secondary">
              Create Account
            </Link>
          </div>
        )}
      </div>
      
      <div className="features-section">
        <h2>Platform Features</h2>
        <div className="features-grid">
          <div className="feature-card">
            <h3>🔐 Secure Authentication</h3>
            <p>JWT-based authentication with role management</p>
          </div>
          <div className="feature-card">
            <h3>🤖 AI-Powered Quizzes</h3>
            <p>Dynamic quiz generation using Google's Gemini AI</p>
          </div>
          <div className="feature-card">
            <h3>📊 Progress Tracking</h3>
            <p>Monitor your learning progress and achievements</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
