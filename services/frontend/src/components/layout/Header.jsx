import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { selectUnreadAlerts, selectWebsocketConnectionStatus, markAlertAsRead, clearAlerts } from '../../features/alerts/alertsSlice';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Badge,
  Menu,
  MenuItem,
  Box,
  Divider,
  ListItemText // <--- ADD THIS LINE
} from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';
import CloseIcon from '@mui/icons-material/Close';

function Header() {
  const dispatch = useDispatch();
  const unreadAlerts = useSelector(selectUnreadAlerts);
  const isWebsocketConnected = useSelector(selectWebsocketConnectionStatus);

  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleMarkAsRead = (alertId) => {
    dispatch(markAlertAsRead(alertId));
    if (unreadAlerts.length === 1) {
        setAnchorEl(null);
    }
  };

  const handleClearAllAlerts = () => {
    dispatch(clearAlerts());
    setAnchorEl(null);
  };

  return (
    <AppBar position="static" sx={{ backgroundColor: '#282c34', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
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
          <Button color="inherit" component={Link} to="/settings">
            Settings
          </Button>

          {/* Alert Indicator and Dropdown */}
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
          <Menu
            anchorEl={anchorEl}
            open={open}
            onClose={handleMenuClose}
            MenuListProps={{
              'aria-labelledby': 'basic-button',
            }}
          >
            <MenuItem disabled>
                <Typography variant="subtitle2" sx={{fontWeight: 'bold'}}>Notifications</Typography>
            </MenuItem>
            <Divider />
            {unreadAlerts.length === 0 ? (
              <MenuItem onClick={handleMenuClose}>No new alerts</MenuItem>
            ) : (
              <>
                {unreadAlerts.map((alert) => (
                  <MenuItem key={alert.id} onClick={() => handleMarkAsRead(alert.id)}>
                    <ListItemText // This is the component that was not defined
                      primary={alert.symbol + ": " + alert.message}
                      secondary={new Date(parseInt(alert.timestamp)).toLocaleString()} // Ensure timestamp is parsed
                    />
                    <IconButton edge="end" size="small" onClick={(e) => { e.stopPropagation(); handleMarkAsRead(alert.id); }}>
                        <CloseIcon fontSize="small" />
                    </IconButton>
                  </MenuItem>
                ))}
                <Divider />
                <MenuItem onClick={handleClearAllAlerts}>
                  <Typography color="primary">Clear All Alerts</Typography>
                </MenuItem>
              </>
            )}
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Header;
