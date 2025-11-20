import React, { useState, useEffect } from 'react'
import {
  Container, Grid, Paper, Typography, Box, Button, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Alert, CircularProgress, LinearProgress, IconButton, Tooltip
} from '@mui/material'
import {
  Refresh, PlayArrow, History, Warning, CheckCircle, Error
} from '@mui/icons-material'
import {
  PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis
} from 'recharts'
import { api } from './services/api'

const COLORS = ['#4caf50', '#2196f3', '#ff9800', '#f44336']

function App() {
  const [stats, setStats] = useState(null)
  const [content, setContent] = useState([])
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [processingMessage, setProcessingMessage] = useState('')

  const fetchData = async () => {
    try {
      const [statsRes, contentRes, jobsRes] = await Promise.all([
        api.get('/api/content/dashboard'),
        api.get('/api/content/?limit=20'),
        api.get('/api/jobs/?limit=10')
      ])
      setStats(statsRes.data)
      setContent(contentRes.data)
      setJobs(jobsRes.data)
    } catch (error) {
      console.error('Failed to fetch data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  const triggerScan = async () => {
    setRefreshing(true)
    try {
      await api.post('/api/jobs/scan-freshness')
      await fetchData()
    } finally {
      setRefreshing(false)
    }
  }

  const processJobs = async () => {
    setRefreshing(true)
    setProcessingMessage('Starting to process jobs...')
    try {
      // Start processing
      const response = await api.post('/api/jobs/process?batch_size=5')
      const processedCount = response.data.processed || 0
      
      if (processedCount === 0) {
        setProcessingMessage('No pending jobs to process')
        await fetchData()
      } else {
        setProcessingMessage(`Processing ${processedCount} job(s)...`)
        
        // Poll for updates while processing (jobs take time)
        const pollInterval = setInterval(async () => {
          await fetchData()
        }, 1000) // Poll every second
        
        // Wait for processing to complete (estimate: 2 seconds per job + processing time)
        const estimatedTime = processedCount * 3000 // 3 seconds per job estimate
        await new Promise(resolve => setTimeout(resolve, estimatedTime))
        
        clearInterval(pollInterval)
        setProcessingMessage(`Completed processing ${processedCount} job(s)`)
        await fetchData()
        
        // Clear message after 3 seconds
        setTimeout(() => setProcessingMessage(''), 3000)
      }
    } catch (error) {
      console.error('Failed to process jobs:', error)
      setProcessingMessage('Error processing jobs')
      setTimeout(() => setProcessingMessage(''), 3000)
    } finally {
      setRefreshing(false)
    }
  }

  const retryFailedJobs = async () => {
    setRefreshing(true)
    setProcessingMessage('Retrying failed jobs...')
    try {
      const response = await api.post('/api/jobs/retry-failed')
      const retriedCount = response.data.retried || 0
      
      if (retriedCount === 0) {
        setProcessingMessage('No failed jobs to retry')
      } else {
        setProcessingMessage(`Reset ${retriedCount} failed job(s) to pending`)
      }
      await fetchData()
      setTimeout(() => setProcessingMessage(''), 3000)
    } catch (error) {
      console.error('Failed to retry jobs:', error)
      setProcessingMessage('Error retrying jobs')
      setTimeout(() => setProcessingMessage(''), 3000)
    } finally {
      setRefreshing(false)
    }
  }

  const requestRefresh = async (contentId) => {
    try {
      await api.post('/api/content/refresh', {
        content_id: contentId,
        priority: 1
      })
      await fetchData()
    } catch (error) {
      console.error('Failed to request refresh:', error)
    }
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    )
  }

  const lifecycleData = stats ? [
    { name: 'Fresh', value: stats.fresh_count },
    { name: 'Current', value: stats.current_count },
    { name: 'Aging', value: stats.aging_count },
    { name: 'Stale', value: stats.stale_count }
  ] : []

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box 
        display="flex" 
        justifyContent="space-between" 
        alignItems="center" 
        mb={3}
        flexWrap="wrap"
        gap={2}
      >
        <Typography variant="h4" fontWeight="bold">
          Content Refresh Dashboard
        </Typography>
        <Box display="flex" gap={1} flexWrap="wrap">
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={triggerScan}
            disabled={refreshing}
            size="small"
          >
            Scan Freshness
          </Button>
          {stats?.queue_breakdown?.failed > 0 && (
            <Button
              variant="outlined"
              color="error"
              onClick={retryFailedJobs}
              disabled={refreshing}
              size="small"
            >
              Retry Failed ({stats.queue_breakdown.failed})
            </Button>
          )}
          <Button
            variant="contained"
            startIcon={<PlayArrow />}
            onClick={processJobs}
            disabled={refreshing}
            size="small"
          >
            Process Queue
          </Button>
        </Box>
      </Box>

      {refreshing && <LinearProgress sx={{ mb: 2 }} />}
      {processingMessage && (
        <Alert severity="info" sx={{ mb: 2 }}>
          {processingMessage}
        </Alert>
      )}

      {/* Alerts */}
      {stats?.alerts?.map((alert, i) => (
        <Alert severity={alert.type} sx={{ mb: 2 }} key={i}>
          {alert.message}
        </Alert>
      ))}

      {/* Stats Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 3, textAlign: 'center', height: '100%' }}>
            <Typography variant="h3" color="primary" fontWeight="bold">
              {stats?.total_content || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Total Content
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h3" color="secondary" sx={{ textAlign: 'center', mb: 1 }}>
              {stats?.queue_depth || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', mb: 2 }}>
              Queue Depth
            </Typography>
            {stats?.queue_breakdown && (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.75, mt: 'auto', pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="caption" color="text.secondary">Pending:</Typography>
                  <Chip label={stats.queue_breakdown.pending || 0} size="small" variant="outlined" />
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="caption" color="text.secondary">Processing:</Typography>
                  <Chip label={stats.queue_breakdown.processing || 0} size="small" color="warning" variant="outlined" />
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="caption" color="text.secondary">Completed:</Typography>
                  <Chip label={stats.queue_breakdown.completed || 0} size="small" color="success" variant="outlined" />
                </Box>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="caption" color="text.secondary">Failed:</Typography>
                  <Chip label={stats.queue_breakdown.failed || 0} size="small" color="error" variant="outlined" />
                </Box>
              </Box>
            )}
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 3, textAlign: 'center', height: '100%' }}>
            <Typography variant="h3" color="success.main" fontWeight="bold">
              {stats?.avg_freshness_score?.toFixed(1) || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Avg Freshness Score
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 3, textAlign: 'center', height: '100%' }}>
            <Typography variant="h3" color={stats?.rollback_rate > 0.1 ? 'error' : 'success.main'} fontWeight="bold">
              {((stats?.rollback_rate || 0) * 100).toFixed(1)}%
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Rollback Rate
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Lifecycle Distribution */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              Content Lifecycle Distribution
            </Typography>
            {lifecycleData.length > 0 && lifecycleData.some(d => d.value > 0) ? (
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={lifecycleData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={90}
                    label={({ name, value }) => `${name}: ${value}`}
                    labelLine={false}
                  >
                    {lifecycleData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <Box display="flex" justifyContent="center" alignItems="center" height={280}>
                <Typography variant="body2" color="text.secondary">
                  No data available
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Recent Jobs */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Refresh Jobs
            </Typography>
            <TableContainer sx={{ maxHeight: 400 }}>
              <Table size="small" stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Type</strong></TableCell>
                    <TableCell><strong>Status</strong></TableCell>
                    <TableCell><strong>Priority</strong></TableCell>
                    <TableCell><strong>Error</strong></TableCell>
                    <TableCell><strong>Created</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {jobs.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} align="center" sx={{ py: 3 }}>
                        <Typography variant="body2" color="text.secondary">
                          No jobs found
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    jobs.map((job) => (
                      <TableRow key={job.id} hover>
                        <TableCell>{job.job_type?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</TableCell>
                        <TableCell>
                          <Chip
                            size="small"
                            label={job.status}
                            color={
                              job.status === 'completed' ? 'success' :
                              job.status === 'failed' ? 'error' :
                              job.status === 'processing' ? 'warning' : 'default'
                            }
                          />
                        </TableCell>
                        <TableCell>{job.priority}</TableCell>
                        <TableCell sx={{ maxWidth: 250 }}>
                          {job.error_message ? (
                            <Tooltip title={job.error_message} arrow>
                              <Typography 
                                variant="caption" 
                                color="error" 
                                sx={{ 
                                  display: 'block',
                                  overflow: 'hidden', 
                                  textOverflow: 'ellipsis',
                                  whiteSpace: 'nowrap'
                                }}
                              >
                                {job.error_message}
                              </Typography>
                            </Tooltip>
                          ) : (
                            <Typography variant="caption" color="text.secondary">—</Typography>
                          )}
                        </TableCell>
                        <TableCell>
                          <Typography variant="caption">
                            {new Date(job.created_at).toLocaleString()}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        {/* Content List */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Content Status
            </Typography>
            <TableContainer sx={{ maxHeight: 600 }}>
              <Table stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Topic</strong></TableCell>
                    <TableCell><strong>Question</strong></TableCell>
                    <TableCell><strong>State</strong></TableCell>
                    <TableCell><strong>Lifecycle</strong></TableCell>
                    <TableCell><strong>Freshness</strong></TableCell>
                    <TableCell><strong>Actions</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {content.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} align="center" sx={{ py: 3 }}>
                        <Typography variant="body2" color="text.secondary">
                          No content found
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    content.map((item) => (
                      <TableRow key={item.id} hover>
                        <TableCell><strong>{item.topic}</strong></TableCell>
                        <TableCell sx={{ maxWidth: 350 }}>
                          <Tooltip title={item.question} arrow>
                            <Typography 
                              variant="body2" 
                              sx={{ 
                                overflow: 'hidden', 
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap'
                              }}
                            >
                              {item.question}
                            </Typography>
                          </Tooltip>
                        </TableCell>
                        <TableCell>
                          <Chip
                            size="small"
                            label={item.state}
                            color={
                              item.state === 'active' ? 'success' :
                              item.state === 'flagged' ? 'warning' :
                              item.state === 'refreshing' ? 'info' : 'default'
                            }
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            size="small"
                            label={item.lifecycle}
                            variant="outlined"
                            color={
                              item.lifecycle === 'fresh' ? 'success' :
                              item.lifecycle === 'current' ? 'info' :
                              item.lifecycle === 'aging' ? 'warning' : 'error'
                            }
                          />
                        </TableCell>
                        <TableCell>
                          <Box display="flex" alignItems="center" gap={1}>
                            <LinearProgress
                              variant="determinate"
                              value={item.freshness_score}
                              sx={{ width: 80, height: 8, borderRadius: 1 }}
                              color={
                                item.freshness_score >= 70 ? 'success' :
                                item.freshness_score >= 40 ? 'warning' : 'error'
                              }
                            />
                            <Typography variant="body2" fontWeight="medium">
                              {item.freshness_score.toFixed(0)}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Tooltip title="Request Refresh">
                            <span>
                              <IconButton
                                size="small"
                                onClick={() => requestRefresh(item.id)}
                                disabled={item.state !== 'active'}
                                color="primary"
                              >
                                <Refresh />
                              </IconButton>
                            </span>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  )
}

export default App
