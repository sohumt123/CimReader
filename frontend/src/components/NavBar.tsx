import React from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from './Auth';

const NavBar = () => {
  const { session, openModal, handleSignOut } = useAuth();
  return (
    <AppBar position="static" color="default" sx={{ bgcolor: '#181c24', color: '#fff', boxShadow: 2 }}>
      <Toolbar>
        <Typography variant="h6" component={RouterLink} to="/" sx={{ flexGrow: 1, textDecoration: 'none', color: 'inherit', fontWeight: 700 }}>
          4C Tool
        </Typography>
        <Button color="inherit" component={RouterLink} to="/" sx={{ fontWeight: 500 }}>
          Home
        </Button>
        <Button color="inherit" component={RouterLink} to="/convert" sx={{ fontWeight: 500 }}>
          PDF Converter
        </Button>
        <Box sx={{ flexGrow: 0, ml: 2 }}>
          {session ? (
            <>
              <Typography variant="body2" sx={{ display: 'inline', mr: 1, color: '#b0b8c1' }}>
                {session.user.email}
              </Typography>
              <Button color="inherit" onClick={handleSignOut} sx={{ fontWeight: 500 }}>
                Sign Out
              </Button>
            </>
          ) : (
            <Button color="inherit" onClick={openModal} sx={{ fontWeight: 500 }}>
              Sign In
            </Button>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default NavBar; 