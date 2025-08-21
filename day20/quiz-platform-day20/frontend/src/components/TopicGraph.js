import React, { useEffect, useState } from 'react';
import { Network } from 'vis-network/standalone';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';

const TopicGraph = ({ data }) => {
  const [network, setNetwork] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    if (!data || !data.nodes || !data.edges) return;

    const container = document.getElementById('topic-graph');
    
    const options = {
      nodes: {
        shape: 'dot',
        size: 16,
        font: { size: 12 },
        borderWidth: 2,
        shadow: true,
        color: {
          border: '#2B7CE9',
          background: '#97C2FC',
          highlight: { border: '#2B7CE9', background: '#D2E5FF' }
        }
      },
      edges: {
        width: 1,
        color: { inherit: 'from' },
        smooth: { type: 'continuous' },
        arrows: { to: { enabled: true, scaleFactor: 1 } },
        font: { size: 10 }
      },
      physics: {
        stabilization: false,
        barnesHut: {
          gravitationalConstant: -8000,
          springConstant: 0.001,
          springLength: 200
        }
      },
      interaction: {
        hover: true,
        hoverConnectedEdges: true
      }
    };

    const networkInstance = new Network(container, {
      nodes: data.nodes,
      edges: data.edges
    }, options);

    networkInstance.on('selectNode', (event) => {
      const nodeId = event.nodes[0];
      const node = data.nodes.find(n => n.id === nodeId);
      setSelectedNode(node);
    });

    setNetwork(networkInstance);

    return () => {
      if (networkInstance) {
        networkInstance.destroy();
      }
    };
  }, [data]);

  return (
    <Box sx={{ display: 'flex', gap: 2, height: '600px' }}>
      <Box sx={{ flex: 1 }}>
        <div 
          id="topic-graph" 
          style={{ 
            width: '100%', 
            height: '100%', 
            border: '1px solid #ddd',
            borderRadius: '8px'
          }} 
        />
      </Box>
      
      {selectedNode && (
        <Card sx={{ width: 300, height: 'fit-content' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              {selectedNode.label}
            </Typography>
            
            <Box sx={{ mb: 2 }}>
              <Chip 
                label={selectedNode.category} 
                size="small" 
                color="primary" 
                variant="outlined"
              />
            </Box>
            
            <Typography variant="body2" color="text.secondary">
              Difficulty Level: {selectedNode.difficulty}
            </Typography>
            
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Group: {selectedNode.group}
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default TopicGraph;
