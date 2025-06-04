import React, { useState } from 'react';
import { Container, Typography, Box, TextField, Button, Paper } from '@mui/material';
// import StockGraphViz from '../components/graph/StockGraphViz'; // You'll create this component later

function RelationshipsGraphPage() {
  const [companySymbol, setCompanySymbol] = useState('');
  const [graphData, setGraphData] = useState(null); // This would hold data fetched from backend

  const handleSearch = () => {
    if (companySymbol.trim()) {
      console.log(`Fetching relationships for: ${companySymbol.toUpperCase()}`);
      // TODO: Call your backend service (e.g., graphService.js) here
      // Example: fetchCompanyRelationships(companySymbol.toUpperCase()).then(data => setGraphData(data));
      // For now, simulate some data or just log the action
      setGraphData({
        nodes: [
          { id: 'AAPL', label: 'Apple Inc.' },
          { id: 'MSFT', label: 'Microsoft Corp.' },
          { id: 'GOOGL', label: 'Alphabet Inc.' },
        ],
        links: [
          { source: 'AAPL', target: 'MSFT', type: 'COMPETES_WITH' },
          { source: 'AAPL', target: 'GOOGL', type: 'COMPETES_WITH' },
        ]
      });
    }
  };

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 4 }}>
        Company Relationships Graph
      </Typography>

      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>Explore Connections</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            label="Enter Company Symbol (e.g., AAPL)"
            variant="outlined"
            value={companySymbol}
            onChange={(e) => setCompanySymbol(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleSearch();
              }
            }}
            fullWidth
          />
          <Button
            variant="contained"
            color="primary"
            onClick={handleSearch}
            sx={{ px: 4 }}
          >
            Search
          </Button>
        </Box>
      </Paper>

      {/* Placeholder for the Graph Visualization Component */}
      <Paper elevation={3} sx={{ p: 3, height: '600px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        {graphData ? (
          // <StockGraphViz data={graphData} /> // Uncomment when you create StockGraphViz
          <Typography variant="h5" color="textSecondary">
            Graph visualization would appear here for {companySymbol.toUpperCase()}
            <pre>{JSON.stringify(graphData, null, 2)}</pre>
          </Typography>
        ) : (
          <Typography variant="h5" color="textSecondary">
            Search for a company to visualize its relationships.
          </Typography>
        )}
      </Paper>
    </Container>
  );
}

export default RelationshipsGraphPage;
