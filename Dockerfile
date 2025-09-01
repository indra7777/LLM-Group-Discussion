# Multi-stage Docker build
FROM node:18-slim as frontend-builder

WORKDIR /app

# Copy frontend package files
COPY web/package*.json ./
RUN npm ci --only=production

# Copy frontend source
COPY web/src ./src
COPY web/public ./public
COPY web/*.css web/*.js web/*.json web/*.html ./

# Build frontend
RUN npm run build

# Python backend stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY web_api.py .
COPY src ./src
COPY config ./config

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/build ./web/build

# Expose port
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests, os; requests.get(f'http://localhost:{os.environ.get(\"PORT\", 8000)}/api/health')" || exit 1

# Start the application
CMD ["python", "web_api.py"]