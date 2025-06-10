import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'; // Removed Navigate as it's not needed without PrivateRoute
import { useDispatch } from 'react-redux';

// Import Layout Components
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';

// Import Page Components
import DashboardPage from './pages/DashboardPage';
import WatchlistPage from './pages/WatchlistPage';
import StockDetailPage from './pages/StockDetailPage';
import RelationshipsGraphPage from './pages/RelationshipsGraphPage';
import ChatWidget from './components/layout/ChatWidget';

//import SettingsPage from './pages/SettingsPage';

// Import Redux actions/thunks
import { initMarketDataWebSocket } from './features/marketData/marketDataSlice';

function App() {
  const dispatch = useDispatch();

  // Initialize WebSocket connection immediately as there's no authentication gate
  useEffect(() => {
    //dispatch(initAlertsWebSocket());
    // This connects to the new Real-time Data Gateway for market data
    dispatch(initMarketDataWebSocket()); // <--- NEW DISPATCH
  }, [dispatch]); // Only dispatch once on mount

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

          {/* Floating global chatbot widget */}
          <ChatWidget />
        </div>
      </div>
    </Router>
  );
}

export default App;