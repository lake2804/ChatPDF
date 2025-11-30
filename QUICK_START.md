# Quick Start Guide

## Running the Backend

### Option 1: Using Start Scripts (Recommended)
```bash
# Windows
start.bat

# Linux/macOS
chmod +x start.sh
./start.sh
```

### Option 2: Manual Start

**Important**: Always run uvicorn from the `backend` directory!

```bash
# 1. Start Qdrant (Docker)
docker compose up -d

# 2. Install dependencies (if not already done)
cd backend
pip install -r requirements.txt

# 3. Start backend server (from backend directory)
python -m uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: From Root Directory (Alternative)

If you need to run from root, set PYTHONPATH:

```bash
# Windows
set PYTHONPATH=%CD%\backend
python -m uvicorn backend.app.api:app --reload --host 0.0.0.0 --port 8000

# Linux/macOS
export PYTHONPATH=$PWD/backend
python -m uvicorn backend.app.api:app --reload --host 0.0.0.0 --port 8000
```

## Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:3000 in your browser.

## Troubleshooting

### ModuleNotFoundError: No module named 'app'

**Solution**: Make sure you're running uvicorn from the `backend` directory, or set PYTHONPATH as shown above.

### Qdrant Connection Error

**Solution**: Make sure Docker is running and Qdrant container is started:
```bash
docker compose up -d
docker ps  # Should show qdrant container running
```

### Google API Key Error

**Solution**: Make sure you have a `.env` file in the root directory with your `GOOGLE_API_KEY`:
```env
GOOGLE_API_KEY=your_actual_api_key_here
```


