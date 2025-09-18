import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    // Simulate login for E2E testing
    navigate('/dashboard');
  };

  return (
    <div className="page">
      <div className="card">
        <h2>Login to Quiz Platform</h2>
        <form onSubmit={handleLogin}>
          <input
            data-testid="email-input"
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            data-testid="password-input"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button data-testid="login-button" type="submit">
            Login
          </button>
        </form>
      </div>
    </div>
  );
}

export default LoginPage;
