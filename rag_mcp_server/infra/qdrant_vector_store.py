from typing import List, Optional, Dict
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from ..core.interfaces import VectorStore
from ..core.models import Chunk, SearchResult, Document
from ..config import get_settings
import uuid

class QdrantVectorStore(VectorStore):
    def __init__(self):
        settings = get_settings()
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None
        )
        self.collection_name = "rag_documents"
        
        # Ensure collection exists
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            # Create collection with default vector size (OpenAI small = 1536)
            # In production, vector size should be configurable
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=rest.VectorParams(size=1536, distance=rest.Distance.COSINE)
            )

    async def add_chunks(self, chunks: List[Chunk]):
        if not chunks:
            return

        points = []
        for c in chunks:
            payload = {
                "document_id": c.document_id,
                "text": c.text,
                "filename": c.metadata.filename,
                "created_at": c.metadata.created_at,
                **c.metadata.extra
            }
            
            points.append(rest.PointStruct(
                id=str(uuid.UUID(c.id)), # Qdrant prefers UUID objects or ints
                vector=c.embedding,
                payload=payload
            ))
            
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    async def search(self, query_embedding: List[float], limit: int = 5, filters: Optional[dict] = None) -> List[SearchResult]:
        # Build filter
        query_filter = None
        if filters:
            conditions = []
            for k, v in filters.items():
                conditions.append(
                    rest.FieldCondition(
                        key=k,
                        match=rest.MatchValue(value=v)
                    )
                )
            query_filter = rest.Filter(must=conditions)

        hits = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            query_filter=query_filter
        )
        
        results = []
        for hit in hits:
            results.append(SearchResult(
                chunk_id=str(hit.id),
                document_id=hit.payload.get("document_id"),
                text=hit.payload.get("text"),
                score=hit.score,
                metadata=hit.payload
            ))
            
        return results

    async def delete_document(self, document_id: str):
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=rest.FilterSelector(
                filter=rest.Filter(
                    must=[
                        rest.FieldCondition(
                            key="document_id",
                            match=rest.MatchValue(value=document_id)
                        )
                    ]
                )
            )
        )

    async def get_document(self, document_id: str) -> Optional[Document]:
        # Qdrant scroll/search to get all chunks
        # This can be heavy for large docs, but OK for POC
        hits, _ = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=rest.Filter(
                must=[
                    rest.FieldCondition(
                        key="document_id",
                        match=rest.MatchValue(value=document_id)
                    )
                ]
            ),
            limit=1000 # Configurable limit
        )
        
        if not hits:
            return None
            
        full_text = "\n\n".join([h.payload.get("text", "") for h in hits])
        meta = hits[0].payload
        from ..core.models import DocumentMetadata
        
        return Document(
            id=document_id,
            content=full_text,
            metadata=DocumentMetadata(
                filename=meta.get("filename", "unknown"),
                extra=meta
            )
        )
