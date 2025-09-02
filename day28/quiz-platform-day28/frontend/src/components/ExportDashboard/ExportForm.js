import React, { useState } from 'react';
import { Download, Calendar, Filter, Settings } from 'lucide-react';

const ExportForm = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    format: 'csv',
    includeAiInsights: true,
    filters: {
      subjectArea: '',
      difficultyLevel: '',
      userId: ''
    },
    dateRange: {
      startDate: '',
      endDate: ''
    }
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await onSubmit(formData);
      // Reset form
      setFormData({
        format: 'csv',
        includeAiInsights: true,
        filters: { subjectArea: '', difficultyLevel: '', userId: '' },
        dateRange: { startDate: '', endDate: '' }
      });
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const updateFilter = (key, value) => {
    setFormData(prev => ({
      ...prev,
      filters: { ...prev.filters, [key]: value }
    }));
  };

  const updateDateRange = (key, value) => {
    setFormData(prev => ({
      ...prev,
      dateRange: { ...prev.dateRange, [key]: value }
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Export Format */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Download className="w-4 h-4 inline mr-1" />
            Export Format
          </label>
          <select
            value={formData.format}
            onChange={(e) => setFormData(prev => ({ ...prev, format: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="csv">CSV (Compressed)</option>
            <option value="json">JSON (Compressed)</option>
            <option value="excel">Excel Spreadsheet</option>
            <option value="xml">XML Document</option>
            <option value="pdf">PDF Report</option>
          </select>
        </div>

        {/* AI Insights Toggle */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Settings className="w-4 h-4 inline mr-1" />
            Include AI Insights
          </label>
          <div className="flex items-center">
            <input
              type="checkbox"
              checked={formData.includeAiInsights}
              onChange={(e) => setFormData(prev => ({ ...prev, includeAiInsights: e.target.checked }))}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span className="ml-2 text-sm text-gray-600">
              Include AI-generated performance insights
            </span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          <Filter className="w-4 h-4 inline mr-1" />
          Filters
        </label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs text-gray-600 mb-1">Subject Area</label>
            <select
              value={formData.filters.subjectArea}
              onChange={(e) => updateFilter('subjectArea', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Subjects</option>
              <option value="Mathematics">Mathematics</option>
              <option value="Science">Science</option>
              <option value="History">History</option>
              <option value="Literature">Literature</option>
              <option value="Geography">Geography</option>
            </select>
          </div>

          <div>
            <label className="block text-xs text-gray-600 mb-1">Difficulty Level</label>
            <select
              value={formData.filters.difficultyLevel}
              onChange={(e) => updateFilter('difficultyLevel', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Levels</option>
              <option value="Easy">Easy</option>
              <option value="Medium">Medium</option>
              <option value="Hard">Hard</option>
            </select>
          </div>

          <div>
            <label className="block text-xs text-gray-600 mb-1">User ID (Optional)</label>
            <input
              type="text"
              value={formData.filters.userId}
              onChange={(e) => updateFilter('userId', e.target.value)}
              placeholder="e.g., user_123"
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Date Range */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          <Calendar className="w-4 h-4 inline mr-1" />
          Date Range
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-gray-600 mb-1">Start Date</label>
            <input
              type="date"
              value={formData.dateRange.startDate}
              onChange={(e) => updateDateRange('startDate', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs text-gray-600 mb-1">End Date</label>
            <input
              type="date"
              value={formData.dateRange.endDate}
              onChange={(e) => updateDateRange('endDate', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Submit Button */}
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Creating Export...
            </>
          ) : (
            <>
              <Download className="w-4 h-4 mr-2" />
              Create Export
            </>
          )}
        </button>
      </div>
    </form>
  );
};

export default ExportForm;
