import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Layout, Card, Row, Col, Statistic, Table, Input, Button, DatePicker, Alert, Space } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { SearchOutlined, ReloadOutlined, DashboardOutlined } from '@ant-design/icons';
import './App.css';

const { Header, Content } = Layout;
const { RangePicker } = DatePicker;

function App() {
  const [metrics, setMetrics] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [performanceData, setPerformanceData] = useState([]);

  // Fetch metrics summary
  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/v1/metrics/summary');
      setMetrics(response.data);
      
      // Generate mock performance data for demo
      const mockData = Array.from({ length: 24 }, (_, i) => ({
        hour: `${i}:00`,
        requests: Math.floor(Math.random() * 1000) + 100,
        responseTime: Math.floor(Math.random() * 500) + 50,
        errors: Math.floor(Math.random() * 50)
      }));
      setPerformanceData(mockData);
      
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  // Search logs
  const searchLogs = async (query = searchQuery) => {
    try {
      setLoading(true);
      const response = await axios.get('/api/v1/logs/search', {
        params: { query, limit: 50 }
      });
      setLogs(response.data.logs);
    } catch (error) {
      console.error('Failed to search logs:', error);
    } finally {
      setLoading(false);
    }
  };

  // Submit test quiz
  const submitTestQuiz = async () => {
    try {
      const testData = {
        question_id: `q_${Date.now()}`,
        quiz_type: 'demo',
        question: 'What is the capital of France?',
        answer: 'Paris'
      };

      await axios.post('/api/v1/quiz/submit', testData, {
        headers: {
          'X-User-ID': 'demo_user_123',
          'X-Session-ID': `session_${Date.now()}`
        }
      });

      // Refresh data
      setTimeout(() => {
        fetchMetrics();
        searchLogs();
      }, 1000);
      
    } catch (error) {
      console.error('Failed to submit test quiz:', error);
    }
  };

  useEffect(() => {
    fetchMetrics();
    searchLogs();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchMetrics();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const logColumns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (text) => new Date(text).toLocaleString(),
      width: 200
    },
    {
      title: 'Event',
      dataIndex: 'event',
      key: 'event',
      width: 150
    },
    {
      title: 'Level',
      dataIndex: 'level',
      key: 'level',
      width: 100,
      render: (level) => (
        <span className={`log-level ${level?.toLowerCase()}`}>
          {level?.toUpperCase()}
        </span>
      )
    },
    {
      title: 'User ID',
      dataIndex: 'user_id',
      key: 'user_id',
      width: 120
    },
    {
      title: 'Details',
      key: 'details',
      render: (record) => (
        <div style={{ fontSize: '12px', color: '#666' }}>
          {record.request_id && <div>Request: {record.request_id}</div>}
          {record.process_time_ms && <div>Time: {record.process_time_ms}ms</div>}
          {record.error_message && <div>Error: {record.error_message}</div>}
        </div>
      )
    }
  ];

  return (
    <Layout className="layout">
      <Header className="header">
        <div className="logo">
          <DashboardOutlined /> AI Quiz Platform - Logging & Monitoring
        </div>
      </Header>
      
      <Content style={{ padding: '24px' }}>
        {/* Metrics Overview */}
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="Total Logs Today"
                value={metrics?.logging?.total_logs_today || 0}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="Error Count"
                value={metrics?.logging?.error_count_today || 0}
                valueStyle={{ color: '#cf1322' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="CPU Usage"
                value={metrics?.system?.cpu_percent || 0}
                precision={1}
                suffix="%"
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="Memory Usage"
                value={metrics?.system?.memory_percent || 0}
                precision={1}
                suffix="%"
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
        </Row>

        {/* Performance Charts */}
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col span={12}>
            <Card title="Request Volume (24h)" extra={<ReloadOutlined onClick={fetchMetrics} />}>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="requests" stroke="#1890ff" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          </Col>
          <Col span={12}>
            <Card title="Response Time (24h)">
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="responseTime" fill="#52c41a" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </Col>
        </Row>

        {/* Test Demo */}
        <Card style={{ marginBottom: '24px' }}>
          <Alert
            message="Demo Mode"
            description="Click the button below to submit a test quiz and see real-time logging in action."
            type="info"
            showIcon
            action={
              <Button type="primary" onClick={submitTestQuiz}>
                Submit Test Quiz
              </Button>
            }
          />
        </Card>

        {/* Log Search */}
        <Card title="Log Search & Analysis">
          <div style={{ marginBottom: '16px' }}>
            <Space.Compact>
              <Input
                style={{ width: '300px' }}
                placeholder="Search logs (e.g., 'error', 'quiz_submission')"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onPressEnter={() => searchLogs()}
              />
              <Button type="primary" icon={<SearchOutlined />} onClick={() => searchLogs()}>
                Search
              </Button>
              <Button onClick={() => searchLogs('')} style={{ marginLeft: '8px' }}>
                Show All
              </Button>
            </Space.Compact>
          </div>

          <Table
            dataSource={logs}
            columns={logColumns}
            rowKey={(record) => `${record.timestamp}-${Math.random()}`}
            loading={loading}
            pagination={{ pageSize: 10 }}
            scroll={{ x: 800 }}
            size="small"
          />
        </Card>
      </Content>
    </Layout>
  );
}

export default App;
