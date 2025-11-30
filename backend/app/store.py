"""
Vector store module for Qdrant integration.
Handles collection creation and vector store operations.
"""
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from typing import List
from app.config import QDRANT_URL, QDRANT_COLLECTION, EMBEDDING_DIM
import logging

# Use langchain-community Qdrant (more stable)
from langchain_community.vectorstores import Qdrant

logger = logging.getLogger(__name__)


def get_qdrant_client() -> QdrantClient:
    """Get Qdrant client instance."""
    return QdrantClient(url=QDRANT_URL)


def create_collection_if_not_exists() -> QdrantClient:
    """
    Create Qdrant collection if it doesn't exist.
    Returns the client instance.
    """
    client = get_qdrant_client()
    
    # Check if collection exists
    collections = client.get_collections().collections
    collection_names = [col.name for col in collections]
    
    if QDRANT_COLLECTION not in collection_names:
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=EMBEDDING_DIM,
                distance=Distance.COSINE
            )
        )
        print(f"Created collection: {QDRANT_COLLECTION}")
    else:
        print(f"Collection {QDRANT_COLLECTION} already exists")
    
    return client


def delete_collection(collection_name: str = None) -> bool:
    """Delete the Qdrant collection."""
    collection = collection_name or QDRANT_COLLECTION
    try:
        client = get_qdrant_client()
        client.delete_collection(collection_name=collection)
        logger.info(f"Deleted collection: {collection}")
        return True
    except Exception as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            logger.info(f"Collection {collection} does not exist (already deleted)")
            return True
        logger.error(f"Error deleting collection {collection}: {e}")
        return False


def create_vectorstore_from_docs(
    docs: List[Document],
    embeddings: Embeddings,
    collection_name: str = None,
    force_recreate: bool = False
) -> Qdrant:
    """
    Create Qdrant vectorstore from documents.
    
    Args:
        docs: List of LangChain Documents
        embeddings: Embeddings instance
        collection_name: Optional collection name (defaults to config)
        force_recreate: If True, delete and recreate collection if dimension mismatch
    
    Returns:
        Qdrant vectorstore instance
    """
    collection = collection_name or QDRANT_COLLECTION
    
    # Check if collection exists and has dimension mismatch
    client = get_qdrant_client()
    collections = client.get_collections().collections
    collection_names = [col.name for col in collections]
    
    if collection in collection_names:
        # Check dimension
        try:
            collection_info = client.get_collection(collection)
            existing_dim = collection_info.config.params.vectors.size
            if existing_dim != EMBEDDING_DIM:
                if force_recreate:
                    logger.info(f"Dimension mismatch detected ({existing_dim} vs {EMBEDDING_DIM}). Recreating collection...")
                    if delete_collection(collection):
                        logger.info(f"Collection {collection} deleted successfully")
                        # Recreate it
                        create_collection_if_not_exists()
                    else:
                        logger.warning(f"Failed to delete collection {collection}, trying to continue...")
                else:
                    raise ValueError(
                        f"Existing Qdrant collection is configured for vectors with {existing_dim} dimensions. "
                        f"Selected embeddings are {EMBEDDING_DIM}-dimensional. "
                        f"If you want to recreate the collection, set `force_recreate` parameter to `True`."
                    )
        except Exception as e:
            # If we can't check, try to proceed (might be empty collection)
            if "not found" not in str(e).lower():
                logger.warning(f"Could not check collection dimension: {e}")
    
    # Ensure collection exists (will create if deleted or doesn't exist)
    create_collection_if_not_exists()
    
    # Create vectorstore from documents
    vectorstore = Qdrant.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=collection,
        url=QDRANT_URL
    )
    
    return vectorstore


def get_vectorstore(
    embeddings: Embeddings,
    collection_name: str = None
) -> Qdrant:
    """
    Get existing vectorstore instance.
    
    Args:
        embeddings: Embeddings instance
        collection_name: Optional collection name (defaults to config)
    
    Returns:
        Qdrant vectorstore instance
    """
    collection = collection_name or QDRANT_COLLECTION
    
    # Create a patched QdrantClient that has search method
    client = get_qdrant_client()
    
    # Patch client.search to use query_points if search doesn't exist
    if not hasattr(client, 'search'):
        def search_patch(collection_name, query_vector, limit=10, score_threshold=None, **kwargs):
            """Patch search method to use query_points"""
            from qdrant_client.models import NamedVector
            
            # Use query_points with NamedVector (simpler approach)
            # query_vector can be a list or dict
            if isinstance(query_vector, dict):
                vector_name = list(query_vector.keys())[0]
                vector_value = query_vector[vector_name]
            else:
                vector_name = None  # Use default vector
                vector_value = query_vector
            
            # Query using query_points
            if vector_name:
                query = NamedVector(name=vector_name, vector=vector_value)
            else:
                query = vector_value  # Direct vector for default
            
            results = client.query_points(
                collection_name=collection_name,
                query=query,
                limit=limit,
                score_threshold=score_threshold,
                **{k: v for k, v in kwargs.items() if k not in ['query_filter', 'with_payload', 'with_vectors']}
            )
            
            # Convert to format expected by langchain
            class SearchResult:
                def __init__(self, point):
                    self.id = point.id
                    self.score = point.score if hasattr(point, 'score') else 0.0
                    self.payload = point.payload if hasattr(point, 'payload') else {}
            
            return [SearchResult(point) for point in results.points]
        
        client.search = search_patch
    
    # Both old and new Qdrant use 'embeddings' parameter
    vectorstore = Qdrant(
        client=client,
        collection_name=collection,
        embeddings=embeddings
    )
    
    return vectorstore

