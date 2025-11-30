# ChatPDF - AI-Powered Document Chat Platform

A production-ready full-stack Multimodal Retrieval-Augmented Generation (RAG) chatbot that enables natural language conversations with documents. Built with modern technologies including FastAPI, React, and Google Gemini AI.

## 🚀 Features

### Core Capabilities
- **Multi-Format Document Support**: PDF, DOCX, PPTX, TXT, Markdown, and Images
- **Intelligent Document Processing**: 
  - Automatic text extraction and chunking
  - Image OCR and captioning using Google Gemini Vision
  - Smart document indexing with vector embeddings
- **Advanced RAG Pipeline**: 
  - Semantic search with Qdrant vector database
  - Context-aware answer generation
  - Source citation and reference tracking
- **User Authentication**: Secure login and registration system
- **Modern UI/UX**: 
  - Beautiful, responsive design with Tailwind CSS
  - Real-time chat interface
  - Drag-and-drop file upload
  - Document summarization

### Tech Stack

**Frontend:**
- React 18 with Hooks
- Vite for fast development
- Tailwind CSS for styling
- React Router for navigation
- Lucide React for icons

**Backend:**
- FastAPI (Python)
- LangChain for RAG pipeline
- Google Gemini AI (LLM, Embeddings, Vision)
- Qdrant vector database
- JWT-based authentication

**Infrastructure:**
- Docker & Docker Compose
- Qdrant for vector storage
- RESTful API architecture

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- Docker and Docker Compose
- Google AI API Key ([Get one here](https://makersuite.google.com/app/apikey))

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/lake2804/ChatPDF.git
cd ChatPDF
```

### 2. Configure Environment

Create a `.env` file in the `backend` directory:

```env
# Google AI API Key (Required)
GOOGLE_API_KEY=your_google_api_key_here

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=multimodal_rag
EMBEDDING_DIM=768

# Model Configuration
LLM_MODEL=gemini-2.0-flash
VISION_MODEL=gemini-2.0-flash
EMBEDDING_MODEL=text-embedding-004

# Text Splitting
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Retrieval
DEFAULT_K=5

# Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=52428800  # 50MB
```

### 3. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

## 🚀 Running the Application

### Start Qdrant (Vector Database)

```bash
docker compose up -d qdrant
```

### Start Backend

```bash
cd backend
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend

```bash
cd frontend
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📡 API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration

### Document Management
- `GET /health` - Health check and system status
- `POST /upload` - Upload and index document
- `POST /ask` - Ask questions about documents
- `POST /summarize` - Summarize documents
- `DELETE /reset` - Reset vector database

## 🎨 Key Features

### Document Intelligence
- **Smart Upload**: Drag-and-drop or click to upload multiple file types
- **Automatic Indexing**: Documents are automatically processed and indexed
- **Multi-format Support**: PDF, DOCX, PPTX, TXT, Markdown, Images

### Chat Interface
- **Natural Language Queries**: Ask questions in plain language
- **Context-Aware Answers**: Answers based on uploaded documents
- **Source Citations**: See which documents and pages were used
- **Real-time Responses**: Fast, accurate answers

### Document Summarization
- **Automatic Summaries**: Generate document summaries
- **Custom Prompts**: Provide custom summarization instructions
- **Multi-document Support**: Summarize across multiple documents

## 📁 Project Structure

```
ChatPDF/
├── backend/
│   ├── app/
│   │   ├── api.py          # FastAPI endpoints
│   │   ├── config.py       # Configuration
│   │   ├── loader.py       # Document loaders
│   │   ├── vision.py       # Image processing
│   │   ├── embeddings.py    # Embedding models
│   │   ├── store.py        # Vector store operations
│   │   └── rag.py          # RAG pipeline
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatWindow.jsx
│   │   │   ├── FileUploader.jsx
│   │   │   ├── MessageBubble.jsx
│   │   │   ├── Login.jsx
│   │   │   └── Register.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── style.css
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
└── README.md
```

## 🧪 Testing

### Test Backend

```bash
cd backend
python test_backend.py
```

### Test Health Endpoint

```bash
curl http://localhost:8000/health
```

## 🐛 Troubleshooting

See `DEBUG_FRONTEND_BACKEND.md` and `FIX_PYPDF_ERROR.md` for common issues and solutions.

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Google AI for Gemini models and embeddings
- LangChain for RAG framework
- Qdrant for vector database
- FastAPI for backend framework
- React and Vite for frontend

---

**Built with ❤️ for intelligent document understanding**
