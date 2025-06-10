import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { getPseudoUserId } from './utils/userId'; // NEW: Import pseudo user ID utility

// Import Layout Components
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';

// Import Page Components
import DashboardPage from './pages/DashboardPage';
import WatchlistPage from './pages/WatchlistPage';
import StockDetailPage from './pages/StockDetailPage';
import RelationshipsGraphPage from './pages/RelationshipsGraphPage';
import ChatWidget from './components/layout/ChatWidget';

// Import Redux actions/thunks
import { initMarketDataWebSocket } from './features/marketData/marketDataSlice';
import { initAlertsWebSocket } from './features/alerts/alertsSlice';

function App() {
  const dispatch = useDispatch();

  useEffect(() => {
    // NEW: Initialize pseudo-user ID
    getPseudoUserId(); // Call this once to ensure a user ID exists

    // Initialize WebSocket connections
    dispatch(initAlertsWebSocket());
    dispatch(initMarketDataWebSocket());
  }, [dispatch]);

  return (
    <Router>
      <div style={{ display: 'flex', minHeight: '100vh' }}>
        <Sidebar />
        <div style={{ flexGrow: 1, display: 'flex', flexDirection: 'column', position: 'relative' }}>
          <Header />
          <main style={{ flexGrow: 1, padding: '20px', backgroundColor: '#f4f7fa' }}>
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/stock/:symbol" element={<StockDetailPage />} />
              <Route path="/relationships" element={<RelationshipsGraphPage />} />
              <Route path="/watchlist" element={<WatchlistPage />} />
              <Route path="*" element={<div><h1>404: Page Not Found</h1><p>The page you are looking for does not exist.</p></div>} />
            </Routes>
          </main>

          <ChatWidget />
        </div>
      </div>
    </Router>
  );
}

export default App;
