from typing import List, Optional, Dict
import chromadb
from chromadb.utils import embedding_functions
from ..core.interfaces import VectorStore
from ..core.models import Chunk, SearchResult, Document
from ..config import get_settings
import uuid

class ChromaVectorStore(VectorStore):
    def __init__(self):
        settings = get_settings()
        # Using persistent client
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)
        self.collection = self.client.get_or_create_collection(name="rag_documents")
        
    async def add_chunks(self, chunks: List[Chunk]):
        if not chunks:
            return
            
        ids = [c.id for c in chunks]
        embeddings = [c.embedding for c in chunks] # Chroma handles None? No, we need embeddings.
        documents = [c.text for c in chunks]
        metadatas = []
        
        for c in chunks:
            # Flattens metadata for Chroma compatibility
            meta = {
                "document_id": c.document_id,
                "filename": c.metadata.filename,
                "created_at": c.metadata.created_at,
            }
            if c.metadata.extra:
                for k, v in c.metadata.extra.items():
                    meta[k] = str(v) # Ensure primitive types
            metadatas.append(meta)

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    async def search(self, query_embedding: List[float], limit: int = 5, filters: Optional[dict] = None) -> List[SearchResult]:
        # Translate filters to Chroma format
        # Chroma filter: {"metadata_field": "value"} or {"metadata_field": {"$eq": "value"}}
        chroma_filter = filters if filters else None
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=chroma_filter
        )
        
        # Parse results
        search_results = []
        if not results['ids']:
            return []
            
        count = len(results['ids'][0])
        for i in range(count):
            meta = results['metadatas'][0][i]
            search_results.append(SearchResult(
                chunk_id=results['ids'][0][i],
                document_id=meta.get("document_id"),
                text=results['documents'][0][i],
                # Chroma distance is not cosine similarity score directly, often L2 or Cosine Distance
                # For this generic interface, we just pass the distance/score. 
                score=results['distances'][0][i] if results['distances'] else 0.0,
                metadata=meta
            ))
            
        return search_results

    async def delete_document(self, document_id: str):
        self.collection.delete(
            where={"document_id": document_id}
        )

    async def get_document(self, document_id: str) -> Optional[Document]:
        # Retrieve all chunks for doc
        results = self.collection.get(
            where={"document_id": document_id}
        )
        
        if not results['ids']:
            return None
            
        # Reconstruct text
        full_text = "\n\n".join(results['documents'])
        # Taking metadata from first chunk
        meta = results['metadatas'][0]
        
        from ..core.models import DocumentMetadata
        
        return Document(
            id=document_id,
            content=full_text,
            metadata=DocumentMetadata(
                filename=meta.get("filename", "unknown"),
                extra=meta
            )
        )
