#!/bin/bash

echo "=========================================="
echo "  Multimodal RAG Chatbot - Startup"
echo "=========================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << EOF
# Google AI API Key (Required)
GOOGLE_API_KEY=your_google_api_key_here

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=multimodal_rag
EMBEDDING_DIM=768

# Model Configuration
LLM_MODEL=gemini-1.5-flash
VISION_MODEL=gemini-1.5-flash

# Text Splitting
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Retrieval
DEFAULT_K=5

# Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=52428800
EOF
    echo "✅ Created .env template. Please edit it and add your GOOGLE_API_KEY"
    echo ""
fi

# Check if GOOGLE_API_KEY is set
if grep -q "your_google_api_key_here" .env 2>/dev/null || ! grep -q "GOOGLE_API_KEY=" .env 2>/dev/null; then
    echo "⚠️  WARNING: GOOGLE_API_KEY not configured in .env"
    echo "   Please edit .env and add your Google AI API key"
    echo ""
fi

# Step 1: Start Docker containers
echo "📦 Starting Docker containers (Qdrant)..."
docker compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Failed to start Docker containers"
    exit 1
fi

echo "✅ Docker containers started"
echo ""

# Step 2: Wait for Qdrant to be ready
echo "⏳ Waiting for Qdrant to be ready..."
sleep 5

# Step 3: Install Python dependencies
echo "📚 Installing Python dependencies..."
cd backend
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

echo "✅ Dependencies installed"
echo ""

# Step 4: Start backend server
echo "🚀 Starting FastAPI backend server..."
echo "   Backend will be available at: http://localhost:8000"
echo "   API docs at: http://localhost:8000/docs"
echo ""

# Start backend in background (from backend directory)
cd backend
python -m uvicorn app.api:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

echo "✅ Backend server started (PID: $BACKEND_PID)"
echo ""

# Step 5: Instructions for frontend
echo "=========================================="
echo "  Next Steps:"
echo "=========================================="
echo ""
echo "1. Install frontend dependencies:"
echo "   cd frontend && npm install"
echo ""
echo "2. Start frontend development server:"
echo "   npm run dev"
echo ""
echo "3. Open browser to: http://localhost:3000"
echo ""
echo "=========================================="
echo "  Services:"
echo "=========================================="
echo "  Backend API:  http://localhost:8000"
echo "  API Docs:     http://localhost:8000/docs"
echo "  Qdrant:       http://localhost:6333"
echo "  Frontend:     http://localhost:3000 (after npm run dev)"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
wait $BACKEND_PID
