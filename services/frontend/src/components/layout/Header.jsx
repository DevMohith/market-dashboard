import React from 'react';
import { Link } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { selectUnreadAlerts, selectWebsocketConnectionStatus } from '../../features/alerts/alertsSlice'; // Adjust path as needed

function Header() {
  const unreadAlerts = useSelector(selectUnreadAlerts);
  const isWebsocketConnected = useSelector(selectWebsocketConnectionStatus);

  return (
    <header style={{
      backgroundColor: '#282c34',
      color: 'white',
      padding: '15px 20px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    }}>
      <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
        <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>
          Market Dashboard
        </Link>
      </div>
      <nav>
        <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex' }}>
          <li style={{ marginLeft: '20px' }}>
            <Link to="/watchlist" style={{ color: 'white', textDecoration: 'none' }}>
              Watchlist
            </Link>
          </li>
          <li style={{ marginLeft: '20px' }}>
            <Link to="/relationships" style={{ color: 'white', textDecoration: 'none' }}>
              Relationships
            </Link>
          </li>          
          {/* Alert Indicator */}
          <li style={{ marginLeft: '20px', position: 'relative' }}>
            <span style={{ color: isWebsocketConnected ? 'lightgreen' : 'gray' }}>●</span> {/* Connection status indicator */}
            Alerts {unreadAlerts.length > 0 && (
              <span style={{
                backgroundColor: 'red',
                color: 'white',
                borderRadius: '50%',
                padding: '2px 6px',
                fontSize: '12px',
                position: 'absolute',
                top: '-8px',
                right: '-8px'
              }}>
                {unreadAlerts.length}
              </span>
            )}
          </li>
        </ul>
      </nav>
    </header>
  );
}

export default Header;