import React from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const Home = () => {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '70vh' }}>
      <Paper elevation={6} sx={{ p: 5, bgcolor: '#23272f', color: '#fff', maxWidth: 600, textAlign: 'center', borderRadius: 4 }}>
        <Typography variant="h3" fontWeight={700} gutterBottom>
          Welcome to 4C Tool
        </Typography>
        <Typography variant="h6" sx={{ mb: 3, color: '#b0b8c1' }}>
          Your all-in-one solution for converting and enhancing PDF documents with AI.
        </Typography>
        <Button
          variant="contained"
          color="primary"
          size="large"
          component={RouterLink}
          to="/convert"
          sx={{ mt: 2, fontWeight: 600 }}
        >
          Try PDF Converter
        </Button>
      </Paper>
    </Box>
  );
};

export default Home; 