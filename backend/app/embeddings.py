"""
Embeddings module using Google text-embedding-004 model.
"""
from typing import List
from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import EMBEDDING_MODEL, GOOGLE_API_KEY


class GoogleEmbeddings(Embeddings):
    """
    Wrapper for Google text-embedding-004 model.
    Implements LangChain Embeddings interface.
    """
    
    def __init__(self):
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not set. Please set it in .env file.")
        self.embeddings_client = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL,
            google_api_key=GOOGLE_API_KEY
        )
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        return self.embeddings_client.embed_documents(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query string."""
        return self.embeddings_client.embed_query(text)

