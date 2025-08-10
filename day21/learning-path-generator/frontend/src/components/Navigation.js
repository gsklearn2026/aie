import React from 'react';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Button, 
  Box,
  IconButton,
  Avatar 
} from '@mui/material';
import { 
  Dashboard,
  Psychology,
  TrendingUp,
  School,
  AccountCircle 
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

function Navigation() {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { path: '/', label: 'Dashboard', icon: Dashboard },
    { path: '/generate', label: 'Generate Path', icon: Psychology },
    { path: '/progress', label: 'Progress', icon: TrendingUp },
    { path: '/topics', label: 'Topics', icon: School },
  ];

  return (
    <AppBar 
      position="static" 
      elevation={0}
      sx={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderBottom: '1px solid rgba(255,255,255,0.1)'
      }}
    >
      <Toolbar>
        <Typography 
          variant="h6" 
          component="div" 
          sx={{ 
            flexGrow: 0, 
            fontWeight: 700,
            mr: 4,
            display: 'flex',
            alignItems: 'center',
            gap: 1
          }}
        >
          <Psychology />
          Learning Path AI
        </Typography>
        
        <Box sx={{ flexGrow: 1, display: 'flex', gap: 1 }}>
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <Button
                key={item.path}
                onClick={() => navigate(item.path)}
                startIcon={<Icon />}
                sx={{ 
                  color: 'white',
                  fontWeight: isActive ? 600 : 400,
                  bgcolor: isActive ? 'rgba(255,255,255,0.15)' : 'transparent',
                  '&:hover': {
                    bgcolor: 'rgba(255,255,255,0.1)',
                  },
                  borderRadius: 2,
                  px: 2
                }}
              >
                {item.label}
              </Button>
            );
          })}
        </Box>

        <IconButton 
          sx={{ color: 'white' }}
          onClick={() => navigate('/profile')}
        >
          <Avatar sx={{ width: 32, height: 32, bgcolor: 'rgba(255,255,255,0.2)' }}>
            <AccountCircle />
          </Avatar>
        </IconButton>
      </Toolbar>
    </AppBar>
  );
}

export default Navigation;
