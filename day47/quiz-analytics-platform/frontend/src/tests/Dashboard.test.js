import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../components/dashboard/Dashboard';
import * as api from '../services/api';

// Mock the API
jest.mock('../services/api');

const MockedDashboard = () => (
  <BrowserRouter>
    <Dashboard />
  </BrowserRouter>
);

test('renders dashboard with loading state', () => {
  api.fetchDashboardOverview.mockResolvedValue({ data: { data: {} } });
  api.fetchPerformanceTrends.mockResolvedValue({ data: { data: [] } });
  api.fetchScoreDistribution.mockResolvedValue({ data: { data: [] } });
  
  render(<MockedDashboard />);
  expect(screen.getByRole('progressbar')).toBeInTheDocument();
});

test('renders dashboard content after loading', async () => {
  const mockOverview = {
    total_users: 100,
    total_quizzes: 50,
    total_sessions: 500,
    completion_rate: 85.5
  };
  
  api.fetchDashboardOverview.mockResolvedValue({ data: { data: mockOverview } });
  api.fetchPerformanceTrends.mockResolvedValue({ data: { data: [] } });
  api.fetchScoreDistribution.mockResolvedValue({ data: { data: [] } });
  
  render(<MockedDashboard />);
  
  await waitFor(() => {
    expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument();
    expect(screen.getByText('50')).toBeInTheDocument();
  });
});
