import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from './Dashboard';

// Mock the API module
jest.mock('../../services/api', () => ({
  quizAPI: {
    getQuiz: jest.fn(),
    getUserProgress: jest.fn(),
    getLeaderboard: jest.fn(),
    invalidateQuizCache: jest.fn(),
    getAIExplanation: jest.fn(),
  }
}));

const MockedDashboard = () => (
  <BrowserRouter>
    <Dashboard />
  </BrowserRouter>
);

test('renders dashboard components', async () => {
  const { quizAPI } = require('../../services/api');
  
  // Mock API responses
  quizAPI.getQuiz.mockResolvedValue({
    data: { id: 'test', title: 'Test Quiz', questions: [] }
  });
  quizAPI.getUserProgress.mockResolvedValue({
    data: { score: 85, completed: true, time_spent: 300 }
  });
  quizAPI.getLeaderboard.mockResolvedValue({
    data: { leaderboard: [] }
  });

  render(<MockedDashboard />);
  
  // Check for key elements that actually exist in the component
  expect(screen.getByText('Response Time')).toBeInTheDocument();
  expect(screen.getByText('Cache Benefits')).toBeInTheDocument();
  
  // Wait for data loading
  await waitFor(() => {
    expect(screen.getByText('🔄 Load Quiz Data')).toBeInTheDocument();
  });
});

test('displays performance metrics', async () => {
  const { quizAPI } = require('../../services/api');
  
  // Mock API responses
  quizAPI.getQuiz.mockResolvedValue({
    data: { id: 'test', title: 'Test Quiz', questions: [] }
  });
  quizAPI.getUserProgress.mockResolvedValue({
    data: { score: 85, completed: true, time_spent: 300 }
  });
  quizAPI.getLeaderboard.mockResolvedValue({
    data: { leaderboard: [] }
  });

  render(<MockedDashboard />);
  
  // Wait for component to load and render
  await waitFor(() => {
    expect(screen.getByText('Response Time')).toBeInTheDocument();
    expect(screen.getByText('Cache Benefits')).toBeInTheDocument();
    expect(screen.getByText(/Average of last \d+ requests/)).toBeInTheDocument();
  });
});


