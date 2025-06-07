import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Container, Typography, Box, CircularProgress, Paper, Grid } from '@mui/material';
// import PriceLineChart from '../components/charts/PriceLineChart'; // You'll create this
// import { fetchStockDetails, fetchStockHistory } from '../services/marketDataService'; // You'll create these

function StockDetailPage() {
  const { symbol } = useParams(); // Get stock symbol from URL (e.g., /stock/AAPL)
  const [stockDetails, setStockDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadStockData = async () => {
      setLoading(true);
      setError(null);
      try {
        // TODO: Replace with actual API calls to your backend
        // const details = await fetchStockDetails(symbol);
        // const history = await fetchStockHistory(symbol);
        // setStockDetails({ ...details, history });

        // Simulate fetching data
        setTimeout(() => {
          setStockDetails({
            symbol: symbol.toUpperCase(),
            name: `${symbol.toUpperCase()} Company`,
            price: (Math.random() * 200 + 50).toFixed(2),
            change: (Math.random() * 10 - 5).toFixed(2),
            changePercent: (Math.random() * 5 - 2.5).toFixed(2),
            volume: (Math.random() * 10000000).toFixed(0),
            description: `This is a simulated description for ${symbol.toUpperCase()} Company. It's a leading player in its industry, known for innovation and market leadership.`,
            // Dummy history data for chart
            history: Array.from({ length: 30 }, (_, i) => ({
              date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
              price: (Math.random() * 100 + 100).toFixed(2),
            })),
          });
          setLoading(false);
        }, 1000);

      } catch (err) {
        console.error("Failed to fetch stock details:", err);
        setError("Failed to load stock data. Please try again.");
        setLoading(false);
      }
    };

    if (symbol) {
      loadStockData();
    }
  }, [symbol]); // Re-run effect if symbol changes

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ textAlign: 'center', mt: 8 }}>
        <CircularProgress />
        <Typography variant="h6" sx={{ mt: 2 }}>Loading stock data for {symbol.toUpperCase()}...</Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md" sx={{ textAlign: 'center', mt: 8 }}>
        <Typography variant="h6" color="error">{error}</Typography>
      </Container>
    );
  }

  if (!stockDetails) {
    return (
      <Container maxWidth="md" sx={{ textAlign: 'center', mt: 8 }}>
        <Typography variant="h6">No stock data found for {symbol.toUpperCase()}.</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 4 }}>
        {stockDetails.name} ({stockDetails.symbol})
      </Typography>

      <Grid container spacing={3}>
        {/* Stock Overview */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>Overview</Typography>
            <Typography variant="h6" color="primary">Current Price: ${stockDetails.price}</Typography>
            <Typography variant="body1" color={stockDetails.change > 0 ? 'success.main' : 'error.main'}>
              Change: ${stockDetails.change} ({stockDetails.changePercent}%)
            </Typography>
            <Typography variant="body2">Volume: {parseInt(stockDetails.volume).toLocaleString()}</Typography>
            <Typography variant="body2" sx={{ mt: 2 }}>{stockDetails.description}</Typography>
          </Paper>
        </Grid>

        {/* Price Chart */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>Price History</Typography>
            {/* Uncomment and use your chart component here */}
            {/* <PriceLineChart data={stockDetails.history} /> */}
            <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: '#f0f0f0' }}>
              <Typography variant="h6" color="textSecondary">
                Price Chart Placeholder
              </Typography>
            </Box>
          </Paper>
        </Grid>

        {/* Additional Sections (e.g., News, Financials, Events) */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>Recent News & Events</Typography>
            <Typography variant="body2" color="textSecondary">
              (This section would display sentiment analysis on news headlines and stock events like earnings, dividends, IPOs.)
            </Typography>
            {/* You'll integrate news and event data here */}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default StockDetailPage;
