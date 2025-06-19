import React from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import { useAuth } from './Auth';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import LogoutIcon from '@mui/icons-material/Logout';
import LoginIcon from '@mui/icons-material/Login';

const NavBar = () => {
  const { session, openModal, handleSignOut } = useAuth();
  const location = useLocation();
  
  const isActive = (path: string) => location.pathname === path;
  
  return (
    <AppBar 
      position="static" 
      elevation={0}
      sx={{ 
        bgcolor: 'var(--bg-secondary)', 
        borderBottom: '1px solid var(--border-primary)',
        boxShadow: 'var(--shadow-sm)'
      }}
    >
      <Toolbar sx={{ px: { xs: 2, sm: 3, md: 4 }, py: 1 }}>
        <Typography 
          variant="h5" 
          component={RouterLink} 
          to="/" 
          sx={{ 
            flexGrow: 1, 
            textDecoration: 'none', 
            color: 'var(--text-primary)', 
            fontWeight: 700,
            fontSize: { xs: 'var(--font-size-xl)', sm: 'var(--font-size-2xl)' }
          }}
        >
          📄 CIM
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
        
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <Button 
            component={RouterLink} 
            to="/" 
            sx={{ 
              color: isActive('/') ? 'var(--primary-500)' : 'var(--text-secondary)',
              fontWeight: 500,
              fontSize: 'var(--font-size-sm)',
              textTransform: 'none',
              borderRadius: 'var(--radius-md)',
              px: 2,
              py: 1,
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                backgroundColor: 'var(--bg-tertiary)',
                color: 'var(--primary-500)',
                transform: 'translateY(-1px)'
              },
              ...(isActive('/') && {
                backgroundColor: 'var(--bg-tertiary)',
                color: 'var(--primary-500)'
              })
            }}
          >
            Home
          </Button>
          
          <Button 
            component={RouterLink} 
            to="/convert" 
            sx={{ 
              color: isActive('/convert') ? 'var(--primary-500)' : 'var(--text-secondary)',
              fontWeight: 500,
              fontSize: 'var(--font-size-sm)',
              textTransform: 'none',
              borderRadius: 'var(--radius-md)',
              px: 2,
              py: 1,
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                backgroundColor: 'var(--bg-tertiary)',
                color: 'var(--primary-500)',
                transform: 'translateY(-1px)'
              },
              ...(isActive('/convert') && {
                backgroundColor: 'var(--bg-tertiary)',
                color: 'var(--primary-500)'
              })
            }}
          >
            PDF Converter
          </Button>
          
          {session && (
            <Button 
              component={RouterLink} 
              to="/summaries" 
              sx={{ 
                color: isActive('/summaries') ? 'var(--primary-500)' : 'var(--text-secondary)',
                fontWeight: 500,
                fontSize: 'var(--font-size-sm)',
                textTransform: 'none',
                borderRadius: 'var(--radius-md)',
                px: 2,
                py: 1,
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  backgroundColor: 'var(--bg-tertiary)',
                  color: 'var(--primary-500)',
                  transform: 'translateY(-1px)'
                },
                ...(isActive('/summaries') && {
                  backgroundColor: 'var(--bg-tertiary)',
                  color: 'var(--primary-500)'
                })
              }}
            >
              My Summaries
            </Button>
          )}
        </Box>
        
        <Box sx={{ flexGrow: 0, ml: 3 }}>
          {session ? (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Chip
                icon={<AccountCircleIcon />}
                label={session.user.email}
                variant="outlined"
                sx={{
                  borderColor: 'var(--border-primary)',
                  color: 'var(--text-secondary)',
                  fontSize: 'var(--font-size-xs)',
                  '& .MuiChip-icon': {
                    color: 'var(--primary-500)'
                  }
                }}
              />
              <Button 
                onClick={handleSignOut} 
                startIcon={<LogoutIcon />}
                sx={{ 
                  color: 'var(--text-secondary)',
                  fontWeight: 500,
                  fontSize: 'var(--font-size-sm)',
                  textTransform: 'none',
                  borderRadius: 'var(--radius-md)',
                  px: 2,
                  py: 1,
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    backgroundColor: 'var(--error-bg)',
                    color: 'var(--error)',
                    transform: 'translateY(-1px)'
                  }
                }}
              >
                Sign Out
              </Button>
            </Box>
          ) : (
            <Button 
              onClick={openModal} 
              startIcon={<LoginIcon />}
              variant="contained"
              sx={{ 
                backgroundColor: 'var(--primary-600)',
                color: 'white',
                fontWeight: 600,
                fontSize: 'var(--font-size-sm)',
                textTransform: 'none',
                borderRadius: 'var(--radius-md)',
                px: 3,
                py: 1,
                '&:hover': {
                  backgroundColor: 'var(--primary-700)',
                  transform: 'translateY(-1px)',
                  boxShadow: 'var(--shadow-lg)'
                }
              }}
            >
              Sign In
            </Button>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default NavBar; 