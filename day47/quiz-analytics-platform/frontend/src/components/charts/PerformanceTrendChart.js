import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { format, parseISO } from 'date-fns';

function PerformanceTrendChart({ data }) {
  const formattedData = data.map(item => ({
    ...item,
    date: format(parseISO(item.date), 'MMM dd'),
    avg_score: Math.round(item.avg_score * 10) / 10
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={formattedData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis 
          dataKey="date" 
          tick={{ fontSize: 12 }}
        />
        <YAxis 
          domain={[0, 100]}
          tick={{ fontSize: 12 }}
        />
        <Tooltip 
          formatter={(value, name) => [
            `${value}${name === 'avg_score' ? '%' : ''}`,
            name === 'avg_score' ? 'Average Score' : 'Sessions'
          ]}
          labelFormatter={(label) => `Date: ${label}`}
        />
        <Legend />
        <Line 
          type="monotone" 
          dataKey="avg_score" 
          stroke="#2196f3" 
          strokeWidth={2}
          dot={{ r: 4 }}
          name="Average Score (%)"
        />
        <Line 
          type="monotone" 
          dataKey="sessions" 
          stroke="#ff9800" 
          strokeWidth={2}
          dot={{ r: 4 }}
          name="Daily Sessions"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

export default PerformanceTrendChart;
