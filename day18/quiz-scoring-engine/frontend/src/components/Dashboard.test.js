import React from 'react';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from './Dashboard';

// Mock the API
jest.mock('../services/api', () => ({
  api: {
    getStrategies: jest.fn(() => Promise.resolve({
      strategies: [
        { name: 'basic', description: 'Basic scoring' },
        { name: 'weighted', description: 'Weighted scoring' }
      ]
    }))
  }
}));

const renderWithProviders = (component) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

test('renders dashboard title', () => {
  renderWithProviders(<Dashboard />);
  const titleElement = screen.getByText(/Quiz Scoring Engine Dashboard/i);
  expect(titleElement).toBeInTheDocument();
});

test('renders stats cards', () => {
  renderWithProviders(<Dashboard />);
  expect(screen.getByText(/Total Scores/i)).toBeInTheDocument();
  expect(screen.getByText(/Average Score/i)).toBeInTheDocument();
  expect(screen.getByText(/Active Strategies/i)).toBeInTheDocument();
});
