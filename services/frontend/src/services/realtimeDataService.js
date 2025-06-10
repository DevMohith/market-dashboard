// src/services/realtimeDataService.js
let realtimeSocket = null;

export const connectRealtimeWebSocket = (url, callbacks) => {
  if (realtimeSocket && realtimeSocket.readyState === WebSocket.OPEN) {
    realtimeSocket.close(); // Close existing connection if any
  }

  realtimeSocket = new WebSocket(url);

  realtimeSocket.onopen = (event) => {
    callbacks.onOpen(event);
  };
  realtimeSocket.onmessage = (event) => {
    callbacks.onMessage(event);
  };
  realtimeSocket.onclose = (event) => {
    callbacks.onClose(event);
  };
  realtimeSocket.onerror = (event) => {
    callbacks.onError(event);
  };
};

export const closeRealtimeWebSocket = () => {
  if (realtimeSocket) {
    realtimeSocket.close();
    realtimeSocket = null;
  }
};
