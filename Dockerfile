FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Run the application
# Railway provides PORT environment variable
# Use python -m to ensure proper module resolution
ENV PORT=8000
EXPOSE 8000
CMD python -m uvicorn app.api:app --host 0.0.0.0 --port ${PORT:-8000}

