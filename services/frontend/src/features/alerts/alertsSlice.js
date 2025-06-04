import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { connectAlertsWebSocket, closeAlertsWebSocket } from '../../services/marketDataService';

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
      state.currentAlerts.unshift(action.payload);
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

// Async Thunk for WebSocket Initialization - SIMPLIFIED
export const initAlertsWebSocket = createAsyncThunk(
  'alerts/initAlertsWebSocket',
  async (_, { dispatch }) => { // Removed getState as token is no longer needed from auth
    // Assuming the WebSocket doesn't require a token without user management
    const wsUrl = `${import.meta.env.VITE_APP_API_WS_URL}/ws/alerts`; // No token needed here
    console.log(`Attempting to connect to WebSocket at: ${wsUrl}`);

    connectAlertsWebSocket(wsUrl, {
      onOpen: () => {
        dispatch(setWebsocketConnectionStatus(true));
        console.log('Alerts WebSocket connected.');
      },
      onMessage: (event) => {
        const data = JSON.parse(event.data);
        const newAlert = {
          id: Date.now().toString(),
          stockSymbol: data.symbol,
          type: data.type,
          message: data.message,
          timestamp: new Date().toISOString(),
          isRead: false,
        };
        dispatch(addAlert(newAlert));
      },
      onClose: () => {
        dispatch(setWebsocketConnectionStatus(false));
        console.log('Alerts WebSocket disconnected.');
        // Consider implementing reconnection logic here if needed for robustness
      },
      onError: (error) => {
        console.error('Alerts WebSocket error:', error);
      },
    });
  }
);

export const selectAllAlerts = (state) => state.alerts.currentAlerts;
export const selectUnreadAlerts = (state) => state.alerts.currentAlerts.filter(alert => !alert.isRead);
export const selectWebsocketConnectionStatus = (state) => state.alerts.websocketConnected;

export default alertsSlice.reducer;