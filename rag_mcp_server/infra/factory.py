from ..core.interfaces import VectorStore
from ..config import get_settings
from .vector_store import InMemoryVectorStore
from .chroma_vector_store import ChromaVectorStore
from .qdrant_vector_store import QdrantVectorStore
from .pg_vector_store import PgVectorStore
import logging

logger = logging.getLogger(__name__)

def get_vector_store() -> VectorStore:
    settings = get_settings()
    store_type = settings.VECTOR_STORE_TYPE.lower()
    
    logger.info(f"Initializing Vector Store: {store_type}")
    
    if store_type == "chroma":
        return ChromaVectorStore()
    elif store_type == "qdrant":
        return QdrantVectorStore()
    elif store_type == "postgres":
        return PgVectorStore()
    elif store_type == "memory" or store_type == "faiss": # Keeping faiss config mapping to memory/simple implementation for now
        return InMemoryVectorStore()
    else:
        logger.warning(f"Unknown vector store type '{store_type}', defaulting to InMemory")
        return InMemoryVectorStore()
