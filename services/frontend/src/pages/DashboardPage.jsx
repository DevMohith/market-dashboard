import React from 'react';
import { useSelector } from 'react-redux';
import { selectLatestPrices, selectRecentTrades, selectMarketDataWebsocketStatus } from '../features/marketData/marketDataSlice';
import { Container, Typography, Box, Paper, Grid, CircularProgress, List, ListItem, ListItemText } from '@mui/material';

function DashboardPage() {
  const latestPrices = useSelector(selectLatestPrices);
  const recentTrades = useSelector(selectRecentTrades);
  const isMarketDataWebsocketConnected = useSelector(selectMarketDataWebsocketStatus);

  // Convert latestPrices object to an array for easier rendering
  const latestPricesArray = Object.entries(latestPrices).map(([symbol, data]) => ({
    symbol,
    ...data,
  }));

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 4 }}>
        Market Intelligence Dashboard
      </Typography>

      {/* WebSocket Connection Status */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="body1" color={isMarketDataWebsocketConnected ? 'success.main' : 'error.main'}>
          Market Data WebSocket Status: {isMarketDataWebsocketConnected ? 'Connected' : 'Disconnected'}
          {!isMarketDataWebsocketConnected && <CircularProgress size={16} sx={{ ml: 1 }} />}
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Latest Prices Section */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3, minHeight: '300px' }}>
            <Typography variant="h5" gutterBottom>Latest Stock Prices</Typography>
            {latestPricesArray.length === 0 ? (
              <Typography variant="body1" color="textSecondary">
                Waiting for real-time market data...
              </Typography>
            ) : (
              <List dense>
                {latestPricesArray
                  .sort((a, b) => a.symbol.localeCompare(b.symbol)) // Sort alphabetically
                  .map((stock) => (
                    <ListItem key={stock.symbol}>
                      <ListItemText
                        primary={`${stock.symbol}: $${stock.price.toFixed(2)}`}
                        secondary={`Last updated: ${new Date(parseInt(stock.timestamp)).toLocaleTimeString()}`}
                        primaryTypographyProps={{ variant: 'h6' }}
                        secondaryTypographyProps={{ variant: 'body2', color: 'textSecondary' }}
                      />
                    </ListItem>
                  ))}
              </List>
            )}
          </Paper>
        </Grid>

        {/* Recent Trades Section */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3, minHeight: '300px' }}>
            <Typography variant="h5" gutterBottom>Recent Trades</Typography>
            {recentTrades.length === 0 ? (
              <Typography variant="body1" color="textSecondary">
                No recent trades yet.
              </Typography>
            ) : (
              <List dense>
                {recentTrades.map((trade, index) => (
                  <ListItem key={index}> {/* Using index as key for simplicity, unique ID better in production */}
                    <ListItemText
                      primary={`${trade.symbol}: $${trade.price.toFixed(2)}`}
                      secondary={`at ${new Date(parseInt(trade.timestamp)).toLocaleTimeString()}`}
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
        </Grid>

        {/* Placeholder for Alerts Summary */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>Alerts Summary</Typography>
            <Typography variant="body2" color="textSecondary">
              (This section would display a summary of recent anomaly alerts from your Alerts Microservice.)
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default DashboardPage;
