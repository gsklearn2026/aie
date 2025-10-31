import React, { useState, useEffect } from 'react';
import { Clock, CheckCircle, XCircle, AlertCircle, RefreshCw } from 'lucide-react';

const JobStatus = ({ jobId, onJobComplete }) => {
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!jobId) return;

    const pollJobStatus = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/jobs/${jobId}`);
        const jobData = await response.json();
        
        setJob(jobData);
        setLoading(false);

        // If job is complete, notify parent and stop polling
        if (jobData.status === 'completed' || jobData.status === 'failed') {
          if (onJobComplete) {
            onJobComplete(jobData);
          }
          return;
        }

        // Continue polling if job is still running
        if (jobData.status === 'pending' || jobData.status === 'processing' || jobData.status === 'retrying') {
          setTimeout(pollJobStatus, 2000); // Poll every 2 seconds
        }
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    pollJobStatus();
  }, [jobId, onJobComplete]);

  if (loading) {
    return (
      <div className="flex items-center space-x-2 p-4 bg-blue-50 rounded-lg">
        <RefreshCw className="w-5 h-5 animate-spin text-blue-500" />
        <span>Loading job status...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center space-x-2 p-4 bg-red-50 rounded-lg">
        <XCircle className="w-5 h-5 text-red-500" />
        <span className="text-red-700">Error: {error}</span>
      </div>
    );
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'processing':
        return <RefreshCw className="w-5 h-5 animate-spin text-blue-500" />;
      case 'retrying':
        return <AlertCircle className="w-5 h-5 text-orange-500" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-50 border-yellow-200';
      case 'processing':
        return 'bg-blue-50 border-blue-200';
      case 'retrying':
        return 'bg-orange-50 border-orange-200';
      case 'completed':
        return 'bg-green-50 border-green-200';
      case 'failed':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className={`p-4 rounded-lg border ${getStatusColor(job.status)}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          {getStatusIcon(job.status)}
          <span className="font-medium capitalize">{job.status}</span>
        </div>
        <span className="text-sm text-gray-500">Job ID: {job.job_id.slice(0, 8)}...</span>
      </div>

      <div className="space-y-2 text-sm">
        <div>
          <span className="font-medium">Type:</span> {job.job_type}
        </div>
        <div>
          <span className="font-medium">Created:</span> {new Date(job.created_at).toLocaleString()}
        </div>
        {job.started_at && (
          <div>
            <span className="font-medium">Started:</span> {new Date(job.started_at).toLocaleString()}
          </div>
        )}
        {job.completed_at && (
          <div>
            <span className="font-medium">Completed:</span> {new Date(job.completed_at).toLocaleString()}
          </div>
        )}
        {job.retry_count > 0 && (
          <div>
            <span className="font-medium">Retries:</span> {job.retry_count}
          </div>
        )}
      </div>

      {job.error_message && (
        <div className="mt-3 p-2 bg-red-100 rounded text-sm text-red-700">
          <span className="font-medium">Error:</span> {job.error_message}
        </div>
      )}

      {job.result_data && (
        <div className="mt-3">
          <span className="font-medium text-sm">Results:</span>
          <div className="mt-1 p-2 bg-white rounded border text-sm">
            {job.result_data.questions && (
              <div>Generated {job.result_data.questions.length} questions</div>
            )}
            {job.result_data.batch_results && (
              <div>Processed {job.result_data.total_topics} topics, {job.result_data.total_questions} questions</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default JobStatus;
