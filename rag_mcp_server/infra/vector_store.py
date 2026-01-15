import numpy as np
from typing import List, Optional, Dict
import threading
from ..core.interfaces import VectorStore
from ..core.models import Chunk, SearchResult, Document
from ..config import get_settings

class InMemoryVectorStore(VectorStore):
    def __init__(self):
        self.chunks: Dict[str, Chunk] = {}
        self.vectors: Optional[np.ndarray] = None
        self.ids: List[str] = []
        self._lock = threading.Lock()
        
    def _update_index(self):
        # Rebuild simple index
        if not self.chunks:
            self.vectors = None
            self.ids = []
            return

        # Sort chunks to ensure aligned order
        sorted_ids = sorted(self.chunks.keys())
        embeddings = [self.chunks[uid].embedding for uid in sorted_ids]
        
        # Check if any embedding is None
        valid_embeddings = []
        valid_ids = []
        for uid, emb in zip(sorted_ids, embeddings):
            if emb is not None:
                valid_embeddings.append(emb)
                valid_ids.append(uid)
        
        if valid_embeddings:
            self.vectors = np.array(valid_embeddings, dtype=np.float32)
            # Normalize for cosine similarity
            norm = np.linalg.norm(self.vectors, axis=1, keepdims=True)
            self.vectors = self.vectors / (norm + 1e-10)
            self.ids = valid_ids
        else:
            self.vectors = None
            self.ids = []

    async def add_chunks(self, chunks: List[Chunk]):
        with self._lock:
            for chunk in chunks:
                self.chunks[chunk.id] = chunk
            self._update_index()

    async def search(self, query_embedding: List[float], limit: int = 5, filters: Optional[dict] = None) -> List[SearchResult]:
        if self.vectors is None or len(self.ids) == 0:
            return []
            
        # Prepare query
        q_vec = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        q_vec = q_vec / (q_norm + 1e-10)
        
        # Calculate similarity
        scores = np.dot(self.vectors, q_vec)
        
        # Get top k
        # We start with more candidates to allow for filtering
        k = min(len(scores), limit * 2 if filters else limit)
        top_k_indices = np.argsort(scores)[::-1][:k]
        
        results = []
        count = 0
        for idx in top_k_indices:
            chunk_id = self.ids[idx]
            chunk = self.chunks[chunk_id]
            
            # Apply filters if any (simple exact match on metadata)
            if filters:
                match = True
                for key, val in filters.items():
                    # Check if key exists in extra or is a direct attribute
                    if hasattr(chunk.metadata, key):
                         if getattr(chunk.metadata, key) != val:
                             match = False; break
                    elif key in chunk.metadata.extra:
                         if chunk.metadata.extra[key] != val:
                             match = False; break
                    else:
                        match = False; break
                if not match:
                    continue

            results.append(SearchResult(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                text=chunk.text,
                score=float(scores[idx]),
                metadata={
                    "filename": chunk.metadata.filename,
                    "created_at": chunk.metadata.created_at,
                    **chunk.metadata.extra
                }
            ))
            count += 1
            if count >= limit:
                break
                
        return results

    async def delete_document(self, document_id: str):
        with self._lock:
            keys_to_delete = [k for k, v in self.chunks.items() if v.document_id == document_id]
            for k in keys_to_delete:
                del self.chunks[k]
            self._update_index()

    async def get_document(self, document_id: str) -> Optional[Document]:
        # reconstruct document from chunks
        chunks = [v for v in self.chunks.values() if v.document_id == document_id]
        if not chunks:
            return None
            
        # In a real system, we'd store the full doc separately or have chunk order.
        # Here we just join them. Assuming simple order isn't guaranteed without an index.
        # But for this MVP, we join blindly.
        full_text = "\n\n".join([c.text for c in chunks])
        first_chunk = chunks[0]
        
        return Document(
            id=document_id,
            content=full_text,
            metadata=first_chunk.metadata
        )
