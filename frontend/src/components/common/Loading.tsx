import React from 'react';
import { CircularProgress, Box, Typography } from '@mui/material';

const Loading: React.FC = () => {
  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
      <CircularProgress size={60} />
      <Box mt={2}>
        <Typography variant="body2">Loading...</Typography>
      </Box>
    </Box>
  );
};

export default Loading;