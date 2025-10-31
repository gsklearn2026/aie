import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from 'react-query'
import { toast } from 'react-hot-toast'
import { useQuiz } from '../context/QuizContext'
import { quizService } from '../services/api'
import QuizList from '../components/quiz/QuizList'
import QuizFilters from '../components/quiz/QuizFilters'
import BulkActions from '../components/quiz/BulkActions'
import { Search, Filter } from 'lucide-react'

const Dashboard = () => {
  const navigate = useNavigate()
  const { quizzes, searchTerm, filters, selectedQuizzes, dispatch } = useQuiz()
  const [showFilters, setShowFilters] = useState(false)

  const { data, isLoading, refetch } = useQuery(
    ['quizzes', searchTerm, filters],
    () => quizService.getQuizzes({ 
      search: searchTerm,
      tags: filters.tags.join(',')
    }),
    {
      onSuccess: (data) => {
        dispatch({ type: 'SET_QUIZZES', payload: data })
      }
    }
  )

  const handleSearch = (term) => {
    dispatch({ type: 'SET_SEARCH', payload: term })
  }

  const handleBulkDelete = async (ids) => {
    try {
      await quizService.bulkDelete(ids)
      dispatch({ type: 'BULK_DELETE', payload: ids })
      dispatch({ type: 'SET_SELECTED', payload: [] })
      toast.success(`Deleted ${ids.length} quizzes`)
      refetch()
    } catch (error) {
      toast.error('Failed to delete quizzes')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Quiz Dashboard</h1>
          <p className="text-gray-600">Manage your quizzes and track performance</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search quizzes..."
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`btn-secondary flex items-center space-x-2 ${showFilters ? 'bg-primary-100 text-primary-700' : ''}`}
          >
            <Filter className="h-4 w-4" />
            <span>Filters</span>
          </button>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <QuizFilters />
      )}

      {/* Bulk Actions */}
      {selectedQuizzes.length > 0 && (
        <BulkActions 
          selectedCount={selectedQuizzes.length}
          onBulkDelete={() => handleBulkDelete(selectedQuizzes)}
        />
      )}

      {/* Quiz List */}
      <QuizList 
        quizzes={quizzes} 
        onRefetch={refetch}
      />

      {/* Empty State */}
      {quizzes.length === 0 && !searchTerm && (
        <div className="text-center py-12">
          <div className="max-w-md mx-auto">
            <h3 className="text-lg font-medium text-gray-900 mb-2">No quizzes yet</h3>
            <p className="text-gray-600 mb-6">Get started by creating your first quiz</p>
            <button
              onClick={() => navigate('/quiz/create')}
              className="btn-primary"
            >
              Create Your First Quiz
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
