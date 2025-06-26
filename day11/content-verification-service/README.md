# Content Verification Service

AI-powered content verification service for quiz platform implementation.

## Features

- ✅ Format validation with Joi schemas
- 🤖 Claude AI-powered factual accuracy checking
- 📊 Quality scoring and confidence metrics
- 🔄 Async processing with Bull queues
- 🔁 Retry logic with exponential backoff
- 📈 Batch verification support
- 🏥 Health monitoring and logging

## Quick Start

```bash
# Install dependencies
npm install

# Set up environment
cp .env.example .env
# Edit .env with your Anthropic API key

# Start Redis (required for queues)
docker run -d -p 6379:6379 redis:7-alpine

# Start service
npm start

# Run tests
npm test

# View demo
open demo.html
```

## API Endpoints

- `GET /api/verification/health` - Health check
- `POST /api/verification/verify` - Synchronous verification
- `POST /api/verification/verify/async` - Asynchronous verification
- `POST /api/verification/verify/batch` - Batch verification
- `GET /api/verification/job/:jobId` - Job status

## Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t content-verification-service .
docker run -p 3003:3003 content-verification-service
```

## Architecture

The service follows a multi-stage verification pipeline:
1. Format validation (structure, required fields)
2. Claude AI factual accuracy check
3. Quality scoring and decision making
4. Result routing (approved/rejected/review)

## Testing

```bash
# Unit tests
npm test

# Coverage report
npm run test:coverage

# Interactive demo
node demo.js
``` 