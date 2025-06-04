import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
// import { fetchWatchlistApi, addStockToWatchlistApi, removeStockFromWatchlistApi } from '../../services/watchlistService'; // You'll create these

const watchlistSlice = createSlice({
  name: 'watchlist',
  initialState: {
    items: [], // Array of stock symbols or objects {symbol: 'AAPL', name: 'Apple'}
    status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
    error: null,
  },
  reducers: {
    addStock: (state, action) => {
      // Ensure no duplicates
      if (!state.items.some(item => item.symbol === action.payload.symbol)) {
        state.items.push(action.payload);
      }
    },
    removeStock: (state, action) => {
      state.items = state.items.filter(item => item.symbol !== action.payload); // Payload is symbol
    },
    setWatchlist: (state, action) => {
      state.items = action.payload;
    },
  },
  extraReducers: (builder) => {
    // You would add async thunks here for fetching/updating watchlist from backend
    // For example:
    // builder
    //   .addCase(fetchWatchlist.pending, (state) => { state.status = 'loading'; })
    //   .addCase(fetchWatchlist.fulfilled, (state, action) => { state.status = 'succeeded'; state.items = action.payload; })
    //   .addCase(fetchWatchlist.rejected, (state, action) => { state.status = 'failed'; state.error = action.error.message; });
  },
});

export const { addStock, removeStock, setWatchlist } = watchlistSlice.actions;

// Example async thunk (uncomment and implement when you have watchlistService)
// export const fetchWatchlist = createAsyncThunk(
//   'watchlist/fetchWatchlist',
//   async (_, { getState }) => {
//     const userId = getState().auth.user.id; // Assuming user ID is in auth state
//     const response = await fetchWatchlistApi(userId);
//     return response.data;
//   }
// );

export const selectWatchlistItems = (state) => state.watchlist.items;

export default watchlistSlice.reducer;