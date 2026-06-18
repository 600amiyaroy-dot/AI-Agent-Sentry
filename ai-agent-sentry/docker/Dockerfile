# ============================================
# ENTERPRISE DOCKERFILE FOR AI AGENT SENTRY
# Version: 2.0.0 (With pyyaml)
# ============================================

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies - INCLUDING PYYAML
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt pyyaml

# Install additional enterprise packages
RUN pip install --no-cache-dir \
    uvicorn \
    fastapi \
    psycopg2-binary \
    redis \
    prometheus-client \
    python-multipart \
    python-jose \
    passlib

# Copy the entire application
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/models /app/uploads

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:///data/agents.db
ENV PYTHONPATH=/app

# Expose ports
EXPOSE 8000
EXPOSE 9090

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run both main.py and web_dashboard
CMD bash -c "python main.py & uvicorn web_dashboard:app --host 0.0.0.0 --port 8000 --workers 2"