// File: services/frontend/src/components/layout/TrendingStocks.jsx
import React, { useEffect, useState } from 'react';
import './TrendingStocks.css';

const TrendingStocks = ({ onClose }) => {
  const [stocks, setStocks] = useState([]);

  useEffect(() => {
    const fetchTrending = async () => {
      try {
        const response = await fetch('http://localhost:8010/trending');
        const data = await response.json();
        setStocks(data.trending_stocks);
      } catch (err) {
        console.error('Failed to fetch trending stocks:', err);
      }
    };

    fetchTrending();
  }, []);

  return (
    <div className="trending-modal">
      <div className="modal-header">
        <h2>🔥 Trending Stocks</h2>
        <button onClick={onClose}>X</button>
      </div>
      <div className="modal-body">
        {stocks.map((stock, idx) => (
          <div key={idx} className="stock-card">
            <div className="stock-title">
              <strong>{stock.symbol}</strong> — {stock.name}
            </div>
            <div className="progress-container">
              <div className="progress-bar" style={{ width: `${stock.investment_percent}%` }} />
              <span>{stock.investment_percent}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TrendingStocks;
