import React from 'react';
import { Clock, CheckCircle, XCircle, AlertCircle, RefreshCw, Loader } from 'lucide-react';

const ExportProgress = ({ exports, onRefresh }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'processing':
        return <Loader className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'queued':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      case 'queued':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getProgressBarColor = (status) => {
    switch (status) {
      case 'processing':
        return 'bg-blue-600';
      case 'queued':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-400';
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900">Export Progress</h2>
        <button
          onClick={onRefresh}
          className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      {exports.length === 0 ? (
        <div className="text-center py-8">
          <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-4" />
          <p className="text-gray-500">No active exports</p>
          <p className="text-sm text-gray-400">All exports are completed or there are no exports in progress</p>
        </div>
      ) : (
        <div className="space-y-4">
          {exports.map((exportItem) => (
            <div key={exportItem.job_id} className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(exportItem.status)}
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">
                      Quiz Export - {exportItem.export_format?.toUpperCase()}
                    </h3>
                    <p className="text-sm text-gray-500">
                      Started: {formatDate(exportItem.created_at)}
                    </p>
                  </div>
                </div>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(exportItem.status)}`}>
                  {exportItem.status}
                </span>
              </div>

              {/* Progress Bar */}
              <div className="mb-4">
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>Progress</span>
                  <span>{exportItem.progress || 0}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-300 ${getProgressBarColor(exportItem.status)}`}
                    style={{ width: `${exportItem.progress || 0}%` }}
                  ></div>
                </div>
              </div>

              {/* Export Details */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-700">Job ID:</span>
                  <p className="text-gray-600 font-mono text-xs">{exportItem.job_id}</p>
                </div>
                {exportItem.total_records && (
                  <div>
                    <span className="font-medium text-gray-700">Total Records:</span>
                    <p className="text-gray-600">{exportItem.total_records}</p>
                  </div>
                )}
                {exportItem.processed_records && (
                  <div>
                    <span className="font-medium text-gray-700">Processed:</span>
                    <p className="text-gray-600">{exportItem.processed_records}</p>
                  </div>
                )}
              </div>

              {/* Error Message */}
              {exportItem.error_message && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-sm text-red-800">
                    <strong>Error:</strong> {exportItem.error_message}
                  </p>
                </div>
              )}

              {/* Estimated Time */}
              {exportItem.status === 'processing' && exportItem.progress > 0 && (
                <div className="mt-4 text-sm text-gray-600">
                  <p>Estimated time remaining: Calculating...</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ExportProgress;

