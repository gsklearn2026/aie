import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuiz } from '../../context/QuizContext'
import { quizService } from '../../services/api'
import { toast } from 'react-hot-toast'
import { Edit, Trash2, Eye, Calendar, Tag } from 'lucide-react'

const QuizList = ({ quizzes, onRefetch }) => {
  const navigate = useNavigate()
  const { selectedQuizzes, dispatch } = useQuiz()

  const handleSelectQuiz = (quizId, isSelected) => {
    if (isSelected) {
      dispatch({ 
        type: 'SET_SELECTED', 
        payload: [...selectedQuizzes, quizId] 
      })
    } else {
      dispatch({ 
        type: 'SET_SELECTED', 
        payload: selectedQuizzes.filter(id => id !== quizId) 
      })
    }
  }

  const handleSelectAll = (isSelected) => {
    if (isSelected) {
      dispatch({ 
        type: 'SET_SELECTED', 
        payload: quizzes.map(q => q.id) 
      })
    } else {
      dispatch({ type: 'SET_SELECTED', payload: [] })
    }
  }

  const handleDeleteQuiz = async (quizId) => {
    if (window.confirm('Are you sure you want to delete this quiz?')) {
      try {
        await quizService.deleteQuiz(quizId)
        dispatch({ type: 'DELETE_QUIZ', payload: quizId })
        toast.success('Quiz deleted successfully')
        onRefetch()
      } catch (error) {
        toast.error('Failed to delete quiz')
      }
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  return (
    <div className="space-y-4">
      {/* Header with Select All */}
      <div className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
        <div className="flex items-center space-x-3">
          <input
            type="checkbox"
            checked={quizzes.length > 0 && selectedQuizzes.length === quizzes.length}
            onChange={(e) => handleSelectAll(e.target.checked)}
            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="text-sm font-medium text-gray-700">
            {selectedQuizzes.length > 0 
              ? `${selectedQuizzes.length} selected` 
              : `${quizzes.length} quizzes`
            }
          </span>
        </div>
        
        <div className="text-sm text-gray-500">
          Last updated: {new Date().toLocaleDateString()}
        </div>
      </div>

      {/* Quiz Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {quizzes.map((quiz) => (
          <div
            key={quiz.id}
            className={`card transition-all duration-200 hover:shadow-md ${
              selectedQuizzes.includes(quiz.id) ? 'ring-2 ring-primary-500' : ''
            }`}
          >
            {/* Quiz Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-3 flex-1">
                <input
                  type="checkbox"
                  checked={selectedQuizzes.includes(quiz.id)}
                  onChange={(e) => handleSelectQuiz(quiz.id, e.target.checked)}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-semibold text-gray-900 truncate">
                    {quiz.title}
                  </h3>
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {quiz.description}
                  </p>
                </div>
              </div>
            </div>

            {/* Quiz Stats */}
            <div className="flex items-center space-x-4 text-sm text-gray-500 mb-3">
              <div className="flex items-center space-x-1">
                <Calendar className="h-4 w-4" />
                <span>{formatDate(quiz.created_at)}</span>
              </div>
              <div className="flex items-center space-x-1">
                <Eye className="h-4 w-4" />
                <span>{quiz.view_count} views</span>
              </div>
            </div>

            {/* Quiz Questions Count */}
            <div className="mb-3">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                {quiz.questions?.length || 0} questions
              </span>
            </div>

            {/* Tags */}
            {quiz.tags && quiz.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mb-3">
                {quiz.tags.slice(0, 3).map((tag, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-700"
                  >
                    <Tag className="h-3 w-3 mr-1" />
                    {tag}
                  </span>
                ))}
                {quiz.tags.length > 3 && (
                  <span className="text-xs text-gray-500">
                    +{quiz.tags.length - 3} more
                  </span>
                )}
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex items-center justify-between pt-3 border-t border-gray-200">
              <button
                onClick={() => navigate(`/quiz/edit/${quiz.id}`)}
                className="flex items-center space-x-1 px-3 py-1.5 text-sm text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-md transition-colors"
              >
                <Edit className="h-4 w-4" />
                <span>Edit</span>
              </button>
              
              <button
                onClick={() => handleDeleteQuiz(quiz.id)}
                className="flex items-center space-x-1 px-3 py-1.5 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors"
              >
                <Trash2 className="h-4 w-4" />
                <span>Delete</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default QuizList
