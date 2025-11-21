import React from 'react';
import { Chip } from '@mui/material';

function QualityBadge({ score }) {
  let color = 'default';
  let label = `${(score * 100).toFixed(0)}%`;

  if (score >= 0.9) {
    color = 'success';
  } else if (score >= 0.7) {
    color = 'warning';
  } else {
    color = 'error';
  }

  return <Chip label={label} color={color} size="small" />;
}

export default QualityBadge;
