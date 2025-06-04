import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import { Provider } from 'react-redux'; // For Redux
import store from './store'; // Your Redux store

// --- UI Library Global Styles ---
// For Material UI:
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';
// For Ant Design (if chosen): import 'antd/dist/antd.css';
// --- End UI Library Global Styles ---

// Import your own global application styles
import './assets/styles/index.css'; // Create this file in src/assets/styles

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Provider store={store}> {/* Wrap your App with Redux Provider */}
      <App />
    </Provider>
  </React.StrictMode>,
);