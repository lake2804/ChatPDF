# ChatPDF - AI-Powered Document Chat Platform

A production-ready full-stack Multimodal Retrieval-Augmented Generation (RAG) chatbot that enables natural language conversations with documents. Built with modern technologies including FastAPI, React, and Google Gemini AI.

## 🚀 Features

### Core Capabilities
- **Multi-Format Document Support**: PDF, DOCX, PPTX, TXT, Markdown, and Images
- **Intelligent Document Processing**: 
  - Automatic text extraction and chunking
  - Image OCR and captioning using Google Gemini Vision
  - Smart document indexing with vector embeddings
  - Image extraction from PDF and PPTX files
- **Advanced RAG Pipeline**: 
  - Semantic search with Qdrant vector database
  - Context-aware answer generation with no output limits
  - Source citation and reference tracking
  - Language-aware responses (Vietnamese/English)
- **User Authentication**: Secure login and registration system
- **Modern UI/UX**: 
  - Beautiful, responsive design with Tailwind CSS
  - Real-time chat interface with progress tracking
  - Drag-and-drop file upload with progress bar
  - Document summarization
  - Markdown rendering for better answer formatting

### Tech Stack

**Frontend:**
- React 18 with Hooks
- Vite for fast development
- Tailwind CSS for styling
- React Router for navigation
- React Markdown for content rendering
- Lucide React for icons

**Backend:**
- FastAPI (Python 3.11+)
- LangChain for RAG pipeline
- Google Gemini AI (LLM, Embeddings, Vision)
- Qdrant vector database
- PyMuPDF, PyPDF for PDF processing
- python-docx, python-pptx for Office documents

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

# CORS (for production)
ALLOWED_ORIGINS=http://localhost:3000
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

Verify Qdrant is running:
```bash
curl http://localhost:6333/health
```

### Start Backend

```bash
cd backend
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Start Frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at: http://localhost:3000

## 📡 API Endpoints

### Health Check
- `GET /health` - Health check and system status

### Document Management
- `POST /upload` - Upload and index document
  - Supports: PDF, DOCX, PPTX, TXT, Markdown, Images
  - Returns: filename, chunks_indexed, file_type

### Query & Chat
- `POST /ask` - Ask questions about documents
  - Body: `{ "question": "your question", "k": 5, "stream": false }`
  - Returns: answer, sources, source_count

- `POST /summarize` - Summarize documents
  - Body: `{ "question": "optional custom prompt" }`
  - Returns: summary, sources, source_count

### Database Management
- `DELETE /reset` - Reset vector database (delete all indexed documents)

## 🏗️ Architecture

### How It Works

1. **Document Upload & Processing**
   - User uploads document (PDF, DOCX, PPTX, etc.)
   - Backend extracts text and images
   - Images are processed with OCR and captioning
   - Text is split into chunks with overlap

2. **Vector Indexing**
   - Each chunk is converted to embeddings using Google's text-embedding-004
   - Embeddings are stored in Qdrant vector database
   - Metadata (page numbers, file names) is preserved

3. **Query Processing**
   - User asks a question
   - Question is converted to embedding
   - Similar chunks are retrieved from Qdrant
   - Context is sent to Google Gemini LLM
   - LLM generates comprehensive answer based on context

4. **Response Generation**
   - Answer is formatted with markdown
   - Sources are cited with page numbers
   - Response language matches question language

### Project Structure

```
ChatPDF/
├── backend/
│   ├── app/
│   │   ├── api.py          # FastAPI endpoints and routes
│   │   ├── config.py       # Configuration and environment variables
│   │   ├── loader.py       # Document loaders (PDF, DOCX, PPTX, etc.)
│   │   ├── vision.py       # Image processing (OCR, captioning)
│   │   ├── embeddings.py   # Google embedding models
│   │   ├── store.py        # Qdrant vector store operations
│   │   └── rag.py          # RAG pipeline (retrieval + generation)
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Docker configuration
│   └── uploads/            # Uploaded documents storage
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatWindow.jsx    # Main chat interface
│   │   │   ├── FileUploader.jsx # File upload with progress
│   │   │   ├── MessageBubble.jsx # Message display with markdown
│   │   │   ├── Login.jsx        # Login component
│   │   │   └── Register.jsx     # Registration component
│   │   ├── App.jsx              # Main app component
│   │   ├── main.jsx             # Entry point
│   │   └── style.css            # Global styles
│   ├── package.json
│   └── vite.config.js          # Vite configuration
├── docker-compose.yml          # Qdrant service configuration
├── railway.json                # Railway deployment config
└── README.md
```

## 🎨 Key Features Explained

### Document Intelligence
- **Smart Upload**: Drag-and-drop or click to upload
- **Progress Tracking**: Real-time upload progress bar
- **Automatic Indexing**: Documents processed automatically
- **Multi-format Support**: PDF, DOCX, PPTX, TXT, Markdown, Images
- **Image Processing**: Automatic OCR and captioning for images in documents

### Chat Interface
- **Natural Language Queries**: Ask questions in plain language
- **Context-Aware Answers**: Answers based on uploaded documents
- **Comprehensive Responses**: No output limits, detailed answers
- **Language Detection**: Automatically responds in question language
- **Source Citations**: See which documents and pages were used
- **Markdown Formatting**: Beautifully formatted answers with lists, headings, etc.

### Document Summarization
- **Automatic Summaries**: Generate document summaries
- **Custom Prompts**: Provide custom summarization instructions
- **Multi-document Support**: Summarize across multiple documents

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google AI API key (required) | - |
| `QDRANT_URL` | Qdrant server URL | `http://localhost:6333` |
| `QDRANT_COLLECTION` | Collection name | `multimodal_rag` |
| `EMBEDDING_DIM` | Embedding dimension | `768` |
| `LLM_MODEL` | LLM model name | `gemini-2.0-flash` |
| `VISION_MODEL` | Vision model name | `gemini-2.0-flash` |
| `CHUNK_SIZE` | Text chunk size | `1000` |
| `CHUNK_OVERLAP` | Chunk overlap | `200` |
| `DEFAULT_K` | Default retrieval count | `5` |
| `MAX_FILE_SIZE` | Max upload size (bytes) | `52428800` (50MB) |
| `ALLOWED_ORIGINS` | CORS allowed origins | `*` |

