import React from 'react';
import { Download, Calendar, FileText, Eye, RefreshCw } from 'lucide-react';
import { format } from 'date-fns';
import { exportService } from '../../services/exportService';

const ExportHistory = ({ exports, onRefresh }) => {
  const handleDownload = async (jobId) => {
    try {
      await exportService.downloadExport(jobId);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Download failed. Please try again.');
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      completed: { bg: 'bg-green-100', text: 'text-green-800', label: 'Completed' },
      processing: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Processing' },
      queued: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Queued' },
      failed: { bg: 'bg-red-100', text: 'text-red-800', label: 'Failed' }
    };

    const config = statusConfig[status] || statusConfig.queued;
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
        {config.label}
      </span>
    );
  };

  const getFormatIcon = (format) => {
    return <FileText className="w-4 h-4" />;
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">Export History</h3>
        <button
          onClick={onRefresh}
          className="flex items-center px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
        >
          <RefreshCw className="w-4 h-4 mr-1" />
          Refresh
        </button>
      </div>

      {exports.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No exports yet</h3>
          <p className="text-gray-600">Create your first export to see it here.</p>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {exports.map((exportJob) => (
              <li key={exportJob.job_id}>
                <div className="px-4 py-4 flex items-center justify-between">
                  <div className="flex items-center min-w-0 flex-1">
                    <div className="flex-shrink-0">
                      {getFormatIcon(exportJob.format)}
                    </div>
                    <div className="ml-4 min-w-0 flex-1">
                      <div className="flex items-center space-x-2">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {exportJob.format.toUpperCase()} Export
                        </p>
                        {getStatusBadge(exportJob.status)}
                      </div>
                      <div className="flex items-center space-x-4 mt-1">
                        <p className="text-sm text-gray-500 flex items-center">
                          <Calendar className="w-3 h-3 mr-1" />
                          {format(new Date(exportJob.created_at), 'MMM dd, yyyy HH:mm')}
                        </p>
                        {exportJob.total_records > 0 && (
                          <p className="text-sm text-gray-500">
                            {exportJob.total_records.toLocaleString()} records
                          </p>
                        )}
                        {exportJob.file_size > 0 && (
                          <p className="text-sm text-gray-500">
                            {formatFileSize(exportJob.file_size)}
                          </p>
                        )}
                      </div>
                      {exportJob.status === 'processing' && (
                        <div className="mt-2">
                          <div className="flex items-center">
                            <div className="flex-1 bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                style={{ width: `${exportJob.progress || 0}%` }}
                              ></div>
                            </div>
                            <span className="ml-2 text-sm text-gray-600">
                              {Math.round(exportJob.progress || 0)}%
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {exportJob.status === 'completed' && (
                      <button
                        onClick={() => handleDownload(exportJob.job_id)}
                        className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      >
                        <Download className="w-4 h-4 mr-1" />
                        Download
                      </button>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ExportHistory;
