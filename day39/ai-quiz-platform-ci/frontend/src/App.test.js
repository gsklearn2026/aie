import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import App from './App';

// Mock axios
jest.mock('axios');
const mockedAxios = axios;

describe('App Component', () => {
  beforeEach(() => {
    mockedAxios.get.mockClear();
    mockedAxios.post.mockClear();
  });

  test('renders AI Quiz Platform heading', () => {
    render(<App />);
    const linkElement = screen.getByText(/AI Quiz Platform/i);
    expect(linkElement).toBeInTheDocument();
  });

  test('displays health status', async () => {
    mockedAxios.get.mockResolvedValueOnce({ data: { status: 'healthy' } });
    
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText(/healthy/i)).toBeInTheDocument();
    });
  });

  test('handles quiz generation', async () => {
    mockedAxios.get.mockResolvedValueOnce({ data: { status: 'healthy' } });
    mockedAxios.post.mockResolvedValueOnce({
      data: {
        topic: 'Python',
        difficulty: 'medium',
        status: 'generated'
      }
    });
    
    render(<App />);
    
    const topicInput = screen.getByPlaceholderText(/Enter quiz topic/i);
    const generateButton = screen.getByText(/Generate Quiz/i);
    
    fireEvent.change(topicInput, { target: { value: 'Python' } });
    fireEvent.click(generateButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Quiz Generated!/i)).toBeInTheDocument();
    });
  });

  test('disables button when no topic entered', () => {
    render(<App />);
    
    const generateButton = screen.getByText(/Generate Quiz/i);
    expect(generateButton).toBeDisabled();
  });
});
