let alertsSocket = null;

export const connectAlertsWebSocket = (url, callbacks) => {
  if (alertsSocket && alertsSocket.readyState === WebSocket.OPEN) {
    alertsSocket.close(); // Close existing connection if any
  }

  alertsSocket = new WebSocket(url);

  alertsSocket.onopen = (event) => {
    callbacks.onOpen(event);
  };
  alertsSocket.onmessage = (event) => {
    callbacks.onMessage(event);
  };
  alertsSocket.onclose = (event) => {
    callbacks.onClose(event);
    // You might want to implement reconnection logic here or in the Redux thunk
  };
  alertsSocket.onerror = (event) => {
    callbacks.onError(event);
  };
};

export const closeAlertsWebSocket = () => {
  if (alertsSocket) {
    alertsSocket.close();
    alertsSocket = null;
  }
};