"""
Configuration module for the RAG application.
Loads environment variables and sets up application settings.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Google AI API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_google_api_key_here":
    import warnings
    warnings.warn(
        "GOOGLE_API_KEY not set or using placeholder. "
        "Please set GOOGLE_API_KEY in .env file. "
        "Get your API key from: https://makersuite.google.com/app/apikey",
        UserWarning
    )

# Qdrant Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "multimodal_rag")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "768"))  # text-embedding-004 uses 768 dimensions

# Model Configuration
EMBEDDING_MODEL = "text-embedding-004"  # Google embedding model
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")
VISION_MODEL = os.getenv("VISION_MODEL", "gemini-2.0-flash")

# Text Splitting Configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Retrieval Configuration
DEFAULT_K = int(os.getenv("DEFAULT_K", "5"))

# Upload Configuration
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "50")) * 1024 * 1024  # 50MB default

