import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Avatar,
  Box,
  CircularProgress
} from '@mui/material';
import { EmojiEvents, Person } from '@mui/icons-material';
import { fetchTopPerformers } from '../../services/api';

function TopPerformersTable() {
  const [performers, setPerformers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTopPerformers();
  }, []);

  const loadTopPerformers = async () => {
    try {
      const response = await fetchTopPerformers();
      setPerformers(response.data.data);
    } catch (error) {
      console.error('Error loading top performers:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRankColor = (index) => {
    switch (index) {
      case 0: return 'gold';
      case 1: return 'silver';
      case 2: return '#cd7f32';
      default: return 'primary';
    }
  };

  if (loading) {
    return (
      <Paper sx={{ p: 2 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
          <CircularProgress />
        </Box>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2 }}>
      <Box display="flex" alignItems="center" mb={2}>
        <EmojiEvents sx={{ mr: 1, color: 'gold' }} />
        <Typography variant="h6">
          Top Performers
        </Typography>
      </Box>
      
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Rank</TableCell>
              <TableCell>User</TableCell>
              <TableCell align="right">Avg Score</TableCell>
              <TableCell align="right">Sessions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {performers.slice(0, 5).map((performer, index) => (
              <TableRow key={`${performer.user_id}-${index}`}>
                <TableCell>
                  <Chip 
                    size="small"
                    label={`#${index + 1}`}
                    sx={{ 
                      bgcolor: index < 3 ? getRankColor(index) : 'default',
                      color: index < 3 ? 'white' : 'default'
                    }}
                  />
                </TableCell>
                <TableCell>
                  <Box display="flex" alignItems="center">
                    <Avatar sx={{ width: 24, height: 24, mr: 1 }}>
                      <Person fontSize="small" />
                    </Avatar>
                    <Box>
                      <Typography variant="body2" fontWeight="medium">
                        {performer.full_name || performer.username}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        @{performer.username}
                      </Typography>
                    </Box>
                  </Box>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body2" fontWeight="bold" color="primary">
                    {performer.average_score}%
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body2">
                    {performer.sessions_completed}
                  </Typography>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
}

export default TopPerformersTable;
