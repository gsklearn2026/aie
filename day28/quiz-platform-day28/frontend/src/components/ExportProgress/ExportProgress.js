import React, { useEffect, useState } from 'react';
import { Clock, AlertCircle, CheckCircle, XCircle } from 'lucide-react';

const ExportProgress = ({ exports, onRefresh }) => {
  const [refreshInterval, setRefreshInterval] = useState(null);

  useEffect(() => {
    // Auto-refresh every 2 seconds when there are active jobs
    if (exports.length > 0) {
      const interval = setInterval(onRefresh, 2000);
      setRefreshInterval(interval);
      return () => clearInterval(interval);
    } else if (refreshInterval) {
      clearInterval(refreshInterval);
      setRefreshInterval(null);
    }
  }, [exports.length, onRefresh]);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'processing':
        return <Clock className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'queued':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getProgressColor = (progress) => {
    if (progress < 30) return 'bg-red-500';
    if (progress < 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const estimateTimeRemaining = (progress, startTime) => {
    if (!progress || progress === 0) return 'Calculating...';
    
    const elapsed = Date.now() - new Date(startTime).getTime();
    const remaining = (elapsed / progress) * (100 - progress);
    
    if (remaining < 60000) return 'Less than 1 minute';
    if (remaining < 3600000) return `${Math.round(remaining / 60000)} minutes`;
    return `${Math.round(remaining / 3600000)} hours`;
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Active Export Jobs</h3>

      {exports.length === 0 ? (
        <div className="text-center py-12">
          <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No active exports</h3>
          <p className="text-gray-600">All exports have completed processing.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {exports.map((exportJob) => (
            <div key={exportJob.job_id} className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  {getStatusIcon(exportJob.status)}
                  <div className="ml-3">
                    <h4 className="text-lg font-medium text-gray-900">
                      {exportJob.format.toUpperCase()} Export
                    </h4>
                    <p className="text-sm text-gray-600">
                      Job ID: {exportJob.job_id.substring(0, 8)}...
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900 capitalize">
                    {exportJob.status}
                  </p>
                  <p className="text-sm text-gray-600">
                    {exportJob.total_records > 0 && 
                      `${exportJob.processed_records || 0} / ${exportJob.total_records} records`
                    }
                  </p>
                </div>
              </div>

              {exportJob.status === 'processing' && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Progress</span>
                    <span className="font-medium">{Math.round(exportJob.progress || 0)}%</span>
                  </div>
                  
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div 
                      className={`h-3 rounded-full transition-all duration-300 ${getProgressColor(exportJob.progress || 0)}`}
                      style={{ width: `${exportJob.progress || 0}%` }}
                    ></div>
                  </div>
                  
                  <div className="flex justify-between text-sm text-gray-600">
                    <span>
                      Started: {new Date(exportJob.created_at).toLocaleTimeString()}
                    </span>
                    <span>
                      ETA: {estimateTimeRemaining(exportJob.progress, exportJob.created_at)}
                    </span>
                  </div>
                </div>
              )}

              {exportJob.status === 'queued' && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
                  <p className="text-sm text-yellow-800">
                    Export is queued for processing. It will start shortly.
                  </p>
                </div>
              )}

              {exportJob.status === 'failed' && exportJob.error_message && (
                <div className="bg-red-50 border border-red-200 rounded-md p-3">
                  <p className="text-sm text-red-800">
                    <strong>Error:</strong> {exportJob.error_message}
                  </p>
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
