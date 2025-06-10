import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import { selectLatestPrices, selectRecentTrades, selectMarketDataWebsocketStatus } from '../features/marketData/marketDataSlice';
import {
  Container, Typography, Box, Paper, Grid, CircularProgress, List, ListItem, ListItemText,
  TextField, Pagination
} from '@mui/material';

function DashboardPage() {
  const latestPrices = useSelector(selectLatestPrices);
  const recentTrades = useSelector(selectRecentTrades);
  const isMarketDataWebsocketConnected = useSelector(selectMarketDataWebsocketStatus);

  const [searchQuery, setSearchQuery] = useState('');
  const [currentPagePrices, setCurrentPagePrices] = useState(1);
  const [currentPageTrades, setCurrentPageTrades] = useState(1);
  
  // --- CHANGED: Number of items to show per page ---
  const itemsPerPage = 7; // Changed from 10 to 7

  // Convert latestPrices object to an array for easier rendering
  const latestPricesArray = Object.entries(latestPrices).map(([symbol, data]) => ({
    symbol,
    name: `${symbol} Co.`, // Dummy name for search, enhance if actual names are available from backend
    ...data,
  }));

  // Filtered and sorted list of latest prices
  const filteredAndSortedPrices = latestPricesArray
    .filter(stock =>
      stock.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (stock.name && stock.name.toLowerCase().includes(searchQuery.toLowerCase()))
    )
    .sort((a, b) => a.symbol.localeCompare(b.symbol));

  // Pagination for Latest Prices
  const totalPagesPrices = Math.ceil(filteredAndSortedPrices.length / itemsPerPage);
  const indexOfLastPrice = currentPagePrices * itemsPerPage;
  const indexOfFirstPrice = indexOfLastPrice - itemsPerPage;
  const currentPrices = filteredAndSortedPrices.slice(indexOfFirstPrice, indexOfLastPrice);

  // Pagination for Recent Trades (assuming recentTrades is also a large list for pagination)
  // Note: Your Redux slice limits `recentTrades` to 20. If you want more, increase the limit there.
  const totalPagesTrades = Math.ceil(recentTrades.length / itemsPerPage);
  const indexOfLastTrade = currentPageTrades * itemsPerPage;
  const indexOfFirstTrade = indexOfLastTrade - itemsPerPage;
  const currentTrades = recentTrades.slice(indexOfFirstTrade, indexOfLastTrade);


  const handlePageChangePrices = (event, value) => {
    setCurrentPagePrices(value);
  };

  const handlePageChangeTrades = (event, value) => {
    setCurrentPageTrades(value);
  };

  const CARD_HEIGHT = 590; // Define a consistent height for the data cards

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

      {/* Search Bar */}
      <Box sx={{ mb: 4 }}>
        <TextField
          label="Search Stocks (Symbol or Name)"
          variant="outlined"
          fullWidth
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            setCurrentPagePrices(1); // Reset to first page on search
          }}
        />
      </Box>

      <Grid container spacing={3}>
        {/* Latest Prices Section */}
        <Grid xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3, height: CARD_HEIGHT, overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h5" gutterBottom>Latest Stock Prices</Typography>
            {currentPrices.length === 0 && searchQuery ? (
              <Typography variant="body1" color="textSecondary">
                No matching stocks for "{searchQuery}"
              </Typography>
            ) : filteredAndSortedPrices.length === 0 ? (
                <Typography variant="body1" color="textSecondary">
                    Waiting for real-time market data...
                </Typography>
            ) : (
              <List dense sx={{ flexGrow: 1 }}>
                {currentPrices.map((stock) => (
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
            {/* Pagination for Prices */}
            {totalPagesPrices > 1 && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                <Pagination
                  count={totalPagesPrices}
                  page={currentPagePrices}
                  onChange={handlePageChangePrices}
                  color="primary"
                />
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Recent Trades Section */}
        <Grid xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3, height: CARD_HEIGHT, overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h5" gutterBottom>Recent Trades</Typography>
            {currentTrades.length === 0 ? (
              <Typography variant="body1" color="textSecondary">
                No recent trades yet.
              </Typography>
            ) : (
              <List dense sx={{ flexGrow: 1 }}>
                {currentTrades.map((trade, index) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={`${trade.symbol}: $${trade.price.toFixed(2)}`}
                      secondary={`at ${new Date(parseInt(trade.timestamp)).toLocaleTimeString()}`}
                    />
                  </ListItem>
                ))}
              </List>
            )}
            {/* Pagination for Trades */}
            {totalPagesTrades > 1 && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                <Pagination
                  count={totalPagesTrades}
                  page={currentPageTrades}
                  onChange={handlePageChangeTrades}
                  color="primary"
                />
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Placeholder for Alerts Summary */}
        <Grid xs={12}>
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
