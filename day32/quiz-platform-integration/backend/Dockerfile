FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements/base.txt requirements/base.txt
RUN pip install -r requirements/base.txt

# Copy source code
COPY src/ .

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "main.py"]
