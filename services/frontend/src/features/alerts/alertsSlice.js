import { createSlice, createAsyncThunk, createSelector } from '@reduxjs/toolkit';
import { connectRealtimeWebSocket } from '../../services/realtimeDataService';
import { getPseudoUserId } from '../../utils/userId';
import { selectWatchlistItems } from '../watchlist/watchlistSlice'; // Keep this import, it's used in the thunk

const alertsSlice = createSlice({
  name: 'alerts',
  initialState: {
    currentAlerts: [],
    websocketConnected: false,
    status: 'idle',
    error: null,
  },
  reducers: {
    // This reducer now simply adds the alert without any filtering logic.
    // Filtering is done BEFORE this action is dispatched.
    addAlert: (state, action) => {
      // Ensure unique IDs for alerts, or handle duplicates
      if (!state.currentAlerts.some(alert => alert.id === action.payload.id)) {
        console.log(`AddAlert Reducer: Adding alert for ${action.payload.symbol}.`);
        state.currentAlerts.unshift(action.payload);
      }
    },
    markAlertAsRead: (state, action) => {
      const alertId = action.payload;
      const existingAlert = state.currentAlerts.find(alert => alert.id === alertId);
      if (existingAlert) {
        existingAlert.isRead = true;
      }
    },
    setWebsocketConnectionStatus: (state, action) => {
      state.websocketConnected = action.payload;
    },
    clearAlerts: (state) => {
      state.currentAlerts = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(initAlertsWebSocket.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(initAlertsWebSocket.fulfilled, (state) => {
        state.status = 'succeeded';
      })
      .addCase(initAlertsWebSocket.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message;
      });
  },
});

export const { addAlert, markAlertAsRead, setWebsocketConnectionStatus, clearAlerts } = alertsSlice.actions;

export const initAlertsWebSocket = createAsyncThunk(
  'alerts/initAlertsWebSocket',
  async (_, { dispatch, getState }) => { // getState is crucial here
    const userId = getPseudoUserId();
    const wsUrl = `${import.meta.env.VITE_APP_ALERTS_WS_URL}/ws/alerts/${userId}`;
    console.log(`Attempting to connect to Alerts WebSocket at: ${wsUrl}`);

    connectRealtimeWebSocket(wsUrl, {
      onOpen: () => {
        dispatch(setWebsocketConnectionStatus(true));
        console.log('✅ Alerts WebSocket connected.');
      },
      onMessage: (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('FRONTEND: Received raw alert data:', data); // Log the raw alert

          // --- NEW: Perform filtering *before* dispatching the addAlert action ---
          const state = getState(); // Get the current Redux state
          const currentWatchlist = selectWatchlistItems(state); // Use the selector to get the watchlist array
          const incomingSymbol = data.symbol.toUpperCase();

          if (currentWatchlist.includes(incomingSymbol)) {
            console.log(`FRONTEND: Filtering: Adding alert for ${incomingSymbol} (on watchlist).`);
            dispatch(addAlert(data)); // Dispatch action only if it passes the filter
          } else {
            console.log(`FRONTEND: Filtering: Ignoring alert for ${incomingSymbol} (not in current watchlist: ${JSON.stringify(currentWatchlist)}).`);
          }
          // --- END NEW ---

        } catch (e) {
          console.error("Error parsing alerts WebSocket message:", e, event.data);
        }
      },
      onClose: () => {
        dispatch(setWebsocketConnectionStatus(false));
        console.log('🛑 Alerts WebSocket disconnected.');
      },
      onError: (error) => {
        console.error('❌ Alerts WebSocket error:', error);
      },
    });
  }
);

export const selectAllAlerts = (state) => state.alerts.currentAlerts;
export const selectUnreadAlerts = createSelector(
  [(state) => state.alerts.currentAlerts],
  (currentAlerts) => currentAlerts.filter(alert => !alert.isRead)
);
export const selectWebsocketConnectionStatus = (state) => state.alerts.websocketConnected;

export default alertsSlice.reducer;
