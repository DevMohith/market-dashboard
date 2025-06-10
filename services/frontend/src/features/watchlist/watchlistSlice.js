import { createSlice, createAsyncThunk, createSelector } from '@reduxjs/toolkit';
import { getPseudoUserId } from '../../utils/userId'; // Import pseudo user ID utility

// Async Thunk to fetch watchlist from backend
export const fetchWatchlist = createAsyncThunk(
  'watchlist/fetchWatchlist',
  async (_, { rejectWithValue }) => {
    try {
      const userId = getPseudoUserId();
      const response = await fetch(`${import.meta.env.VITE_APP_WATCHLIST_API_URL}/watchlist/${userId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch watchlist');
      }
      const data = await response.json();
      return data.stocks; // Assuming the backend returns { user_id: "...", stocks: ["AAPL", "MSFT"] }
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

// Async Thunk to save watchlist to backend
export const saveWatchlist = createAsyncThunk(
  'watchlist/saveWatchlist',
  async (stocks, { rejectWithValue }) => {
    try {
      const userId = getPseudoUserId();
      const response = await fetch(`${import.meta.env.VITE_APP_WATCHLIST_API_URL}/watchlist`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId, stocks }),
      });
      if (!response.ok) {
        throw new Error('Failed to save watchlist');
      }
      const data = await response.json();
      return data.stocks; // Return the confirmed list of stocks
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);


const watchlistSlice = createSlice({
  name: 'watchlist',
  initialState: {
    items: [], // Array of stock symbols, e.g., ["AAPL", "MSFT"]
    status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
    error: null,
  },
  reducers: {
    addStockToWatchlist: (state, action) => {
      const stockSymbol = action.payload.toUpperCase();
      if (!state.items.includes(stockSymbol)) {
        state.items.push(stockSymbol);
      }
    },
    removeStockFromWatchlist: (state, action) => {
      const stockSymbol = action.payload.toUpperCase();
      state.items = state.items.filter(item => item !== stockSymbol);
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Watchlist
      .addCase(fetchWatchlist.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchWatchlist.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.items = action.payload;
      })
      .addCase(fetchWatchlist.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      })
      // Save Watchlist
      .addCase(saveWatchlist.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(saveWatchlist.fulfilled, (state, action) => {
        state.status = 'succeeded';
        // The items are already updated by add/remove reducers,
        // this just confirms saving was successful or updates if backend returned changed list
        state.items = action.payload;
      })
      .addCase(saveWatchlist.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload;
      });
  },
});

export const { addStockToWatchlist, removeStockFromWatchlist } = watchlistSlice.actions;

export const selectWatchlistItems = (state) => state.watchlist.items;
export const selectWatchlistStatus = (state) => state.watchlist.status;

export default watchlistSlice.reducer;
