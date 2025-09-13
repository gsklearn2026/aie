FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY tests/ ./tests/
COPY .env .

# Create reports directory
RUN mkdir -p reports

# Expose ports
EXPOSE 8080 8089

# Default command runs the dashboard
CMD ["streamlit", "run", "src/performance_monitor/dashboard.py", "--server.port", "8080", "--server.address", "0.0.0.0"]
