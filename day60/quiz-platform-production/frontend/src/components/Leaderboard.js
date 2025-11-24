import React, { useState, useEffect } from 'react';
import {
  Paper, Typography, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, CircularProgress
} from '@mui/material';
import axios from 'axios';

function Leaderboard() {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeaderboard();
  }, []);

  const loadLeaderboard = async () => {
    try {
      const response = await axios.get('/api/leaderboard/');
      setLeaderboard(response.data);
    } catch (error) {
      console.error('Failed to load leaderboard');
    }
    setLoading(false);
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>Leaderboard</Typography>

      {loading ? (
        <CircularProgress />
      ) : (
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Rank</TableCell>
                <TableCell>Username</TableCell>
                <TableCell align="right">Avg Score</TableCell>
                <TableCell align="right">Quiz Count</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {leaderboard.map((user, idx) => (
                <TableRow key={idx}>
                  <TableCell>{idx + 1}</TableCell>
                  <TableCell>{user.username}</TableCell>
                  <TableCell align="right">{user.avg_score}%</TableCell>
                  <TableCell align="right">{user.quiz_count}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Paper>
  );
}

export default Leaderboard;
