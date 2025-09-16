import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { ShieldCheckIcon, ExclamationTriangleIcon, ClockIcon } from '@heroicons/react/24/outline';
import axios from 'axios';

const SecurityDashboard = () => {
  const [metrics, setMetrics] = useState({
    total_audits: 0,
    avg_security_score: 0,
    critical_vulnerabilities: 0,
    high_vulnerabilities: 0,
    last_audit: null
  });
  
  const [audits, setAudits] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
    fetchAudits();
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await axios.get('/api/security/dashboard/metrics');
      setMetrics(response.data);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  };

  const fetchAudits = async () => {
    try {
      const response = await axios.get('/api/security/audits');
      setAudits(response.data.audits || []);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch audits:', error);
      setLoading(false);
    }
  };

  const viewAuditDetails = async (auditId) => {
    try {
      const response = await axios.get(`/api/security/audit/${auditId}`);
      // For now, just log the details - you could show them in a modal or alert
      console.log('Audit Details:', response.data);
      alert(`Audit Details:\n${JSON.stringify(response.data, null, 2)}`);
    } catch (error) {
      console.error('Failed to fetch audit details:', error);
      alert('Failed to fetch audit details. Please try again.');
    }
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 75) return 'text-yellow-600';
    return 'text-red-600';
  };

  const vulnerabilityData = [
    { name: 'Critical', value: metrics.critical_vulnerabilities, color: '#dc2626' },
    { name: 'High', value: metrics.high_vulnerabilities, color: '#ea580c' },
    { name: 'Safe', value: Math.max(0, 100 - metrics.critical_vulnerabilities - metrics.high_vulnerabilities), color: '#16a34a' }
  ];

  const securityTrendData = [
    { date: '2024-01', score: 85 },
    { date: '2024-02', score: 88 },
    { date: '2024-03', score: 92 },
    { date: '2024-04', score: metrics.avg_security_score || 90 },
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Security Dashboard</h1>
        <p className="mt-2 text-gray-600">Monitor your Quiz Platform's security posture</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <ShieldCheckIcon className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Security Score</p>
              <p className={`text-2xl font-bold ${getScoreColor(metrics.avg_security_score)}`}>
                {metrics.avg_security_score}%
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Critical Issues</p>
              <p className="text-2xl font-bold text-red-600">{metrics.critical_vulnerabilities}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-8 w-8 text-orange-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">High Issues</p>
              <p className="text-2xl font-bold text-orange-600">{metrics.high_vulnerabilities}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <ClockIcon className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Audits</p>
              <p className="text-2xl font-bold text-green-600">{metrics.total_audits}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Security Trend Chart */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Security Score Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={securityTrendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="score" 
                stroke="#2563eb" 
                strokeWidth={3}
                dot={{ fill: '#2563eb', strokeWidth: 2, r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Vulnerability Distribution */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Vulnerability Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={vulnerabilityData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={120}
                dataKey="value"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
              >
                {vulnerabilityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Audits */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Recent Audits</h3>
        </div>
        <div className="p-6">
          {audits.length === 0 ? (
            <div className="text-center py-8">
              <ShieldCheckIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No audits yet</h3>
              <p className="mt-1 text-sm text-gray-500">
                Start your first security audit to see results here.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Audit ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {audits.map((audit) => (
                    <tr key={audit.audit_id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {audit.audit_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          audit.status === 'completed' 
                            ? 'bg-green-100 text-green-800'
                            : audit.status === 'running'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {audit.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <button 
                          onClick={() => viewAuditDetails(audit.audit_id)}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SecurityDashboard;
