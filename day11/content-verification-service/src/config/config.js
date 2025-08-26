require('dotenv').config();

module.exports = {
  port: process.env.PORT || 3003,
  nodeEnv: process.env.NODE_ENV || 'development',
  anthropic: {
    apiKey: process.env.ANTHROPIC_API_KEY
  },
  redis: {
    url: process.env.REDIS_URL || 'redis://localhost:6379'
  },
  verification: {
    timeout: parseInt(process.env.VERIFICATION_TIMEOUT) || 30000,
    maxRetryAttempts: parseInt(process.env.MAX_RETRY_ATTEMPTS) || 3,
    qualityThreshold: parseInt(process.env.QUALITY_THRESHOLD) || 7
  },
  logging: {
    level: process.env.LOG_LEVEL || 'info'
  }
};
