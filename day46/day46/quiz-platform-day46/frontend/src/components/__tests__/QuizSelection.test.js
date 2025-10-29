import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import QuizSelection from '../../pages/QuizSelection';

test('renders quiz selection page', () => {
  render(
    <BrowserRouter>
      <QuizSelection />
    </BrowserRouter>
  );
  
  expect(screen.getByText(/Choose Your Quiz Challenge/i)).toBeInTheDocument();
  expect(screen.getByText(/AI Engineering Fundamentals/i)).toBeInTheDocument();
});
