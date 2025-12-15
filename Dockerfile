# =============================================================================
# Multi-stage Dockerfile for MBTQ Smart Financial Platform
# Production-ready containerization with security best practices
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies and build application
# -----------------------------------------------------------------------------
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Copy application code
COPY . .

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Create minimal production image
# -----------------------------------------------------------------------------
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    FLASK_APP=main.py \
    PORT=5000

# Create non-root user for security
RUN groupadd -r mbtq && useradd -r -g mbtq mbtq

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=mbtq:mbtq . .

# Create necessary directories with correct permissions
RUN mkdir -p logs static/uploads && \
    chown -R mbtq:mbtq /app

# Switch to non-root user
USER mbtq

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/internal/health || exit 1

# Run application with gunicorn (production WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "wsgi:app"]
