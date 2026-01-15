from abc import ABC, abstractmethod
from typing import List, Optional
from .models import Document, Chunk, SearchResult

class DocumentProcessor(ABC):
    @abstractmethod
    async def process(self, content: str, filename: str, metadata: dict) -> List[Chunk]:
        """Split content into chunks with metadata."""
        pass

class Embedder(ABC):
    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a query string."""
        pass

    @abstractmethod
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of document chunks."""
        pass

class VectorStore(ABC):
    @abstractmethod
    async def add_chunks(self, chunks: List[Chunk]):
        """Add chunks to the store."""
        pass

    @abstractmethod
    async def search(self, query_embedding: List[float], limit: int = 5, filters: Optional[dict] = None) -> List[SearchResult]:
        """Search for similar chunks."""
        pass

    @abstractmethod
    async def delete_document(self, document_id: str):
        """Delete all chunks associated with a document ID."""
        pass
        
    @abstractmethod
    async def get_document(self, document_id: str) -> Optional[Document]:
        """Retrieve full document text if stored (or reconstructed)."""
        pass
