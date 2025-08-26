import { render, screen } from '@testing-library/react';
import App from './App';

test('renders dashboard title', () => {
  render(<App />);
  const titleElement = screen.getByText(/AI Quiz Platform - Logging & Monitoring/i);
  expect(titleElement).toBeInTheDocument();
});

test('renders metrics cards', () => {
  render(<App />);
  const totalLogsCard = screen.getByText(/Total Logs Today/i);
  expect(totalLogsCard).toBeInTheDocument();
});
