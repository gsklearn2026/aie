import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Paper, Typography, Box, Button, TextField, Card, CardContent,
  Divider, List, ListItem, ListItemText, Chip, Alert,
  CircularProgress, ButtonGroup, Grid
} from '@mui/material';
import QualityBadge from '../components/QualityBadge';
import { curationApi } from '../services/api';

function ReviewPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [curation, setCuration] = useState(null);
  const [feedback, setFeedback] = useState('');
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  const reviewerId = 'admin';

  useEffect(() => {
    fetchData();
  }, [id]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [curationData, logs] = await Promise.all([
        curationApi.getCuration(id),
        curationApi.getAuditLogs(id)
      ]);
      setCuration(curationData);
      setAuditLogs(logs);
      setError(null);
    } catch (err) {
      setError('Failed to load content');
    }
    setLoading(false);
  };

  const handleAction = async (action) => {
    setActionLoading(true);
    try {
      switch (action) {
        case 'approve':
          await curationApi.approve(id, reviewerId);
          break;
        case 'reject':
          if (!feedback) {
            setError('Please provide rejection reason');
            setActionLoading(false);
            return;
          }
          await curationApi.reject(id, reviewerId, feedback);
          break;
        case 'revise':
          if (!feedback) {
            setError('Please provide revision feedback');
            setActionLoading(false);
            return;
          }
          await curationApi.requestRevision(id, reviewerId, feedback);
          break;
        case 'release':
          await curationApi.release(id, reviewerId);
          break;
        default:
          break;
      }
      navigate('/queue');
    } catch (err) {
      setError(`Failed to ${action} content`);
    }
    setActionLoading(false);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (!curation) {
    return <Alert severity="error">Content not found</Alert>;
  }

  const question = curation.question;
  const isUnderReview = curation.status === 'under_review';

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Content Review
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Question</Typography>
                <Box>
                  <Chip label={question.topic} sx={{ mr: 1 }} />
                  <Chip label={question.difficulty} variant="outlined" />
                </Box>
              </Box>

              <Typography variant="body1" paragraph>
                {question.text}
              </Typography>

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" gutterBottom>
                Options:
              </Typography>
              <List dense>
                {question.options.map((option, index) => (
                  <ListItem
                    key={index}
                    sx={{
                      bgcolor: index === question.correct_answer ? 'success.light' : 'transparent',
                      borderRadius: 1
                    }}
                  >
                    <ListItemText
                      primary={`${String.fromCharCode(65 + index)}. ${option}`}
                    />
                    {index === question.correct_answer && (
                      <Chip label="Correct" color="success" size="small" />
                    )}
                  </ListItem>
                ))}
              </List>

              {question.explanation && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="subtitle2" gutterBottom>
                    Explanation:
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {question.explanation}
                  </Typography>
                </>
              )}
            </CardContent>
          </Card>

          {isUnderReview && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Review Actions
                </Typography>

                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Feedback (required for reject/revise)"
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  sx={{ mb: 2 }}
                />

                <ButtonGroup fullWidth disabled={actionLoading}>
                  <Button
                    color="success"
                    variant="contained"
                    onClick={() => handleAction('approve')}
                  >
                    Approve
                  </Button>
                  <Button
                    color="warning"
                    variant="contained"
                    onClick={() => handleAction('revise')}
                  >
                    Request Revision
                  </Button>
                  <Button
                    color="error"
                    variant="contained"
                    onClick={() => handleAction('reject')}
                  >
                    Reject
                  </Button>
                </ButtonGroup>

                <Button
                  fullWidth
                  variant="outlined"
                  sx={{ mt: 1 }}
                  onClick={() => handleAction('release')}
                  disabled={actionLoading}
                >
                  Release Back to Queue
                </Button>
              </CardContent>
            </Card>
          )}
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quality Metrics
              </Typography>

              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography>Overall Score</Typography>
                <QualityBadge score={curation.quality_score} />
              </Box>

              <Divider sx={{ my: 1 }} />

              {Object.entries(curation.quality_metrics).map(([key, value]) => (
                <Box
                  key={key}
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                  py={0.5}
                >
                  <Typography variant="body2">
                    {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </Typography>
                  <Typography variant="body2">
                    {(value * 100).toFixed(0)}%
                  </Typography>
                </Box>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Audit History
              </Typography>

              <List dense>
                {auditLogs.map((log) => (
                  <ListItem key={log.id} sx={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                    <ListItemText
                      primary={log.action.replace(/_/g, ' ').toUpperCase()}
                      secondary={`${log.reviewer_id} - ${new Date(log.timestamp).toLocaleString()}`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Button variant="outlined" onClick={() => navigate('/queue')} sx={{ mt: 2 }}>
        Back to Queue
      </Button>
    </Box>
  );
}

export default ReviewPage;
