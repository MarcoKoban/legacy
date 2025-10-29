# Multi-stage Docker build for Geneweb API
# Security-focused with minimal attack surface

# Build stage
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for building
RUN useradd --create-home --shell /bin/bash builder

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for running the application
RUN useradd --create-home --shell /bin/bash --uid 1000 geneweb

# Create directories with proper permissions
RUN mkdir -p /app /var/log/geneweb /etc/geneweb/ssl \
    && chown -R geneweb:geneweb /app /var/log/geneweb /etc/geneweb

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy application code
COPY --chown=geneweb:geneweb src/ ./src/
COPY --chown=geneweb:geneweb start_api.py docker-entrypoint.sh ./
COPY --chown=geneweb:geneweb pyproject.toml requirements.txt ./

# Make scripts executable
RUN chmod +x start_api.py docker-entrypoint.sh

# Switch to non-root user
USER geneweb

# Security: Remove shell access for the user
RUN sudo usermod -s /bin/false geneweb || true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port (non-privileged)
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Use entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"]