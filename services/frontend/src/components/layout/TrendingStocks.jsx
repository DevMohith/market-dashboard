import React, { useEffect, useState } from 'react';
import './TrendingStocks.css';

function TrendingStocks({ open, onClose }) {
  const [trendingData, setTrendingData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (open) {
      fetch('http://localhost:8010/trending')
        .then(res => res.json())
        .then(data => {
          setTrendingData(data.trending_stocks || []);
          setLoading(false);
        })
        .catch(err => {
          console.error("Error fetching trending stocks:", err);
          setLoading(false);
        });
    }
  }, [open]);

  if (!open) return null;

  return (
    <div className="trending-overlay">
      <div className="trending-modal">
        <div className="trending-header">
          <h2>🔥 Trending Stocks</h2>
          <button className="close-btn" onClick={onClose}>✖</button>
        </div>
        <div className="trending-body">
          {loading ? (
            <p>Loading...</p>
          ) : trendingData.length === 0 ? (
            <p>No trending stocks available.</p>
          ) : (
            <ul className="trending-list">
              {trendingData.map((stock, idx) => (
                <li key={idx} className="trending-item">
                  <span className="stock-name">{stock.name}</span>
                  <span className="stock-symbol">({stock.symbol})</span>
                  <span className="investment">📈 {stock.investment_percent}%</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

export default TrendingStocks;
