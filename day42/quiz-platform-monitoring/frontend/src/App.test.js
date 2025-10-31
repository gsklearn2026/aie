import { render, screen } from '@testing-library/react';
import App from './App';

// Mock fetch for tests
global.fetch = jest.fn();

beforeEach(() => {
  fetch.mockResolvedValue({
    ok: true,
    json: async () => ({
      activeUsers: 10,
      questionsAnswered: 50,
      avgResponseTime: 0.15,
      errorRate: 2.5,
      systemHealth: {
        cpu: 45.2,
        memory: 67.8,
        status: 'healthy'
      }
    })
  });
});

test('renders monitoring dashboard title', async () => {
  render(<App />);
  const titleElement = await screen.findByText(/Quiz Platform Monitoring Dashboard/i);
  expect(titleElement).toBeInTheDocument();
});

test('renders simulate buttons', async () => {
  render(<App />);
  const loadButton = await screen.findByText(/Simulate Load/i);
  const errorButton = await screen.findByText(/Test Alerting/i);
  expect(loadButton).toBeInTheDocument();
  expect(errorButton).toBeInTheDocument();
});
