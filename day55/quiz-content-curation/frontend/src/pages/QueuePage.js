import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Paper, Table, TableBody, TableCell, TableContainer, TableHead,
  TableRow, Button, Typography, Box, Chip, Tabs, Tab,
  CircularProgress, Alert
} from '@mui/material';
import QualityBadge from '../components/QualityBadge';
import { curationApi } from '../services/api';

function QueuePage() {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [status, setStatus] = useState('pending');
  const [total, setTotal] = useState(0);
  const navigate = useNavigate();

  const reviewerId = 'admin';

  useEffect(() => {
    fetchQueue();
  }, [status]);

  const fetchQueue = async () => {
    setLoading(true);
    try {
      const data = await curationApi.getQueue(status);
      setQueue(data.items);
      setTotal(data.total);
      setError(null);
    } catch (err) {
      setError('Failed to load queue');
    }
    setLoading(false);
  };

  const handleClaim = async (id) => {
    try {
      await curationApi.claim(id, reviewerId);
      navigate(`/review/${id}`);
    } catch (err) {
      setError('Failed to claim content');
    }
  };

  const handleViewReview = (id) => {
    navigate(`/review/${id}`);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Curation Queue
      </Typography>

      <Tabs value={status} onChange={(e, v) => setStatus(v)} sx={{ mb: 2 }}>
        <Tab value="pending" label="Pending" />
        <Tab value="under_review" label="Under Review" />
        <Tab value="approved" label="Approved" />
        <Tab value="rejected" label="Rejected" />
        <Tab value="needs_revision" label="Needs Revision" />
      </Tabs>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {loading ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Preview</TableCell>
                <TableCell>Quality</TableCell>
                <TableCell>Topic</TableCell>
                <TableCell>Difficulty</TableCell>
                <TableCell>Age</TableCell>
                <TableCell>Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {queue.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    No items in queue
                  </TableCell>
                </TableRow>
              ) : (
                queue.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell sx={{ maxWidth: 300 }}>
                      {item.preview}
                    </TableCell>
                    <TableCell>
                      <QualityBadge score={item.quality_score} />
                    </TableCell>
                    <TableCell>
                      <Chip label={item.topic} size="small" />
                    </TableCell>
                    <TableCell>{item.difficulty}</TableCell>
                    <TableCell>{item.time_in_queue}</TableCell>
                    <TableCell>
                      {status === 'pending' ? (
                        <Button
                          variant="contained"
                          size="small"
                          onClick={() => handleClaim(item.id)}
                        >
                          Review
                        </Button>
                      ) : (
                        <Button
                          variant="outlined"
                          size="small"
                          onClick={() => handleViewReview(item.id)}
                        >
                          View
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
        Total: {total} items
      </Typography>
    </Box>
  );
}

export default QueuePage;
