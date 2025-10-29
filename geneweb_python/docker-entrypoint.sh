#!/bin/bash
"""
Docker-compatible startup script for Geneweb API
"""

# Default values
HOST=${GENEWEB_API_HOST:-0.0.0.0}
PORT=${GENEWEB_API_PORT:-8000}
WORKERS=${GENEWEB_API_WORKERS:-4}

# Check if running in container
if [ -f /.dockerenv ]; then
    echo "Running in Docker container"
    CONTAINER_MODE=true
else
    CONTAINER_MODE=false
fi

# Create necessary directories
mkdir -p /var/log/geneweb
mkdir -p /etc/geneweb/ssl

# Set permissions
if [ "$CONTAINER_MODE" = true ]; then
    chown -R nobody:nogroup /var/log/geneweb
    chmod 755 /var/log/geneweb
fi

# Validate environment (skip SSL check if variables are empty - e.g., when using reverse proxy)
if [ "$GENEWEB_API_DEBUG" != "true" ] && [ -n "$GENEWEB_API_SSL_CERTFILE" ] && [ -n "$GENEWEB_API_SSL_KEYFILE" ]; then
    if [ ! -f "$GENEWEB_API_SSL_CERTFILE" ] || [ ! -f "$GENEWEB_API_SSL_KEYFILE" ]; then
        echo "ERROR: SSL certificate files required for production mode"
        echo "Set GENEWEB_API_SSL_CERTFILE and GENEWEB_API_SSL_KEYFILE"
        exit 1
    fi
fi

# Start API
echo "Starting Geneweb API..."
echo "Host: $HOST"
echo "Port: $PORT"
echo "Workers: $WORKERS"
echo "Debug: ${GENEWEB_API_DEBUG:-false}"

cd /app
exec python3 start_api.py \
    --host "$HOST" \
    --port "$PORT" \
    --workers "$WORKERS"