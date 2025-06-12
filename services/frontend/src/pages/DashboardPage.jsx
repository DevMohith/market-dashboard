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
  
  const itemsPerPage = 7; 

  const latestPricesArray = Object.entries(latestPrices).map(([symbol, data]) => ({
    symbol,
    name: `${symbol} Co.`, // Dummy name for search, enhance if actual names are available from backend
    ...data,
  }));

  const filteredAndSortedPrices = latestPricesArray
    .filter(stock =>
      stock.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (stock.name && stock.name.toLowerCase().includes(searchQuery.toLowerCase()))
    )
    .sort((a, b) => a.symbol.localeCompare(b.symbol));

  const totalPagesPrices = Math.ceil(filteredAndSortedPrices.length / itemsPerPage);
  const indexOfLastPrice = currentPagePrices * itemsPerPage;
  const indexOfFirstPrice = indexOfLastPrice - itemsPerPage;
  const currentPrices = filteredAndSortedPrices.slice(indexOfFirstPrice, indexOfLastPrice);

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
    // Max width set to "xl" for wider content, centered automatically by Container
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}> 
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 4, textAlign: 'center', fontWeight: 'bold', color: '#2c3e50' }}>
        Market Intelligence Dashboard
      </Typography>

      {/* WebSocket Connection Status */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="body1" sx={{ color: isMarketDataWebsocketConnected ? '#2ecc71' : '#e74c3c', fontWeight: 'medium' }}>
          Market Data WebSocket Status: {isMarketDataWebsocketConnected ? 'Connected' : 'Disconnected'}
          {!isMarketDataWebsocketConnected && <CircularProgress size={16} sx={{ ml: 1, color: '#e74c3c' }} />}
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
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 2, // Rounded corners
              '&.Mui-focused fieldset': {
                borderColor: '#3498db', // Blue border on focus
              },
            },
            '& .MuiInputLabel-root': {
              color: '#34495e', // Darker label
            },
          }}
        />
      </Box>

      <Grid container spacing={4} justifyContent="center"> {/* Increased spacing and centered grid items */}
        {/* Latest Prices Section */}
        <Grid item xs={12} md={6} lg={5.5}> {/* Adjusted grid size for wider cards, allowing for spacing */}
          <Paper 
            elevation={6} // Increased elevation for more prominence
            sx={{ 
              p: 3, 
              height: CARD_HEIGHT, 
              overflowY: 'auto', 
              display: 'flex', 
              flexDirection: 'column',
              borderRadius: 3, // More rounded corners
              boxShadow: '0px 10px 20px rgba(0, 0, 0, 0.1)', // Subtle shadow
              border: '1px solid #e0e0e0', // Light border
            }}
          >
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', color: '#34495e', borderBottom: '2px solid #3498db', pb: 1 }}>
              Latest Stock Prices
            </Typography>
            {currentPrices.length === 0 && searchQuery ? (
              <Typography variant="body1" color="textSecondary" sx={{ mt: 2 }}>
                No matching stocks for "{searchQuery}"
              </Typography>
            ) : filteredAndSortedPrices.length === 0 ? (
              <Typography variant="body1" color="textSecondary" sx={{ mt: 2 }}>
                {isMarketDataWebsocketConnected ? 'Market Closed - No live data available' : 'Waiting for real-time market data...'}
              </Typography>
            ) : (
              <List dense sx={{ flexGrow: 1, mt: 1 }}>
                {currentPrices.map((stock) => (
                  <ListItem 
                    key={stock.symbol} 
                    sx={{ 
                      borderRadius: 1, 
                      mb: 1, 
                      '&:hover': { backgroundColor: '#f5f5f5' }, // Light hover for list items
                      transition: 'background-color 0.3s ease',
                      borderLeft: '4px solid #3498db', // Accent border on left
                      p: 1.5 // Increased padding for list items
                    }}
                  >
                    <ListItemText
                      primary={
                        <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#2c3e50' }}>
                          {stock.symbol}: <span style={{ color: '#27ae60' }}>${stock.price.toFixed(2)}</span>
                        </Typography>
                      }
                      secondary={
                        <Typography variant="body2" color="textSecondary">
                          Last updated: {new Date(parseInt(stock.timestamp)).toLocaleTimeString()}
                        </Typography>
                      }
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
        <Grid item xs={12} md={6} lg={5.5}> {/* Adjusted grid size for wider cards */}
          <Paper 
            elevation={6} 
            sx={{ 
              p: 3, 
              height: CARD_HEIGHT, 
              overflowY: 'auto', 
              display: 'flex', 
              flexDirection: 'column',
              borderRadius: 3, 
              boxShadow: '0px 10px 20px rgba(0, 0, 0, 0.1)', 
              border: '1px solid #e0e0e0', 
            }}
          >
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', color: '#34495e', borderBottom: '2px solid #e74c3c', pb: 1 }}>
              Recent Trades
            </Typography>
            {currentTrades.length === 0 ? (
              <Typography variant="body1" color="textSecondary" sx={{ mt: 2 }}>
                No recent trades yet.
              </Typography>
            ) : (
              <List dense sx={{ flexGrow: 1, mt: 1 }}>
                {currentTrades.map((trade, index) => (
                  <ListItem 
                    key={index} 
                    sx={{ 
                      borderRadius: 1, 
                      mb: 1, 
                      '&:hover': { backgroundColor: '#f5f5f5' }, 
                      transition: 'background-color 0.3s ease',
                      borderLeft: '4px solid #e74c3c', // Accent border on left
                      p: 1.5 
                    }}
                  >
                    <ListItemText
                      primary={
                        <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#2c3e50' }}>
                          {trade.symbol}: <span style={{ color: '#27ae60' }}>${trade.price.toFixed(2)}</span>
                        </Typography>
                      }
                      secondary={
                        <Typography variant="body2" color="textSecondary">
                          at {new Date(parseInt(trade.timestamp)).toLocaleTimeString()}
                        </Typography>
                      }
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
                  color="secondary" // Using secondary color for trades pagination
                />
              </Box>
            )}
          </Paper>
        </Grid>

        
      </Grid>
    </Container>
  );
}

export default DashboardPage;