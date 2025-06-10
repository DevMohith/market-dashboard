import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  selectWatchlistItems,
  selectWatchlistStatus,
  addStockToWatchlist,
  removeStockFromWatchlist,
  fetchWatchlist,
  saveWatchlist
} from '../features/watchlist/watchlistSlice';
import { selectLatestPrices } from '../features/marketData/marketDataSlice';
import { // Ensure all Material UI components are imported here if used
  Container, Typography, Box, TextField, Button, List, ListItem, ListItemText,
  IconButton, CircularProgress, Alert
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';

function WatchlistPage() {
  const dispatch = useDispatch();
  const watchlistItems = useSelector(selectWatchlistItems);
  const watchlistStatus = useSelector(selectWatchlistStatus); // Status of fetching, not saving
  const latestPrices = useSelector(selectLatestPrices);

  const [newStockSymbol, setNewStockSymbol] = useState('');
  const [saveStatus, setSaveStatus] = useState('idle'); // idle | saving | saved | error

  // Effect to fetch watchlist from backend on component mount (runs only once)
  useEffect(() => {
    dispatch(fetchWatchlist());
  }, [dispatch]);

  // IMPORTANT: The problematic useEffect that was causing infinite saves is REMOVED from here.
  // Saving is now solely triggered by handleAddStock and handleRemoveStock.


  const handleAddStock = async () => {
    if (newStockSymbol.trim() && !watchlistItems.includes(newStockSymbol.toUpperCase())) {
      const stockToAdd = newStockSymbol.toUpperCase();
      // Prepare the updated list for saving to backend
      const updatedWatchlistForSave = [...watchlistItems, stockToAdd]; 
      
      // Optimistic UI update: Dispatch immediately to update Redux state for instant feedback
      dispatch(addStockToWatchlist(stockToAdd)); 
      setNewStockSymbol(''); // Clear input field
      setSaveStatus('saving'); // Show saving indicator

      try {
        // Await the save operation to the backend
        await dispatch(saveWatchlist(updatedWatchlistForSave)).unwrap(); 
        setSaveStatus('saved'); // Indicate success
      } catch (error) {
        setSaveStatus('error'); // Indicate error
        console.error("Failed to save watchlist:", error);
      } finally {
        // Reset save status after a short delay, regardless of success or failure
        const timer = setTimeout(() => setSaveStatus('idle'), 2000); 
        return () => clearTimeout(timer);
      }
    }
  };

  const handleRemoveStock = async (symbol) => {
    // Prepare the updated list for saving to backend
    const updatedWatchlistForSave = watchlistItems.filter(item => item !== symbol);

    // Optimistic UI update: Dispatch immediately to update Redux state
    dispatch(removeStockFromWatchlist(symbol));
    setSaveStatus('saving'); // Show saving indicator

    try {
      // Await the save operation to the backend
      await dispatch(saveWatchlist(updatedWatchlistForSave)).unwrap(); 
      setSaveStatus('saved'); // Indicate success
    } catch (error) {
      setSaveStatus('error'); // Indicate error
      console.error("Failed to save watchlist:", error);
    } finally {
      // Reset save status after a short delay
      const timer = setTimeout(() => setSaveStatus('idle'), 2000);
      return () => clearTimeout(timer);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        My Watchlist
      </Typography>

      <Box sx={{ mb: 3 }}>
        <TextField
          label="Add Stock Symbol"
          variant="outlined"
          value={newStockSymbol}
          onChange={(e) => setNewStockSymbol(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') handleAddStock();
          }}
          sx={{ mr: 2 }}
        />
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddStock}
          disabled={!newStockSymbol.trim() || saveStatus === 'saving'} // Disable button while saving
        >
          Add to Watchlist
        </Button>
      </Box>

      {/* Display status messages for loading and saving */}
      {watchlistStatus === 'loading' && <CircularProgress sx={{ mb: 2 }} />}
      {watchlistStatus === 'failed' && <Alert severity="error">Error loading watchlist.</Alert>}

      {saveStatus === 'saving' && <Typography variant="caption" sx={{ color: 'text.secondary' }}>Saving...</Typography>}
      {saveStatus === 'saved' && <Typography variant="caption" sx={{ color: 'success.main' }}>Watchlist saved!</Typography>}
      {saveStatus === 'error' && <Alert severity="error">Error saving watchlist. Check console for details.</Alert>}

      <List sx={{ width: '100%', bgcolor: 'background.paper', borderRadius: 2, boxShadow: 1 }}>
        {watchlistItems.length === 0 ? (
          <ListItem>
            <ListItemText primary="Your watchlist is empty. Add some stocks!" />
          </ListItem>
        ) : (
          // Map over watchlistItems to display each stock
          watchlistItems.map((symbol) => {
            const stockData = latestPrices[symbol]; // Get live data
            const price = stockData ? `$${parseFloat(stockData.price).toFixed(2)}` : 'N/A';
            const timestamp = stockData ? new Date(parseInt(stockData.timestamp)).toLocaleTimeString() : 'N/A';

            return (
              <ListItem
                key={symbol}
                secondaryAction={
                  <IconButton 
                    edge="end" 
                    aria-label="delete" 
                    onClick={() => handleRemoveStock(symbol)}
                    disabled={saveStatus === 'saving'} // Disable delete button while saving
                  >
                    <DeleteIcon />
                  </IconButton>
                }
              >
                <ListItemText
                  primary={`${symbol}: ${price}`}
                  secondary={`Last updated: ${timestamp}`}
                  primaryTypographyProps={{ variant: 'h6' }}
                  secondaryTypographyProps={{ variant: 'body2', color: 'textSecondary' }}
                />
              </ListItem>
            );
          })
        )}
      </List>
    </Container>
  );
}

export default WatchlistPage;
