import faiss
import numpy as np
import pickle
import os
from typing import List, Optional
from ..core.interfaces import VectorStore, Document
from ..core.models import SearchResult
from ..config import get_settings

class FaissVectorStore(VectorStore):
    def __init__(self, index_file: str = "faiss_index.bin", doc_store_file: str = "doc_store.pkl", dimension: int = 1536):
        settings = get_settings()
        self.storage_dir = settings.STORAGE_DIR
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
            
        self.index_path = os.path.join(self.storage_dir, index_file)
        self.doc_path = os.path.join(self.storage_dir, doc_store_file)
        self.dimension = dimension
        
        self.docs = {} # id -> Document
        self.id_map = {} # int_id -> str_uuid
        
        self._load()

    def _load(self):
        if os.path.exists(self.index_path) and os.path.exists(self.doc_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.doc_path, "rb") as f:
                    data = pickle.load(f)
                    self.docs = data.get("docs", {})
                    self.id_map = data.get("id_map", {})
            except Exception as e:
                print(f"Error loading FAISS index: {e}. creating new one.")
                self.index = faiss.IndexFlatL2(self.dimension)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)

    def _save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.doc_path, "wb") as f:
            pickle.dump({"docs": self.docs, "id_map": self.id_map}, f)

    async def add_documents(self, documents: List[Document]):
        # Just an alias for add_chunks really
        await self.add_chunks(documents)

    async def add_chunks(self, chunks: List[Document]):
        if not chunks:
            return

        vectors = [c.embedding for c in chunks]
        
        # Ensure vectors are numpy arrays of float32
        vectors_np = np.array(vectors).astype('float32')
        
        # FAISS dimensions check
        if vectors_np.shape[1] != self.dimension:
            # Recreate index if dimension mismatch (simple handling)
            # In proper production you'd migrate or warn
            if self.index.ntotal == 0:
                 self.dimension = vectors_np.shape[1]
                 self.index = faiss.IndexFlatL2(self.dimension)
            else:
                 raise ValueError(f"Dimension mismatch: Index={self.dimension}, New={vectors_np.shape[1]}")

        start_id = self.index.ntotal
        self.index.add(vectors_np)
        
        for i, chunk in enumerate(chunks):
            int_id = start_id + i
            self.docs[chunk.document_id] = chunk
            self.id_map[int_id] = chunk.document_id
            
        self._save()

    async def search(self, query_vector: List[float], limit: int = 5) -> List[SearchResult]:
        if self.index.ntotal == 0:
            return []
            
        q_vec = np.array([query_vector]).astype('float32')
        D, I = self.index.search(q_vec, limit)
        
        results = []
        for i, idx in enumerate(I[0]):
            if idx == -1: continue
            doc_id = self.id_map.get(idx)
            if doc_id and doc_id in self.docs:
                doc = self.docs[doc_id]
                # FAISS L2 distance: Lower is better. 
                # To make it a "score" (higher better), we can invert or normalize.
                # Common trick: 1 / (1 + distance)
                distance = D[0][i]
                score = 1 / (1 + distance)
                
                results.append(SearchResult(
                    text=doc.text,
                    metadata=doc.metadata,
                    score=float(score)
                ))
        
        return results

    async def delete_document(self, document_id: str):
        # FAISS is append-only mostly for Flat index unless using IDMap, 
        # but pure delete is hard without rebuilding.
        # Simple Logic: Remove from doc store, rebuild index (EXPENSIVE but safe for simple use)
        
        if document_id in self.docs:
            del self.docs[document_id]
            
            # Rebuild necessary
            # Filter out deleted ID from id_map logic? 
            # Actually easier to just rebuild from remaining docs
            
            new_index = faiss.IndexFlatL2(self.dimension)
            new_id_map = {}
            new_docs_list = list(self.docs.values())
            
            if new_docs_list:
                vectors = [d.embedding for d in new_docs_list]
                vectors_np = np.array(vectors).astype('float32')
                new_index.add(vectors_np)
                
                for i, doc in enumerate(new_docs_list):
                    new_id_map[i] = doc.document_id
            
            self.index = new_index
            self.id_map = new_id_map
            self._save()

    async def get_document(self, document_id: str) -> Optional[Document]:
        return self.docs.get(document_id)
