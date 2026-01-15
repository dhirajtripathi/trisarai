from ..core.interfaces import DocumentProcessor, Embedder
from ..config import get_settings
from ..services.text_processing import DefaultDocumentProcessor
from ..services.chunking_strategies import RecursiveTokenChunker, SemanticChunker
import logging

logger = logging.getLogger(__name__)

def get_document_processor(embedder: Embedder = None) -> DocumentProcessor:
    settings = get_settings()
    strategy = settings.CHUNKING_STRATEGY.lower()
    
    logger.info(f"Initializing Chunking Strategy: {strategy}")
    
    if strategy == "recursive":
        return RecursiveTokenChunker()
    elif strategy == "semantic":
        if not embedder:
            logger.warning("Semantic chunking requires embedder, falling back to recursive")
            return RecursiveTokenChunker()
        return SemanticChunker(embedder)
    elif strategy == "sliding":
        return DefaultDocumentProcessor()
    else:
        logger.warning(f"Unknown chunking strategy '{strategy}', defaulting to sliding window")
        return DefaultDocumentProcessor()
