const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const config = require('./config/config');
const logger = require('./utils/logger');
const verificationRoutes = require('./routes/verification');
const errorHandler = require('./middleware/errorHandler');

const app = express();

// Security middleware
app.use(helmet());
app.use(cors());

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api/verification', verificationRoutes);

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    service: 'Content Verification Service',
    version: '1.0.0',
    status: 'healthy'
  });
});

// Error handling
app.use(errorHandler);

const server = app.listen(config.port, () => {
  logger.info(`Content Verification Service listening on port ${config.port}`);
  logger.info(`Environment: ${config.nodeEnv}`);
});

module.exports = { app, server }; 