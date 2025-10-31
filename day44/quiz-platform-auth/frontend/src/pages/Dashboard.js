import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { authService } from '../services/authService';
import { toast } from 'react-hot-toast';

const Dashboard = () => {
  const { user } = useAuth();
  const [protectedData, setProtectedData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const testProtectedEndpoint = async () => {
    setIsLoading(true);
    try {
      const response = await authService.testProtectedEndpoint();
      setProtectedData(response);
      toast.success('Protected endpoint accessed successfully!');
    } catch (error) {
      toast.error('Failed to access protected endpoint');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Welcome to your Dashboard</h1>
        <p>Hello, {user?.full_name || user?.username}!</p>
      </div>

      <div className="dashboard-content">
        <div className="user-info-card">
          <h3>User Information</h3>
          <div className="user-details">
            <p><strong>Username:</strong> {user?.username}</p>
            <p><strong>Email:</strong> {user?.email}</p>
            <p><strong>Role:</strong> {user?.role}</p>
            <p><strong>Account Status:</strong> {user?.is_active ? 'Active' : 'Inactive'}</p>
          </div>
        </div>

        <div className="test-card">
          <h3>Authentication Test</h3>
          <p>Test the protected endpoint to verify authentication is working:</p>
          <button 
            onClick={testProtectedEndpoint}
            disabled={isLoading}
            className="test-button"
          >
            {isLoading ? 'Testing...' : 'Test Protected Endpoint'}
          </button>
          
          {protectedData && (
            <div className="test-result">
              <h4>Protected Data Response:</h4>
              <pre>{JSON.stringify(protectedData, null, 2)}</pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
