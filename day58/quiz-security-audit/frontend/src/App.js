import React, { useState, useEffect } from 'react';
import {
  Container, Grid, Card, CardContent, Typography, Box,
  Button, Chip, LinearProgress, Paper, Tab, Tabs,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Alert, CircularProgress
} from '@mui/material';
import {
  Security, Warning, CheckCircle, BugReport, Shield,
  Speed, TrendingDown, Assessment
} from '@mui/icons-material';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import axios from 'axios';
import './App.css';

const API_BASE = 'http://localhost:8000';

function App() {
  const [status, setStatus] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [scans, setScans] = useState([]);
  const [vulnerabilities, setVulnerabilities] = useState([]);
  const [compliance, setCompliance] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [scanning, setScanning] = useState(false);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [statusRes, metricsRes, scansRes, vulnsRes] = await Promise.all([
        axios.get(`${API_BASE}/api/security/status`),
        axios.get(`${API_BASE}/api/security/metrics`),
        axios.get(`${API_BASE}/api/security/scans?limit=5`),
        axios.get(`${API_BASE}/api/security/vulnerabilities`)
      ]);

      setStatus(statusRes.data);
      setMetrics(metricsRes.data);
      setScans(scansRes.data);
      setVulnerabilities(vulnsRes.data.vulnerabilities);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const startScan = async (scanType) => {
    setScanning(true);
    try {
      await axios.post(`${API_BASE}/api/security/scan`, {
        scan_type: scanType,
        target: 'all'
      });
      setTimeout(loadData, 3000);
    } catch (error) {
      console.error('Error starting scan:', error);
    } finally {
      setScanning(false);
    }
  };

  const loadCompliance = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/api/security/compliance`);
      setCompliance(res.data);
    } catch (error) {
      console.error('Error loading compliance:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStateColor = (state) => {
    const colors = {
      green: '#4caf50',
      yellow: '#ff9800',
      red: '#f44336',
      blue: '#2196f3'
    };
    return colors[state] || '#757575';
  };

  const getSeverityColor = (severity) => {
    const colors = {
      critical: 'error',
      high: 'warning',
      medium: 'info',
      low: 'default'
    };
    return colors[severity] || 'default';
  };

  if (!status || !metrics) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <div className="App">
      <Box sx={{ bgcolor: '#f5f5f5', minHeight: '100vh', py: 4 }}>
        <Container maxWidth="xl">
          <Box mb={4}>
            <Typography variant="h3" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Shield sx={{ fontSize: 40, color: getStateColor(status.state) }} />
              Security Audit Dashboard
            </Typography>
            <Typography variant="subtitle1" color="textSecondary">
              Comprehensive security monitoring for Quiz Platform
            </Typography>
          </Box>

          {/* Status Cards */}
          <Grid container spacing={3} mb={4}>
            <Grid item xs={12} md={3}>
              <Card sx={{ bgcolor: getStateColor(status.state), color: 'white' }}>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Box>
                      <Typography variant="h6">Security State</Typography>
                      <Typography variant="h3" sx={{ textTransform: 'uppercase' }}>
                        {status.state}
                      </Typography>
                    </Box>
                    <Security sx={{ fontSize: 60, opacity: 0.3 }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Box>
                      <Typography color="textSecondary" gutterBottom>Critical Issues</Typography>
                      <Typography variant="h3">{status.critical_count}</Typography>
                      <Typography variant="body2" color="error">Immediate attention</Typography>
                    </Box>
                    <BugReport sx={{ fontSize: 50, color: '#f44336', opacity: 0.5 }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Box>
                      <Typography color="textSecondary" gutterBottom>Compliance Score</Typography>
                      <Typography variant="h3">{status.compliance_score}%</Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={status.compliance_score} 
                        sx={{ mt: 1, height: 8, borderRadius: 4 }}
                      />
                    </Box>
                    <Assessment sx={{ fontSize: 50, color: '#2196f3', opacity: 0.5 }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Box>
                      <Typography color="textSecondary" gutterBottom>Scans Today</Typography>
                      <Typography variant="h3">{metrics.metrics.scans_today}</Typography>
                      <Typography variant="body2" color="success.main">
                        {metrics.metrics.vulnerabilities_fixed_today} fixed
                      </Typography>
                    </Box>
                    <Speed sx={{ fontSize: 50, color: '#4caf50', opacity: 0.5 }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Action Buttons */}
          <Paper sx={{ p: 2, mb: 4 }}>
            <Box display="flex" gap={2} flexWrap="wrap">
              <Button 
                variant="contained" 
                startIcon={<Security />}
                onClick={() => startScan('full')}
                disabled={scanning}
              >
                Full Scan
              </Button>
              <Button 
                variant="outlined" 
                onClick={() => startScan('quick')}
                disabled={scanning}
              >
                Quick Scan
              </Button>
              <Button 
                variant="outlined" 
                onClick={() => startScan('secrets')}
                disabled={scanning}
              >
                Secrets Scan
              </Button>
              <Button 
                variant="outlined" 
                onClick={() => startScan('dependencies')}
                disabled={scanning}
              >
                Dependencies
              </Button>
              <Button 
                variant="outlined" 
                onClick={loadCompliance}
                startIcon={<Assessment />}
              >
                Compliance Report
              </Button>
            </Box>
            {scanning && (
              <Box mt={2}>
                <LinearProgress />
                <Typography variant="body2" color="textSecondary" mt={1}>
                  Security scan in progress...
                </Typography>
              </Box>
            )}
          </Paper>

          {/* Tabs */}
          <Paper sx={{ mb: 3 }}>
            <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
              <Tab label="Overview" />
              <Tab label="Vulnerabilities" />
              <Tab label="Scan History" />
              <Tab label="Compliance" />
            </Tabs>
          </Paper>

          {/* Tab Content */}
          {activeTab === 0 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Vulnerability Trend (7 Days)</Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={metrics.vulnerability_trend}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="critical" stroke="#f44336" strokeWidth={2} />
                        <Line type="monotone" dataKey="high" stroke="#ff9800" strokeWidth={2} />
                        <Line type="monotone" dataKey="medium" stroke="#2196f3" strokeWidth={2} />
                        <Line type="monotone" dataKey="low" stroke="#4caf50" strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Top Vulnerabilities</Typography>
                    {metrics.top_vulnerability_types.map((vuln, idx) => (
                      <Box key={idx} mb={2}>
                        <Box display="flex" justifyContent="space-between" mb={1}>
                          <Typography variant="body2">{vuln.type}</Typography>
                          <Chip 
                            label={vuln.count} 
                            size="small" 
                            color={getSeverityColor(vuln.severity)}
                          />
                        </Box>
                        <LinearProgress 
                          variant="determinate" 
                          value={(vuln.count / 10) * 100} 
                          sx={{ height: 6, borderRadius: 3 }}
                        />
                      </Box>
                    ))}
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Security Metrics</Typography>
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={3}>
                        <Box textAlign="center" p={2}>
                          <Typography variant="h4" color="primary">
                            {metrics.metrics.total_scans}
                          </Typography>
                          <Typography color="textSecondary">Total Scans</Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <Box textAlign="center" p={2}>
                          <Typography variant="h4" color="success.main">
                            {metrics.metrics.vulnerabilities_fixed_today}
                          </Typography>
                          <Typography color="textSecondary">Fixed Today</Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <Box textAlign="center" p={2}>
                          <Typography variant="h4" color="warning.main">
                            {metrics.metrics.mean_time_to_fix_hours}h
                          </Typography>
                          <Typography color="textSecondary">Mean Time to Fix</Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <Box textAlign="center" p={2}>
                          <Typography variant="h4" color="error">
                            {metrics.metrics.security_debt_hours}h
                          </Typography>
                          <Typography color="textSecondary">Security Debt</Typography>
                        </Box>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}

          {activeTab === 1 && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Active Vulnerabilities</Typography>
                {vulnerabilities.length === 0 ? (
                  <Alert severity="success" sx={{ mt: 2 }}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <CheckCircle />
                      No active vulnerabilities found. Your system is secure!
                    </Box>
                  </Alert>
                ) : (
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Severity</TableCell>
                          <TableCell>Title</TableCell>
                          <TableCell>Type</TableCell>
                          <TableCell>File</TableCell>
                          <TableCell>Status</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {vulnerabilities.map((vuln) => (
                          <TableRow key={vuln.id}>
                            <TableCell>
                              <Chip 
                                label={vuln.severity} 
                                color={getSeverityColor(vuln.severity)}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>{vuln.title}</TableCell>
                            <TableCell>{vuln.type}</TableCell>
                            <TableCell>{vuln.file}</TableCell>
                            <TableCell>
                              <Chip label="Open" color="warning" size="small" />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </CardContent>
            </Card>
          )}

          {activeTab === 2 && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Recent Scans</Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Scan ID</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Started</TableCell>
                        <TableCell>Findings</TableCell>
                        <TableCell>Critical</TableCell>
                        <TableCell>High</TableCell>
                        <TableCell>Medium</TableCell>
                        <TableCell>Low</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {scans.map((scan) => (
                        <TableRow key={scan.scan_id}>
                          <TableCell>{scan.scan_id.substring(0, 8)}...</TableCell>
                          <TableCell>
                            <Chip 
                              label={scan.status} 
                              color={scan.status === 'completed' ? 'success' : 'default'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {new Date(scan.started_at).toLocaleString()}
                          </TableCell>
                          <TableCell>{scan.findings.length}</TableCell>
                          <TableCell>{scan.summary.critical}</TableCell>
                          <TableCell>{scan.summary.high}</TableCell>
                          <TableCell>{scan.summary.medium}</TableCell>
                          <TableCell>{scan.summary.low}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          )}

          {activeTab === 3 && (
            <Grid container spacing={3}>
              {!compliance ? (
                <Grid item xs={12}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>Compliance Report</Typography>
                      <Box textAlign="center" py={4}>
                        <Button 
                          variant="contained" 
                          onClick={loadCompliance}
                          disabled={loading}
                        >
                          Generate Compliance Report
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ) : (
                <>
                  <Grid item xs={12}>
                    <Alert severity="info">
                      Report generated: {new Date(compliance.generated_at).toLocaleString()}
                    </Alert>
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>Framework Compliance</Typography>
                        {Object.entries(compliance.compliance_frameworks).map(([key, value]) => (
                          <Box key={key} mb={3}>
                            <Box display="flex" justifyContent="space-between" mb={1}>
                              <Typography variant="body1">
                                {key.replace(/_/g, ' ')}
                              </Typography>
                              <Typography variant="body1" fontWeight="bold">
                                {value.score}%
                              </Typography>
                            </Box>
                            <LinearProgress 
                              variant="determinate" 
                              value={value.score} 
                              sx={{ height: 8, borderRadius: 4 }}
                            />
                            <Typography variant="caption" color="textSecondary">
                              {value.passed_checks}/{value.total_checks} checks passed
                            </Typography>
                          </Box>
                        ))}
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>Recommendations</Typography>
                        {compliance.recommendations.map((rec, idx) => (
                          <Alert key={idx} severity="warning" sx={{ mb: 2 }}>
                            {rec}
                          </Alert>
                        ))}
                      </CardContent>
                    </Card>
                  </Grid>
                </>
              )}
            </Grid>
          )}
        </Container>
      </Box>
    </div>
  );
}

export default App;
