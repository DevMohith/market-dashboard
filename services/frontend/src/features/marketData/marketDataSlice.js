import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { connectRealtimeWebSocket, closeRealtimeWebSocket } from '../../services/realtimeDataService';

const marketDataSlice = createSlice({
  name: 'marketData',
  initialState: {
    latestPrices: {}, // Stores the last known price for each symbol: { 'AAPL': { price: 170.50, timestamp: '...' }, 'MSFT': {...} }
    recentTrades: [], // Stores a limited history of the most recent trades globally
    websocketConnected: false,
    status: 'idle', // 'idle' | 'connecting' | 'connected' | 'failed'
    error: null,
  },
  reducers: {
    // Action to update the price of a specific stock
    updateStockPrice: (state, action) => {
      const { symbol, price, timestamp } = action.payload;
      state.latestPrices[symbol] = { price, timestamp };
    },
    // Action to add a new trade to recentTrades list
    addRecentTrade: (state, action) => {
      // Keep the list to a manageable size, e.g., last 20 trades
      state.recentTrades.unshift(action.payload); // Add to the beginning
      if (state.recentTrades.length > 20) { // Limit to 20 trades
        state.recentTrades.pop(); // Remove the oldest trade
      }
    },
    setMarketDataWebsocketStatus: (state, action) => {
      state.websocketConnected = action.payload;
      state.status = action.payload ? 'connected' : 'disconnected';
    },
    setMarketDataError: (state, action) => {
      state.error = action.payload;
      state.status = 'failed';
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(initMarketDataWebSocket.pending, (state) => {
        state.status = 'connecting';
      })
      .addCase(initMarketDataWebSocket.fulfilled, (state) => {
        state.status = 'connected'; // Status handled by setMarketDataWebsocketStatus as well
      })
      .addCase(initMarketDataWebSocket.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message;
      });
  },
});

export const { updateStockPrice, addRecentTrade, setMarketDataWebsocketStatus, setMarketDataError } = marketDataSlice.actions;

// Async Thunk for WebSocket Initialization
export const initMarketDataWebSocket = createAsyncThunk(
  'marketData/initMarketDataWebSocket',
  async (_, { dispatch }) => {
    const wsUrl = import.meta.env.VITE_APP_REALTIME_GATEWAY_WS_URL; // Use the new URL
    console.log(`Attempting to connect to Market Data WebSocket at: ${wsUrl}`);

    connectRealtimeWebSocket(wsUrl, {
      onOpen: () => {
        dispatch(setMarketDataWebsocketStatus(true));
        console.log('✅ Market Data WebSocket connected.');
      },
      onMessage: (event) => {
        try {
          const data = JSON.parse(event.data);
          // Assuming data structure: { event: "price", symbol: "AAPL", price: 170.50, timestamp: "..." }
          if (data.event === 'price') {
            dispatch(updateStockPrice(data));
            dispatch(addRecentTrade(data));
          }
          // You could handle other event types here if the gateway sends them
        } catch (e) {
          console.error("Error parsing market data WebSocket message:", e, event.data);
          dispatch(setMarketDataError('Failed to parse incoming market data.'));
        }
      },
      onClose: () => {
        dispatch(setMarketDataWebsocketStatus(false));
        console.log('🛑 Market Data WebSocket disconnected.');
        // Consider implementing reconnection logic here or in App.jsx
      },
      onError: (error) => {
        console.error('❌ Market Data WebSocket error:', error);
        dispatch(setMarketDataError('Market Data WebSocket connection error.'));
      },
    });
  }
);

// Selectors
export const selectLatestPrices = (state) => state.marketData.latestPrices;
export const selectRecentTrades = (state) => state.marketData.recentTrades;
export const selectMarketDataWebsocketStatus = (state) => state.marketData.websocketConnected;

export default marketDataSlice.reducer;
