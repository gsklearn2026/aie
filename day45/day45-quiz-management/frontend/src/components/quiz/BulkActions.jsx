import React from 'react'
import { Trash2, Download, Archive, Copy } from 'lucide-react'

const BulkActions = ({ selectedCount, onBulkDelete }) => {
  const handleExport = () => {
    // TODO: Implement bulk export functionality
    console.log('Exporting selected quizzes...')
  }

  const handleDuplicate = () => {
    // TODO: Implement bulk duplicate functionality
    console.log('Duplicating selected quizzes...')
  }

  const handleArchive = () => {
    // TODO: Implement bulk archive functionality
    console.log('Archiving selected quizzes...')
  }

  return (
    <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <span className="text-sm font-medium text-primary-700">
            {selectedCount} quiz{selectedCount > 1 ? 'es' : ''} selected
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={handleExport}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <Download className="h-4 w-4 mr-1" />
            Export
          </button>
          
          <button
            onClick={handleDuplicate}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <Copy className="h-4 w-4 mr-1" />
            Duplicate
          </button>
          
          <button
            onClick={handleArchive}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <Archive className="h-4 w-4 mr-1" />
            Archive
          </button>
          
          <button
            onClick={onBulkDelete}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            <Trash2 className="h-4 w-4 mr-1" />
            Delete
          </button>
        </div>
      </div>
    </div>
  )
}

export default BulkActions
