FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=testing
ENV GEMINI_API_KEY=test_key_for_testing

# Run tests by default
CMD ["pytest", "tests/unit/", "-v", "--cov=src", "--cov-report=term-missing"]
