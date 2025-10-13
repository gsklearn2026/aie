import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const MetricsChart = ({ stats }) => {
  const [metricsHistory, setMetricsHistory] = useState([]);

  useEffect(() => {
    if (stats) {
      const timestamp = new Date().toLocaleTimeString();
      const newDataPoint = {
        time: timestamp,
        activeUsers: stats.activeUsers,
        responseTime: (stats.avgResponseTime * 1000).toFixed(0),
        cpu: stats.systemHealth.cpu.toFixed(1),
        memory: stats.systemHealth.memory.toFixed(1)
      };

      setMetricsHistory(prev => {
        const updated = [...prev, newDataPoint];
        return updated.slice(-20); // Keep last 20 data points
      });
    }
  }, [stats]);

  return (
    <div className="metrics-chart-panel">
      <h3>📊 Real-time Metrics</h3>
      
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={metricsHistory}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="time" 
              tick={{ fontSize: 12 }}
              interval="preserveStartEnd"
            />
            <YAxis />
            <Tooltip />
            <Line 
              type="monotone" 
              dataKey="activeUsers" 
              stroke="#8884d8" 
              name="Active Users"
              strokeWidth={2}
            />
            <Line 
              type="monotone" 
              dataKey="responseTime" 
              stroke="#82ca9d" 
              name="Response Time (ms)"
              strokeWidth={2}
            />
            <Line 
              type="monotone" 
              dataKey="cpu" 
              stroke="#ff7300" 
              name="CPU %"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default MetricsChart;
