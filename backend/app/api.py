"""
FastAPI application with endpoints for document upload, querying, and management.
"""
import os
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import logging
from app.rag import build_and_store_index, rag_query
from app.store import delete_collection, get_qdrant_client
from app.config import UPLOAD_DIR, MAX_FILE_SIZE, QDRANT_COLLECTION

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Multimodal RAG Chatbot API",
    description="RAG system supporting PDF, DOCX, PPTX, TXT, Markdown, and Images",
    version="1.0.0"
)

# CORS middleware
# Allow origins from environment variable or default to all
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins_str == "*":
    allowed_origins = ["*"]
else:
    allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory (relative to backend folder)
UPLOAD_PATH = Path(UPLOAD_DIR)
if not UPLOAD_PATH.is_absolute():
    # If relative path, make it relative to backend directory
    backend_dir = Path(__file__).parent.parent
    UPLOAD_PATH = backend_dir / UPLOAD_DIR
UPLOAD_PATH.mkdir(exist_ok=True, parents=True)

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".pptx", ".txt", ".md", ".markdown",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"
}


@app.get("/health")
async def health_check():
    """Health check endpoint - simplified for Railway healthcheck."""
    # Simple healthcheck that always returns 200 OK
    # This ensures Railway healthcheck passes even if some services are not ready
    return {"status": "healthy", "service": "chatpdf-api"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and index a document file.
    Supports: PDF, DOCX, PPTX, TXT, Markdown, Images (PNG, JPG, etc.)
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        )
    
    # Save file (handle duplicate names)
    file_path = UPLOAD_PATH / file.filename
    counter = 1
    original_name = file.filename
    while file_path.exists():
        name_parts = original_name.rsplit('.', 1)
        if len(name_parts) == 2:
            new_name = f"{name_parts[0]}_{counter}.{name_parts[1]}"
        else:
            new_name = f"{original_name}_{counter}"
        file_path = UPLOAD_PATH / new_name
        counter += 1
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to start
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.1f}MB"
        )
    
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        logger.info(f"File saved: {file_path}")
        
        # Build and store index
        # Try with force_recreate=False first, if dimension mismatch, retry with force_recreate=True
        try:
            chunk_count = build_and_store_index(str(file_path), force_recreate=False)
        except (ValueError, Exception) as e:
            error_msg = str(e)
            if "dimension" in error_msg.lower() or "dimensions" in error_msg.lower():
                # Dimension mismatch - recreate collection
                logger.warning(f"Dimension mismatch detected. Recreating collection...")
                try:
                    chunk_count = build_and_store_index(str(file_path), force_recreate=True)
                except Exception as retry_error:
                    logger.error(f"Failed to recreate collection and index: {retry_error}")
                    # Clean up file on error
                    if file_path.exists():
                        file_path.unlink()
                    raise HTTPException(
                        status_code=500, 
                        detail=f"Failed to index file: {str(retry_error)}"
                    )
            else:
                # Clean up file on error
                if file_path.exists():
                    file_path.unlink()
                # Provide more helpful error messages
                if "GOOGLE_API_KEY" in error_msg or "API key" in error_msg:
                    raise HTTPException(
                        status_code=500,
                        detail="Google API key is missing or invalid. Please check your .env file."
                    )
                elif "qdrant" in error_msg.lower() or "connection" in error_msg.lower():
                    raise HTTPException(
                        status_code=500,
                        detail="Cannot connect to Qdrant vector database. Please ensure Qdrant is running."
                    )
                elif "pypdf" in error_msg.lower():
                    import sys
                    detailed_msg = f"pypdf package not found in backend Python environment.\n"
                    detailed_msg += f"Backend Python: {sys.executable}\n"
                    detailed_msg += f"Please install: pip install pypdf\n"
                    detailed_msg += f"Or restart backend with correct virtual environment."
                    raise HTTPException(
                        status_code=500,
                        detail=detailed_msg
                    )
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error processing file: {error_msg}"
                    )
        
        return {
            "status": "success",
            "message": "File uploaded and indexed successfully",
            "filename": file.filename,
            "chunks_indexed": chunk_count,
            "file_type": file_ext
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing file: {e}", exc_info=True)
        # Clean up file on error
        if file_path.exists():
            try:
                file_path.unlink()
            except:
                pass
        error_msg = str(e)
        if "GOOGLE_API_KEY" in error_msg or "API key" in error_msg:
            error_msg = "Google API key is missing or invalid. Please check your .env file."
        elif "qdrant" in error_msg.lower() or "connection" in error_msg.lower():
            error_msg = "Cannot connect to Qdrant vector database. Please ensure Qdrant is running."
        raise HTTPException(status_code=500, detail=f"Error processing file: {error_msg}")


class AskRequest(BaseModel):
    question: str
    k: Optional[int] = None
    stream: bool = False

@app.post("/summarize")
async def summarize_document(
    request: Optional[AskRequest] = None,
    question: Optional[str] = Query(None)
):
    """
    Summarize the uploaded documents.
    """
    final_question = question or (request.question if request else None) or "Tóm tắt nội dung chính của tài liệu này một cách chi tiết và đầy đủ."
    
    try:
        result = rag_query(final_question, k=10, stream=False)  # Use more chunks for summary
        return {
            "summary": result["answer"],
            "source_count": result["source_count"],
            "sources": [
                {
                    "index": i + 1,
                    "source_file": doc.metadata.get("source_file", "Unknown"),
                    "page": doc.metadata.get("page"),
                    "slide_number": doc.metadata.get("slide_number"),
                    "preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                }
                for i, doc in enumerate(result["sources"])
            ]
        }
    except Exception as e:
        logger.error(f"Error generating summary: {e}", exc_info=True)
        error_msg = str(e)
        if "GOOGLE_API_KEY" in error_msg or "API key" in error_msg or "authentication" in error_msg.lower():
            error_msg = "Google API key is missing or invalid. Please check your .env file."
        elif "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            error_msg = "Google API quota exceeded or rate limited. Please try again later or check your API quota."
        elif "collection" in error_msg.lower() or "qdrant" in error_msg.lower() or "connection" in error_msg.lower():
            error_msg = "Vector database error. Please ensure Qdrant is running and you have uploaded at least one document."
        elif "No documents" in error_msg or "empty" in error_msg.lower() or "No documents indexed" in error_msg:
            error_msg = "No documents found. Please upload at least one document first."
        elif "Failed to retrieve" in error_msg or "retrieve documents" in error_msg.lower():
            error_msg = "Failed to retrieve documents from vector database. Please ensure documents are properly indexed."
        elif "Failed to generate answer" in error_msg:
            # Keep the detailed error message from rag_query
            pass
        raise HTTPException(status_code=500, detail=error_msg)


@app.post("/ask")
async def ask_question(
    request: Optional[AskRequest] = None,
    question: Optional[str] = Query(None),
    k: Optional[int] = Query(None),
    stream: bool = Query(False)
):
    """
    Ask a question and get an answer based on indexed documents.
    Supports both JSON body and query parameters (body takes precedence).
    """
    # Support both request body and query parameters (body takes precedence)
    final_question = question
    final_k = k
    final_stream = stream
    
    if request:
        final_question = request.question
        final_k = request.k if request.k is not None else k
        final_stream = request.stream if request.stream else stream
    
    if not final_question or not final_question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        result = rag_query(final_question, k=final_k, stream=final_stream)
        
        if final_stream:
            # Return streaming response
            def generate():
                import json
                yield '{"answer": "'
                answer_stream = result.get("answer_stream")
                if answer_stream:
                    try:
                        for chunk in answer_stream:
                            # Escape JSON special characters
                            chunk_escaped = chunk.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                            yield chunk_escaped
                    except Exception as e:
                        logger.error(f"Error in streaming: {e}")
                        yield "Error in streaming response"
                yield f'", "source_count": {result["source_count"]}, "sources": ['
                
                # Add sources info
                sources_info = []
                for i, doc in enumerate(result["sources"]):
                    source_info = {
                        "index": i + 1,
                        "source_file": doc.metadata.get("source_file", "Unknown"),
                        "page": doc.metadata.get("page"),
                        "slide_number": doc.metadata.get("slide_number"),
                        "content_type": doc.metadata.get("content_type"),
                        "preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                    }
                    sources_info.append(source_info)
                
                yield json.dumps(sources_info)
                yield ']}'
            
            return StreamingResponse(
                generate(),
                media_type="application/json",
                headers={"X-Accel-Buffering": "no"}  # Disable buffering for streaming
            )
        else:
            # Return non-streaming response
            sources_info = []
            for i, doc in enumerate(result["sources"]):
                sources_info.append({
                    "index": i + 1,
                    "source_file": doc.metadata.get("source_file", "Unknown"),
                    "page": doc.metadata.get("page"),
                    "slide_number": doc.metadata.get("slide_number"),
                    "content_type": doc.metadata.get("content_type"),
                    "preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                })
            
            return {
                "answer": result["answer"],
                "source_count": result["source_count"],
                "sources": sources_info
            }
    except Exception as e:
        logger.error(f"Error processing question: {e}", exc_info=True)
        error_msg = str(e)
        # Provide more helpful error messages
        if "GOOGLE_API_KEY" in error_msg or "API key" in error_msg or "authentication" in error_msg.lower():
            error_msg = "Google API key is missing or invalid. Please check your .env file."
        elif "collection" in error_msg.lower() or "qdrant" in error_msg.lower() or "connection" in error_msg.lower():
            error_msg = "Vector database error. Please ensure Qdrant is running and you have uploaded at least one document."
        elif "No documents" in error_msg or "empty" in error_msg.lower() or "No documents indexed" in error_msg:
            error_msg = "No documents found. Please upload at least one document first."
        elif "Failed to retrieve" in error_msg or "retrieve documents" in error_msg.lower():
            error_msg = "Failed to retrieve documents from vector database. Please ensure documents are properly indexed."
        elif "Failed to generate answer" in error_msg:
            # Keep the detailed error message from rag_query
            pass
        raise HTTPException(status_code=500, detail=error_msg)


@app.delete("/reset")
async def reset_index():
    """
    Reset the vector database by deleting the collection.
    This will remove all indexed documents.
    """
    try:
        success = delete_collection()
        if success:
            # Also clear uploads directory
            for file_path in UPLOAD_PATH.iterdir():
                if file_path.is_file():
                    file_path.unlink()
            
            return {
                "status": "success",
                "message": "Vector database and uploads reset successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to reset database")
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        raise HTTPException(status_code=500, detail=f"Error resetting database: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

