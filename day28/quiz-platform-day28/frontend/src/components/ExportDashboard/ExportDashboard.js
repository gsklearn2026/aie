import React, { useState, useEffect } from 'react';
import { Download, FileText, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import ExportForm from './ExportForm';
import ExportHistory from './ExportHistory';
import ExportProgress from './ExportProgress';
import { exportService } from '../../services/exportService';

const ExportDashboard = () => {
  const [activeTab, setActiveTab] = useState('create');
  const [exports, setExports] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadExports();
    // Poll for updates every 5 seconds
    const interval = setInterval(loadExports, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadExports = async () => {
    try {
      const data = await exportService.getExports();
      setExports(data);
    } catch (error) {
      console.error('Failed to load exports:', error);
    }
  };

  const handleExportCreate = async (exportRequest) => {
    setLoading(true);
    try {
      const response = await exportService.createExport(exportRequest);
      await loadExports();
      setActiveTab('history');
      return response;
    } catch (error) {
      console.error('Failed to create export:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'processing':
        return <Clock className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
    }
  };

  const stats = {
    total: exports.length,
    completed: exports.filter(e => e.status === 'completed').length,
    processing: exports.filter(e => e.status === 'processing').length,
    failed: exports.filter(e => e.status === 'failed').length
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <FileText className="w-8 h-8 text-blue-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Exports</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <CheckCircle className="w-8 h-8 text-green-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Completed</p>
              <p className="text-2xl font-bold text-gray-900">{stats.completed}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <Clock className="w-8 h-8 text-blue-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Processing</p>
              <p className="text-2xl font-bold text-gray-900">{stats.processing}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <XCircle className="w-8 h-8 text-red-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Failed</p>
              <p className="text-2xl font-bold text-gray-900">{stats.failed}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex">
            <button
              onClick={() => setActiveTab('create')}
              className={`py-4 px-6 text-sm font-medium border-b-2 ${
                activeTab === 'create'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Create Export
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`py-4 px-6 text-sm font-medium border-b-2 ${
                activeTab === 'history'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Export History
            </button>
            <button
              onClick={() => setActiveTab('progress')}
              className={`py-4 px-6 text-sm font-medium border-b-2 ${
                activeTab === 'progress'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Active Jobs
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'create' && (
            <ExportForm onSubmit={handleExportCreate} loading={loading} />
          )}
          
          {activeTab === 'history' && (
            <ExportHistory exports={exports} onRefresh={loadExports} />
          )}
          
          {activeTab === 'progress' && (
            <ExportProgress 
              exports={exports.filter(e => e.status === 'processing' || e.status === 'queued')} 
              onRefresh={loadExports}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default ExportDashboard;
