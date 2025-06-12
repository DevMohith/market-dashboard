import React, { useState } from 'react';
import TrendingStocks from './TrendingStocks';
import { Link } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import {
  selectUnreadAlerts,
  selectWebsocketConnectionStatus,
  markAlertAsRead,
  clearAlerts
} from '../../features/alerts/alertsSlice';

import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Badge,
  Menu, // Make sure Menu is imported 
  MenuItem,
  Box,
  Divider,
  ListItemText
} from '@mui/material';

import NotificationsIcon from '@mui/icons-material/Notifications';
import CloseIcon from '@mui/icons-material/Close';

function Header() {
  const dispatch = useDispatch();
  const unreadAlerts = useSelector(selectUnreadAlerts);
  const isWebsocketConnected = useSelector(selectWebsocketConnectionStatus);

  const [anchorEl, setAnchorEl] = useState(null);
  const [showTrending, setShowTrending] = useState(false); // 🔧 Required

  const open = Boolean(anchorEl);

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleMarkAsRead = (alertId) => {
    dispatch(markAlertAsRead(alertId));
    if (unreadAlerts.length === 1) { // If this was the last unread alert, close the menu
      setAnchorEl(null);
    }
  };

  const handleClearAllAlerts = () => {
    dispatch(clearAlerts());
    setAnchorEl(null); // Close menu after clearing
  };

  return (
    <>
      <AppBar position="static" sx={{ backgroundColor: '#282c34' }}>
        <Toolbar>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>
              Market Dashboard
            </Link>
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Button color="inherit" component={Link} to="/watchlist">
              Watchlist
            </Button>
            <Button color="inherit" component={Link} to="/relationships">
              Relationships
            </Button>
            {/* <Button color="inherit" component={Link} to="/settings">
              Settings
            </Button> */}

            {/* 🔥 Trending Stocks Button */}
            <Button
              onClick={() => setShowTrending(true)}
              sx={{
                ml: 2,
                background: 'linear-gradient(to right, #ff416c, #ff4b2b)',
                color: 'white',
                fontWeight: 'bold',
                '&:hover': {
                  background: '#ff4b2b',
                }
              }}
            >
              🔥 Trending Stocks
            </Button>

            <IconButton
              color="inherit"
              aria-label="show alerts"
              onClick={handleMenuClick}
              sx={{ ml: 2 }}
            >
              <Badge badgeContent={unreadAlerts.length} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
            <Typography variant="caption" sx={{ ml: 1, color: isWebsocketConnected ? 'lightgreen' : 'gray' }}>
              ●
            </Typography>
          </Box>
        </Toolbar>
      </AppBar>

      {/* 🔔 Alert Notifications Menu */}
      <Menu
        id="alerts-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleMenuClose}
        MenuListProps={{
          'aria-labelledby': 'alerts-icon-button',
        }}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        {unreadAlerts.length === 0 ? (
          <MenuItem onClick={handleMenuClose}>
            <ListItemText primary="No new alerts" />
          </MenuItem>
        ) : (
          <>
            {unreadAlerts.map((alert) => (
              <MenuItem key={alert.id} onClick={() => handleMarkAsRead(alert.id)}>
                <ListItemText 
                  primary={alert.message} 
                  secondary={new Date(alert.timestamp).toLocaleTimeString()}
                />
                <IconButton 
                  size="small" 
                  onClick={(e) => { e.stopPropagation(); handleMarkAsRead(alert.id); }}
                  sx={{ ml: 1 }}
                >
                  <CloseIcon fontSize="small" />
                </IconButton>
              </MenuItem>
            ))}
            <Divider />
            <MenuItem onClick={handleClearAllAlerts}>
              <Button size="small" fullWidth>
                Clear All Alerts
              </Button>
            </MenuItem>
          </>
        )}
      </Menu>

      {/* 🔳 Modal: Trending Stocks */}
      <TrendingStocks open={showTrending} onClose={() => setShowTrending(false)} />
    </>
  );
}

export default Header;
