import React, { useState, useRef, useCallback } from 'react';
import { Container, Typography, Box, TextField, Button, CircularProgress, Alert } from '@mui/material';
import ForceGraph2D from 'react-force-graph-2d';

function RelationshipsGraphPage() {
  const [symbol, setSymbol] = useState('');
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const graphRef = useRef();

  // Use useCallback for fetchRelationships to prevent unnecessary re-creation
  const fetchRelationships = useCallback(async () => {
    if (!symbol.trim()) {
      setError("Please enter a stock symbol.");
      return;
    }

    setLoading(true);
    setError(null);
    setGraphData({ nodes: [], links: [] }); // Clear previous graph immediately on new search

    try {
      const apiUrl = `${import.meta.env.VITE_APP_GRAPH_API_URL}/relationships/${symbol.toUpperCase()}`;
      console.log(`DEBUG (Frontend): Fetching data from: ${apiUrl}`);
      const response = await fetch(apiUrl);
      if (!response.ok) {
        throw new Error(`Error fetching relationships: ${response.statusText}`);
      }
      const data = await response.json();
      
      console.log("DEBUG (Frontend): Received raw data:", data);
      console.log("DEBUG (Frontend): Received nodes:", data.nodes);
      console.log("DEBUG (Frontend): Received links:", data.links);

      if (data.nodes.length === 0) {
        setError(`No relationships found for ${symbol.toUpperCase()}.`);
        setGraphData({ nodes: [], links: [] }); // Explicitly set empty graph if no data
      } else {
        // Assign initial random positions to nodes to help spread them out
        // Use a wider initial random spread for better visualization
        const nodesWithPositions = data.nodes.map(node => ({
          ...node,
          x: Math.random() * 800 - 400, // Random x between -400 and 400
          y: Math.random() * 800 - 400  // Random y between -400 and 400
        }));
        setGraphData({ nodes: nodesWithPositions, links: data.links });
      }
    } catch (err) {
      console.error("Failed to fetch graph data:", err);
      setError(`Failed to load relationships: ${err.message}. Ensure Neo4j and Stock Relation Service are running.`);
      setGraphData({ nodes: [], links: [] }); // Clear graph on error
    } finally {
      setLoading(false);
    }
  }, [symbol]); // Dependency array: re-create if symbol changes


  // Custom node rendering: draw circle and text label
  const nodeCanvasObject = (node, ctx, scale) => {
    const label = node.label || node.symbol;
    const fontSize = 14 / scale;
    ctx.font = `${fontSize}px Sans-Serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = 'black';
    ctx.fillText(label, node.x, node.y + (node.size / 2 || 10));

    // Draw the node circle
    ctx.beginPath();
    ctx.arc(node.x, node.y, node.size / scale || 8, 0, 2 * Math.PI, false);
    ctx.fillStyle = node.color || '#3f51b5';
    ctx.fill();
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 1 / scale;
    ctx.stroke();
  };

  // Custom link rendering
  const linkCanvasObject = (link, ctx, scale) => {
    const start = link.source;
    const end = link.target;

    // Only draw if both source and target nodes have valid x, y coordinates
    if (!start || typeof start.x !== 'number' || typeof start.y !== 'number' ||
        !end || typeof end.x !== 'number' || typeof end.y !== 'number' ||
        isNaN(start.x) || isNaN(start.y) || isNaN(end.x) || isNaN(end.y)
        ) {
      return; 
    }

    // --- Draw the Line ---
    ctx.beginPath();
    ctx.moveTo(start.x, start.y);
    ctx.lineTo(end.x, end.y);
    ctx.strokeStyle = '#cccccc'; 
    ctx.lineWidth = 1.5 / scale; 
    ctx.stroke(); 

    // --- Draw Arrow Head at the Target End ---
    const arrowLength = 5; 
    const arrowWidth = 3; 
    const angle = Math.atan2(end.y - start.y, end.x - start.x);

    ctx.save(); 
    ctx.beginPath();
    ctx.translate(end.x, end.y); 
    ctx.rotate(angle); 
    ctx.moveTo(-arrowLength, arrowWidth / 2);
    ctx.lineTo(0, 0); 
    ctx.lineTo(-arrowLength, -arrowWidth / 2);
    ctx.fillStyle = '#cccccc'; 
    ctx.fill();
    ctx.restore(); 

    // --- Draw Label on Link ---
    const label = link.type; 
    if (label) {
      const textPos = { x: (start.x + end.x) / 2, y: (start.y + end.y) / 2 };
      const textAngle = angle; 
      
      ctx.save();
      ctx.translate(textPos.x, textPos.y);
      ctx.rotate(textAngle);
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#333333'; 
      ctx.font = `${9 / scale}px Sans-Serif`; 
      ctx.fillText(label, 0, -5 / scale); 
      ctx.restore();
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Company Relationship Graph
      </Typography>

      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
        <TextField
          label="Enter Stock Symbol (e.g., AAPL)"
          variant="outlined"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') fetchRelationships();
          }}
          sx={{ mr: 2, flexGrow: 1 }}
        />
        <Button
          variant="contained"
          onClick={fetchRelationships} // Explicitly call on button click
          disabled={loading || !symbol.trim()}
        >
          {loading ? <CircularProgress size={24} /> : 'Explore Relationships'}
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Box 
        sx={{ 
          border: '1px solid #ddd', 
          borderRadius: 2, 
          overflow: 'hidden', 
          height: '600px', 
          width: '100%',
          position: 'relative',
          backgroundColor: '#f0f0f0' 
        }}
      >
        <ForceGraph2D
          ref={graphRef}
          graphData={graphData}
          nodeId="id"
          nodeLabel="label"
          linkSource="source"
          linkTarget="target"
          linkDirectionalParticles={1} 
          linkDirectionalParticleSpeed={0.005} 
          nodeCanvasObject={nodeCanvasObject}
          linkCanvasObject={linkCanvasObject}
          backgroundColor="#f0f0f0" 
          enableNodeDrag={true}
          onNodeClick={(node) => {
            console.log("Node clicked:", node);
            // Clicking a node will update the symbol, and the user can then click "Explore"
            setSymbol(node.symbol); 
          }}
          // FIX: Corrected zoomToFit signature: (duration = 0, padding = 20)
          onEngineStop={() => {
            if (graphRef.current) {
              // Zoom out a bit more with 1000ms duration and 300px padding
              graphRef.current.zoomToFit(1000, 300); 
            }
          }}
          d3Forces={simulation => { 
            simulation.force('charge').strength(-250); 
            simulation.force('link').distance(80); 
            simulation.force('center').x(0).y(0); 
            simulation.force('collide').radius(30).iterations(2); 
          }}
          width={window.innerWidth * 0.75} 
          height={600} 
        />
      </Box>
    </Container>
  );
}

export default RelationshipsGraphPage;
