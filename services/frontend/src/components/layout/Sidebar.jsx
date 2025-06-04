import React from 'react';
import { Link } from 'react-router-dom';
import { Box, Drawer, List, ListItem, ListItemIcon, ListItemText, Typography, Divider } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import WatchlistIcon from '@mui/icons-material/StarBorder';
import RelationshipsIcon from '@mui/icons-material/Share';
//import SettingsIcon from '@mui/icons-material/Settings';

function Sidebar() {
  const drawerWidth = 240;

  return (
    // The Drawer component from Material UI provides a flexible sidebar.
    // 'variant="permanent"' makes it always visible.
    // 'anchor="left"' places it on the left side.
    <Drawer
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          backgroundColor: '#333f50', // Dark background for the sidebar
          color: 'white',
        },
      }}
      variant="permanent"
      anchor="left"
    >
      {/* App Title/Logo Section */}
      <Box sx={{ p: 2, textAlign: 'center', backgroundColor: '#282c34' }}>
        <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 'bold' }}>
          Market Dashboard
        </Typography>
      </Box>
      <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.12)' }} />

      {/* Navigation List */}
      <List>
        {/* Dashboard Link */}
        <ListItem component={Link} to="/" sx={{ '&:hover': { backgroundColor: '#4a576a' } }}>
          <ListItemIcon>
            <DashboardIcon sx={{ color: 'white' }} />
          </ListItemIcon>
          <ListItemText primary="Dashboard" />
        </ListItem>

        {/* Watchlist Link */}
        <ListItem component={Link} to="/watchlist" sx={{ '&:hover': { backgroundColor: '#4a576a' } }}>
          <ListItemIcon>
            <WatchlistIcon sx={{ color: 'white' }} />
          </ListItemIcon>
          <ListItemText primary="Watchlist" />
        </ListItem>

        {/* Relationships Graph Link */}
        <ListItem component={Link} to="/relationships" sx={{ '&:hover': { backgroundColor: '#4a576a' } }}>
          <ListItemIcon>
            <RelationshipsIcon sx={{ color: 'white' }} />
          </ListItemIcon>
          <ListItemText primary="Relationships" />
        </ListItem>

        {/* Settings Link */}
        {/* <ListItem button component={Link} to="/settings" sx={{ '&:hover': { backgroundColor: '#4a576a' } }}>
          <ListItemIcon>
            <SettingsIcon sx={{ color: 'white' }} />
          </ListItemIcon>
          <ListItemText primary="Settings" />
        </ListItem> */}
      </List>
    </Drawer>
  );
}

export default Sidebar;
