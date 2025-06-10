import { createSlice, createAsyncThunk, createSelector } from '@reduxjs/toolkit';
// Ensure this import points to your real-time data service, not the new alerts one
import { connectRealtimeWebSocket } from '../../services/realtimeDataService'; // This service will handle general WS connections

const alertsSlice = createSlice({
  name: 'alerts',
  initialState: {
    currentAlerts: [],
    websocketConnected: false,
    status: 'idle',
    error: null,
  },
  reducers: {
    addAlert: (state, action) => {
      // Ensure unique IDs for alerts, or handle duplicates
      if (!state.currentAlerts.some(alert => alert.id === action.payload.id)) {
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
  async (_, { dispatch }) => {
    // --- USE THE NEW ALERTS WS URL ---
    const wsUrl = import.meta.env.VITE_APP_ALERTS_WS_URL;
    console.log(`Attempting to connect to Alerts WebSocket at: ${wsUrl}`);

    // Re-use connectRealtimeWebSocket function for alerts WS
    connectRealtimeWebSocket(wsUrl, {
      onOpen: () => {
        dispatch(setWebsocketConnectionStatus(true));
        console.log('✅ Alerts WebSocket connected.');
      },
      onMessage: (event) => {
        try {
          const data = JSON.parse(event.data);
          // Assuming alert data structure: { id, symbol, type, message, timestamp }
          dispatch(addAlert(data));
        } catch (e) {
          console.error("Error parsing alerts WebSocket message:", e, event.data);
        }
      },
      onClose: () => {
        dispatch(setWebsocketConnectionStatus(false));
        console.log('🛑 Alerts WebSocket disconnected.');
        // Implement reconnection logic here if desired
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
