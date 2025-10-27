import React, { createContext, useContext, useReducer } from 'react'

const QuizContext = createContext()

const quizReducer = (state, action) => {
  switch (action.type) {
    case 'SET_QUIZZES':
      return { ...state, quizzes: action.payload }
    case 'ADD_QUIZ':
      return { ...state, quizzes: [action.payload, ...state.quizzes] }
    case 'UPDATE_QUIZ':
      return {
        ...state,
        quizzes: state.quizzes.map(quiz =>
          quiz.id === action.payload.id ? action.payload : quiz
        )
      }
    case 'DELETE_QUIZ':
      return {
        ...state,
        quizzes: state.quizzes.filter(quiz => quiz.id !== action.payload)
      }
    case 'BULK_DELETE':
      return {
        ...state,
        quizzes: state.quizzes.filter(quiz => !action.payload.includes(quiz.id))
      }
    case 'SET_SELECTED':
      return { ...state, selectedQuizzes: action.payload }
    case 'SET_SEARCH':
      return { ...state, searchTerm: action.payload }
    case 'SET_FILTERS':
      return { ...state, filters: action.payload }
    default:
      return state
  }
}

const initialState = {
  quizzes: [],
  selectedQuizzes: [],
  searchTerm: '',
  filters: {
    tags: [],
    sortBy: 'created_at',
    sortOrder: 'desc'
  }
}

export const useQuiz = () => {
  const context = useContext(QuizContext)
  if (!context) {
    throw new Error('useQuiz must be used within a QuizProvider')
  }
  return context
}

export const QuizProvider = ({ children }) => {
  const [state, dispatch] = useReducer(quizReducer, initialState)

  const value = {
    ...state,
    dispatch
  }

  return (
    <QuizContext.Provider value={value}>
      {children}
    </QuizContext.Provider>
  )
}
