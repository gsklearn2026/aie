import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import QuizList from '../components/quiz/QuizList'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
})

const Wrapper = ({ children }) => (
  <QueryClientProvider client={queryClient}>
    <BrowserRouter>
      {children}
    </BrowserRouter>
  </QueryClientProvider>
)

test('renders quiz list', () => {
  const mockQuizzes = [
    {
      id: 1,
      title: 'Test Quiz',
      description: 'A test quiz',
      questions: [],
      created_at: '2024-01-01',
      view_count: 5
    }
  ]

  render(
    <QuizList quizzes={mockQuizzes} onRefetch={() => {}} />,
    { wrapper: Wrapper }
  )

  expect(screen.getByText('Test Quiz')).toBeInTheDocument()
})