### Model Configuration

The project uses Google Gemini models:
- **LLM**: `gemini-2.0-flash` - For answer generation
- **Vision**: `gemini-2.0-flash` - For image OCR and captioning
- **Embeddings**: `text-embedding-004` - For vector embeddings

## 🧪 Testing

### Test Health Endpoint

```bash
curl http://localhost:8000/health
```

### Test Upload

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@your-document.pdf"
```

### Test Query

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'
```

## 🐛 Troubleshooting

### Common Issues

1. **Backend không kết nối được Qdrant**
   ```bash
   # Kiểm tra Docker đang chạy
   docker ps
   
   # Khởi động Qdrant
   docker compose up -d qdrant
   
   # Kiểm tra health
   curl http://localhost:6333/health
   ```

2. **Google API Key Error**
   - Kiểm tra file `.env` trong thư mục `backend`
   - Đảm bảo API key hợp lệ và có quota
   - Lấy API key tại: https://makersuite.google.com/app/apikey

3. **Module not found errors**
   ```bash
   # Cài đặt lại dependencies
   cd backend
   pip install -r requirements.txt
   
   # Kiểm tra virtual environment
   python --version  # Should be 3.11+
   ```

4. **File upload fails**
   - Kiểm tra file size (max 50MB)
   - Kiểm tra file format (PDF, DOCX, PPTX, TXT, MD, Images)
   - Xem backend logs để biết lỗi chi tiết

5. **Frontend không kết nối backend**
   - Kiểm tra backend đang chạy tại http://localhost:8000
   - Kiểm tra CORS settings trong backend
   - Kiểm tra `VITE_API_BASE` trong frontend

## 🚀 Deployment

### Local Development
Follow the installation and running instructions above.

### Production Deployment

For production deployment, consider:
- **Frontend**: Vercel, Netlify, or any static hosting
- **Backend**: Railway, Render, Fly.io, or VPS
- **Database**: Qdrant Cloud or self-hosted Qdrant

Key considerations:
- Set `ALLOWED_ORIGINS` to your frontend domain
- Use Qdrant Cloud for managed database
- Configure environment variables in hosting platform
- Enable HTTPS for production

## 📝 Development

### Adding New Document Types

1. Add loader function in `backend/app/loader.py`
2. Add file extension to `SUPPORTED_EXTENSIONS` in `backend/app/api.py`
3. Update frontend `FileUploader.jsx` to accept new type

### Customizing RAG Pipeline

Modify `backend/app/rag.py`:
- Adjust chunk size and overlap
- Change retrieval count (k)
- Modify prompt templates
- Adjust temperature and other LLM parameters

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Google AI for Gemini models and embeddings
- LangChain for RAG framework
- Qdrant for vector database
- FastAPI for backend framework
- React and Vite for frontend

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For issues and questions, please open an issue on GitHub: https://github.com/lake2804/ChatPDF/issues

---

**Built with ❤️ for intelligent document understanding**
