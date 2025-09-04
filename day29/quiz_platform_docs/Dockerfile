FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY backend/ ./backend/

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=backend/app.py
ENV FLASK_ENV=production

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "backend.app:app"]
