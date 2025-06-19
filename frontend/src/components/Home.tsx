import React from 'react';
import { Box, Typography, Button, Paper, Container, Grid } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import DescriptionIcon from '@mui/icons-material/Description';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import SecurityIcon from '@mui/icons-material/Security';

const Home = () => {
  const features = [
    {
      icon: <DescriptionIcon sx={{ fontSize: 40, color: 'var(--primary-500)' }} />,
      title: 'Smart PDF Processing',
      description: 'Upload any PDF and get intelligent summaries powered by advanced AI technology.'
    },
    {
      icon: <AutoAwesomeIcon sx={{ fontSize: 40, color: 'var(--primary-500)' }} />,
      title: 'AI-Powered Summaries',
      description: 'Get comprehensive, well-structured summaries that capture the key insights from your documents.'
    },
    {
      icon: <CloudUploadIcon sx={{ fontSize: 40, color: 'var(--primary-500)' }} />,
      title: 'Easy Upload & Download',
      description: 'Simple drag-and-drop interface with instant preview and download capabilities.'
    },
    {
      icon: <SecurityIcon sx={{ fontSize: 40, color: 'var(--primary-500)' }} />,
      title: 'Secure & Private',
      description: 'Your documents are processed securely with user authentication and private storage.'
    }
  ];

  return (
    <Container maxWidth="lg" sx={{ py: { xs: 4, sm: 6, md: 8 } }}>
      {/* Hero Section */}
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        alignItems: 'center', 
        textAlign: 'center',
        mb: 8
      }}>
        <Paper 
          elevation={0}
          sx={{ 
            p: { xs: 4, sm: 6, md: 8 }, 
            bgcolor: 'var(--bg-secondary)', 
            border: '1px solid var(--border-primary)',
            borderRadius: 'var(--radius-xl)',
            maxWidth: 800,
            position: 'relative',
            overflow: 'hidden',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '4px',
              background: 'linear-gradient(90deg, var(--primary-500), var(--primary-700))',
            }
          }}
        >
          <Typography 
            variant="h2" 
            component="h1"
            sx={{
              fontWeight: 700,
              mb: 3,
              fontSize: { xs: 'var(--font-size-3xl)', sm: 'var(--font-size-4xl)', md: '3.5rem' },
              color: 'var(--text-primary)',
              lineHeight: 'var(--leading-tight)'
            }}
          >
            Welcome to CIM
            <Box 
              component="span"
              sx={{
                background: 'linear-gradient(135deg, #10b981, #059669)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
                fontWeight: 700
              }}
            >
              ez
            </Box>
          </Typography>
          
          <Typography 
            variant="h5" 
            sx={{ 
              mb: 4, 
              color: 'var(--text-secondary)',
              fontSize: { xs: 'var(--font-size-lg)', sm: 'var(--font-size-xl)' },
              lineHeight: 'var(--leading-relaxed)',
              maxWidth: '600px',
              mx: 'auto'
            }}
          >
            Transform your PDF documents into intelligent, comprehensive summaries with our AI-powered processing tool.
          </Typography>
          
          <Button
            variant="contained"
            size="large"
            component={RouterLink}
            to="/convert"
            startIcon={<AutoAwesomeIcon />}
            sx={{ 
              backgroundColor: 'var(--primary-600)',
              color: 'white',
              fontWeight: 600,
              fontSize: 'var(--font-size-lg)',
              px: 4,
              py: 2,
              borderRadius: 'var(--radius-lg)',
              textTransform: 'none',
              boxShadow: 'var(--shadow-lg)',
              '&:hover': {
                backgroundColor: 'var(--primary-700)',
                transform: 'translateY(-2px)',
                boxShadow: 'var(--shadow-xl)'
              }
            }}
          >
            Try PDF Converter
          </Button>
        </Paper>
      </Box>

      {/* Features Section */}
      <Box sx={{ mb: 6 }}>
        <Typography 
          variant="h4" 
          component="h2"
          sx={{ 
            textAlign: 'center',
            mb: 5,
            fontWeight: 600,
            color: 'var(--text-primary)',
            fontSize: { xs: 'var(--font-size-2xl)', sm: 'var(--font-size-3xl)' }
          }}
        >
                     Why Choose CIM<Box component="span" sx={{ color: '#10b981', fontWeight: 700 }}>ez</Box>?
        </Typography>
        
        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Paper
                elevation={0}
                sx={{
                  p: 4,
                  height: '100%',
                  textAlign: 'center',
                  backgroundColor: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-primary)',
                  borderRadius: 'var(--radius-lg)',
                  transition: 'all 0.3s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 'var(--shadow-xl)',
                    borderColor: 'var(--border-secondary)',
                  }
                }}
              >
                <Box sx={{ mb: 2 }}>
                  {feature.icon}
                </Box>
                <Typography 
                  variant="h6" 
                  component="h3"
                  sx={{ 
                    mb: 2,
                    fontWeight: 600,
                    color: 'var(--text-primary)',
                    fontSize: 'var(--font-size-lg)'
                  }}
                >
                  {feature.title}
                </Typography>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    color: 'var(--text-secondary)',
                    lineHeight: 'var(--leading-relaxed)',
                    fontSize: 'var(--font-size-sm)'
                  }}
                >
                  {feature.description}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Container>
  );
};

export default Home; 