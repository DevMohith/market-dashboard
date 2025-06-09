import { configureStore } from '@reduxjs/toolkit';
// import authReducer from '../features/auth/authSlice'; // REMOVED
import alertsReducer from '../features/alerts/alertsSlice';
import watchlistReducer from '../features/watchlist/watchlistSlice';
// Import other feature slices here as you create them
import marketDataReducer from '../features/marketData/marketDataSlice';
// import marketDataReducer from '../features/marketData/marketDataSlice';
// import relationshipsReducer from '../features/relationships/relationshipsSlice';

export default configureStore({
  reducer: {
    // auth: authReducer, // REMOVED
    alerts: alertsReducer,
    watchlist: watchlistReducer,
    marketData: marketDataReducer,
    // Add other reducers here:
    // marketData: marketDataReducer,
    // relationships: relationshipsReducer,
  },
});