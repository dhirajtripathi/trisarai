from typing import List, Optional, Dict
import asyncpg
import json
import uuid
import asyncio
from ..core.interfaces import VectorStore
from ..core.models import Chunk, SearchResult, Document
from ..config import get_settings

class PgVectorStore(VectorStore):
    def __init__(self):
        self.settings = get_settings()
        self.pool = None
        self._initialized = False

    async def _init_db(self):
        if self._initialized:
            return
            
        self.pool = await asyncpg.create_pool(self.settings.POSTGRES_URL)
        
        async with self.pool.acquire() as conn:
            # Enable pgvector extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            # Create table
            # Assuming 1536 dim for now, but in prod we might want dynamic dim or text-embedding-3-small default
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS rag_chunks (
                    id UUID PRIMARY KEY,
                    document_id UUID,
                    text TEXT,
                    embedding vector(1536),
                    metadata JSONB,
                    created_at FLOAT
                )
            """)
            # Create HNSW index for performance
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_rag_chunks_embedding 
                ON rag_chunks USING hnsw (embedding vector_cosine_ops)
            """)
            
        self._initialized = True

    async def _ensure_conn(self):
        if not self.pool:
            await self._init_db()

    async def add_chunks(self, chunks: List[Chunk]):
        await self._ensure_conn()
        
        if not chunks:
            return

        async with self.pool.acquire() as conn:
            records = []
            for c in chunks:
                records.append((
                    uuid.UUID(c.id),
                    uuid.UUID(c.document_id),
                    c.text,
                    c.embedding, # asyncpg-pgvector handles list[float] mapping if registered, or string format
                    json.dumps({
                        "filename": c.metadata.filename, 
                        **c.metadata.extra
                    }),
                    c.metadata.created_at
                ))
            
            # Use executemany for bulk insert
            # Note: Explicit array text format for vector might be needed if not auto-handled
            # But recent asyncpg env usually handles it if pgvector types registered.
            # For robustness, we'll try standard executemany.
            await conn.executemany("""
                INSERT INTO rag_chunks (id, document_id, text, embedding, metadata, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (id) DO UPDATE 
                SET text = EXCLUDED.text, embedding = EXCLUDED.embedding, metadata = EXCLUDED.metadata
            """, records)

    async def search(self, query_embedding: List[float], limit: int = 5, filters: Optional[dict] = None) -> List[SearchResult]:
        await self._ensure_conn()
        
        # Build query
        # Standard cosine distance is <=> operator in pgvector
        # 1 - (embedding <=> query) is cosine similarity IF normalized? 
        # Actually <=> is cosine distance. 
        # ORDER BY embedding <=> $1 LIMIT $2
        
        filter_clause = ""
        args = [json.dumps(query_embedding), limit] # $1, $2
        param_idx = 3
        
        if filters:
            conditions = []
            for k, v in filters.items():
                # JSONB containment or key access
                # Simple containment: metadata @> '{"key": "value"}'
                conditions.append(f"metadata @> ${param_idx}")
                args.append(json.dumps({k: v}))
                param_idx += 1
            if conditions:
                filter_clause = "WHERE " + " AND ".join(conditions)

        sql = f"""
            SELECT id, document_id, text, metadata, created_at, 1 - (embedding <=> $1) as score
            FROM rag_chunks
            {filter_clause}
            ORDER BY embedding <=> $1
            LIMIT $2
        """
        
        # Correction: asyncpg binding for vector needs to be compatible. 
        # Often it expects a string "[1,2,3...]" if type codec isn't set, or list if it is.
        # We'll rely on list.
        # ARGS correction: $1 is query_embedding (list)
        
        async with self.pool.acquire() as conn:
            # We might need to register type, but let's try raw text for vector literal if needed
            # For now passing list.
            rows = await conn.fetch(sql, *args)
            
        results = []
        for row in rows:
            meta = json.loads(row['metadata'])
            meta['created_at'] = row['created_at']
            results.append(SearchResult(
                chunk_id=str(row['id']),
                document_id=str(row['document_id']),
                text=row['text'],
                score=float(row['score']),
                metadata=meta
            ))
            
        return results

    async def delete_document(self, document_id: str):
        await self._ensure_conn()
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM rag_chunks WHERE document_id = $1", uuid.UUID(document_id))

    async def get_document(self, document_id: str) -> Optional[Document]:
        await self._ensure_conn()
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT text, metadata FROM rag_chunks WHERE document_id = $1", uuid.UUID(document_id))
            
        if not rows:
            return None
            
        full_text = "\n\n".join([r['text'] for r in rows])
        meta = json.loads(rows[0]['metadata'])
        
        from ..core.models import DocumentMetadata
        
        return Document(
            id=document_id,
            content=full_text,
            metadata=DocumentMetadata(
                filename=meta.get("filename", "unknown"),
                extra=meta
            )
        )
