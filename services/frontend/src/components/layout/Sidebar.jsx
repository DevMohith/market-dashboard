import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Box, Drawer, List, ListItem, ListItemIcon, ListItemText, Typography, Divider } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import WatchlistIcon from '@mui/icons-material/StarBorder';
import RelationshipsIcon from '@mui/icons-material/Share';
//import SettingsIcon from '@mui/icons-material/Settings';

function Sidebar() {
  // Increased drawerWidth for a wider sidebar
  const drawerWidth = 280; // Changed from 240 to 280

  const location = useLocation();

  const navItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Watchlist', icon: <WatchlistIcon />, path: '/watchlist' },
    { text: 'Relationships', icon: <RelationshipsIcon />, path: '/relationships' },
    // { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
  ];

  return (
    <Drawer
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          background: 'linear-gradient(to bottom, #2c3e50, #34495e)',
          color: 'white',
          boxShadow: '4px 0px 10px rgba(0, 0, 0, 0.3)',
          borderRight: '1px solid rgba(255, 255, 255, 0.1)',
        },
      }}
      variant="permanent"
      anchor="left"
    >
      {/* App Title/Logo Section */}
      <Box
        sx={{
          p: 3,
          textAlign: 'center',
          background: 'linear-gradient(to right, #3498db, #2980b9)',
          color: 'white',
          borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
          boxShadow: '0px 2px 5px rgba(0,0,0,0.2)'
        }}
      >
        <Typography variant="h5" noWrap component="div" sx={{ fontWeight: 'bold', letterSpacing: 1 }}>
          Market Dashboard
        </Typography>
      </Box>
      <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.12)' }} />

      {/* Navigation List */}
      <List>
        {navItems.map((item) => (
          <ListItem
            key={item.text}
            component={Link}
            to={item.path}
            sx={{
              color: 'white',
              py: 1.5,
              px: 2,
              borderRadius: 1,
              mx: 1,
              mb: 0.5,
              transition: 'background-color 0.3s ease, color 0.3s ease',
              backgroundColor: location.pathname === item.path ? '#3498db' : 'transparent',
              '&:hover': {
                backgroundColor: '#2980b9',
                color: 'white',
              },
            }}
          >
            <ListItemIcon sx={{ color: 'inherit' }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={<Typography variant="body1" sx={{ fontWeight: 'medium' }}>{item.text}</Typography>} />
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
}

export default Sidebar;
