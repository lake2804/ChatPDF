@echo off
echo ==========================================
echo   Multimodal RAG Chatbot - Startup
echo ==========================================
echo.

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Creating template...
    (
        echo # Google AI API Key (Required^)
        echo GOOGLE_API_KEY=your_google_api_key_here
        echo.
        echo # Qdrant Configuration
        echo QDRANT_URL=http://localhost:6333
        echo QDRANT_COLLECTION=multimodal_rag
        echo EMBEDDING_DIM=768
        echo.
        echo # Model Configuration
        echo LLM_MODEL=gemini-1.5-flash
        echo VISION_MODEL=gemini-1.5-flash
        echo.
        echo # Text Splitting
        echo CHUNK_SIZE=1000
        echo CHUNK_OVERLAP=200
        echo.
        echo # Retrieval
        echo DEFAULT_K=5
        echo.
        echo # Upload
        echo UPLOAD_DIR=uploads
        echo MAX_FILE_SIZE=52428800
    ) > .env
    echo ✅ Created .env template. Please edit it and add your GOOGLE_API_KEY
    echo.
)

REM Step 1: Start Docker containers
echo 📦 Starting Docker containers (Qdrant^)...
docker compose up -d

if errorlevel 1 (
    echo ❌ Failed to start Docker containers
    exit /b 1
)

echo ✅ Docker containers started
echo.

REM Step 2: Wait for Qdrant to be ready
echo ⏳ Waiting for Qdrant to be ready...
timeout /t 5 /nobreak >nul

REM Step 3: Install Python dependencies
echo 📚 Installing Python dependencies...
cd backend
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install Python dependencies
    exit /b 1
)

echo ✅ Dependencies installed
echo.

REM Step 4: Start backend server
echo 🚀 Starting FastAPI backend server...
echo    Backend will be available at: http://localhost:8000
echo    API docs at: http://localhost:8000/docs
echo.

REM Start backend (from backend directory)
start "RAG Backend" cmd /k "cd backend && python -m uvicorn app.api:app --reload --host 0.0.0.0 --port 8000"

echo ✅ Backend server started in new window
echo.

echo ==========================================
echo   Next Steps:
echo ==========================================
echo.
echo 1. Install frontend dependencies:
echo    cd frontend ^&^& npm install
echo.
echo 2. Start frontend development server:
echo    cd frontend ^&^& npm run dev
echo.
echo 3. Open browser to: http://localhost:3000
echo.
echo ==========================================
echo   Services:
echo ==========================================
echo   Backend API:  http://localhost:8000
echo   API Docs:     http://localhost:8000/docs
echo   Qdrant:       http://localhost:6333
echo   Frontend:     http://localhost:3000 (after npm run dev^)
echo.
echo Press any key to exit...
pause >nul

