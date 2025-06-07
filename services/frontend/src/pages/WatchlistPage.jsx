import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { addStock, removeStock, selectWatchlistItems } from '../features/watchlist/watchlistSlice';
import {
  Container, Typography, Box, TextField, Button, List, ListItem,
  ListItemText, ListItemSecondaryAction, IconButton, Paper
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';

function WatchlistPage() {
  const dispatch = useDispatch();
  const watchlist = useSelector(selectWatchlistItems);
  const [newStockSymbol, setNewStockSymbol] = useState('');

  const handleAddStock = () => {
    if (newStockSymbol.trim()) {
      // Dispatch the addStock action with a simple stock object.
      // In a real app, you might fetch stock details first.
      dispatch(addStock({ symbol: newStockSymbol.toUpperCase(), name: newStockSymbol.toUpperCase() + ' Co.' }));
      setNewStockSymbol(''); // Clear input
    }
  };

  const handleRemoveStock = (symbol) => {
    // Dispatch the removeStock action
    dispatch(removeStock(symbol));
  };

  return (
    <Container maxWidth="md">
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 4 }}>
        My Watchlist
      </Typography>

      {/* Add New Stock Section */}
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>Add New Stock</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            label="Stock Symbol (e.g., AAPL)"
            variant="outlined"
            value={newStockSymbol}
            onChange={(e) => setNewStockSymbol(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleAddStock();
              }
            }}
            fullWidth
          />
          <Button
            variant="contained"
            color="primary"
            onClick={handleAddStock}
            sx={{ px: 4 }}
          >
            Add
          </Button>
        </Box>
      </Paper>

      {/* Watchlist Display Section */}
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>Current Watchlist ({watchlist.length} stocks)</Typography>
        {watchlist.length === 0 ? (
          <Typography variant="body1" color="textSecondary">
            Your watchlist is empty. Add some stocks above!
          </Typography>
        ) : (
          <List>
            {watchlist.map((stock) => (
              <ListItem key={stock.symbol} divider>
                <ListItemText
                  primary={stock.name}
                  secondary={stock.symbol}
                  primaryTypographyProps={{ variant: 'h6' }}
                  secondaryTypographyProps={{ variant: 'body2' }}
                />
                <ListItemSecondaryAction>
                  <IconButton edge="end" aria-label="delete" onClick={() => handleRemoveStock(stock.symbol)}>
                    <DeleteIcon color="error" />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        )}
      </Paper>
    </Container>
  );
}

export default WatchlistPage;
