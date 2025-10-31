import React from 'react'
import { useQuiz } from '../../context/QuizContext'
import { X, Calendar, Tag, SortAsc, SortDesc } from 'lucide-react'

const QuizFilters = () => {
  const { filters, dispatch } = useQuiz()

  const handleTagFilter = (tag) => {
    const newTags = filters.tags.includes(tag)
      ? filters.tags.filter(t => t !== tag)
      : [...filters.tags, tag]
    
    dispatch({
      type: 'SET_FILTERS',
      payload: { ...filters, tags: newTags }
    })
  }

  const handleSortChange = (sortBy) => {
    const newSortOrder = filters.sortBy === sortBy && filters.sortOrder === 'desc' ? 'asc' : 'desc'
    dispatch({
      type: 'SET_FILTERS',
      payload: { ...filters, sortBy, sortOrder: newSortOrder }
    })
  }

  const clearFilters = () => {
    dispatch({
      type: 'SET_FILTERS',
      payload: { tags: [], sortBy: 'created_at', sortOrder: 'desc' }
    })
  }

  const popularTags = ['Education', 'Science', 'Math', 'History', 'Programming', 'Languages']

  return (
    <div className="card space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">Filters</h3>
        <button
          onClick={clearFilters}
          className="text-sm text-gray-500 hover:text-gray-700 flex items-center space-x-1"
        >
          <X className="h-4 w-4" />
          <span>Clear all</span>
        </button>
      </div>

      {/* Sort Options */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 mb-2">Sort by</h4>
        <div className="flex flex-wrap gap-2">
          {[
            { key: 'created_at', label: 'Date Created' },
            { key: 'updated_at', label: 'Last Modified' },
            { key: 'title', label: 'Title' },
            { key: 'view_count', label: 'Views' }
          ].map(({ key, label }) => (
            <button
              key={key}
              onClick={() => handleSortChange(key)}
              className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm transition-colors ${
                filters.sortBy === key
                  ? 'bg-primary-100 text-primary-700 border-primary-200'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <span>{label}</span>
              {filters.sortBy === key && (
                filters.sortOrder === 'desc' 
                  ? <SortDesc className="h-4 w-4" />
                  : <SortAsc className="h-4 w-4" />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Tag Filters */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 mb-2">Filter by tags</h4>
        <div className="flex flex-wrap gap-2">
          {popularTags.map((tag) => (
            <button
              key={tag}
              onClick={() => handleTagFilter(tag)}
              className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm transition-colors ${
                filters.tags.includes(tag)
                  ? 'bg-primary-100 text-primary-700 border-primary-200'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Tag className="h-3 w-3" />
              <span>{tag}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Active Filters */}
      {(filters.tags.length > 0) && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Active filters</h4>
          <div className="flex flex-wrap gap-2">
            {filters.tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
              >
                {tag}
                <button
                  onClick={() => handleTagFilter(tag)}
                  className="ml-1 hover:text-primary-600"
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default QuizFilters
