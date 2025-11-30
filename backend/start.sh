#!/bin/bash
# Startup script for Railway
set -e

# Get port from environment or default to 8000
PORT=${PORT:-8000}

# Log startup info
echo "Starting ChatPDF API on port $PORT"
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo "Contents: $(ls -la)"

# Start uvicorn
exec python -m uvicorn app.api:app --host 0.0.0.0 --port $PORT

