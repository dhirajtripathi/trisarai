import uuid
from typing import List
import tiktoken
import numpy as np
import re
from ..core.interfaces import DocumentProcessor, Embedder
from ..core.models import Chunk, DocumentMetadata
from ..config import get_settings

class RecursiveTokenChunker(DocumentProcessor):
    def __init__(self):
        self.settings = get_settings()
        self.encoding = tiktoken.get_encoding("cl100k_base") # OpenAI Default
        self.chunk_size = self.settings.CHUNK_SIZE
        self.chunk_overlap = self.settings.CHUNK_OVERLAP

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text by separators until chunks represent token limits."""
        final_chunks = []
        if not separators:
            # Base case: no more separators, hard split by tokens if needed
            tokens = self.encoding.encode(text)
            for i in range(0, len(tokens), self.chunk_size - self.chunk_overlap):
                chunk_text = self.encoding.decode(tokens[i:i + self.chunk_size])
                final_chunks.append(chunk_text)
            return final_chunks

        separator = separators[0]
        splits = text.split(separator)
        
        current_chunk = []
        current_len = 0
        
        for split in splits:
            split_len = len(self.encoding.encode(split))
            
            if split_len > self.chunk_size:
                # If a single split is too big, recurse on it with next separator
                if current_chunk:
                    final_chunks.append(separator.join(current_chunk))
                    current_chunk = []
                    current_len = 0
                final_chunks.extend(self._split_text(split, separators[1:]))
                continue

            if current_len + split_len > self.chunk_size:
                final_chunks.append(separator.join(current_chunk))
                current_chunk = [split]
                current_len = split_len
            else:
                current_chunk.append(split)
                current_len += split_len
                
        if current_chunk:
            final_chunks.append(separator.join(current_chunk))
            
        return final_chunks

    async def process(self, content: str, filename: str, metadata: dict) -> List[Chunk]:
        separators = ["\n\n", "\n", ".", " ", ""]
        text_chunks = self._split_text(content, separators)
        
        doc_id = str(uuid.uuid4())
        chunks = []
        for i, text in enumerate(text_chunks):
            if not text.strip(): continue
            chunk_id = str(uuid.uuid4())
            chunks.append(Chunk(
                id=chunk_id,
                document_id=doc_id,
                text=text.strip(),
                metadata=DocumentMetadata(
                    filename=filename,
                    extra={**metadata, "chunk_index": i}
                )
            ))
        return chunks

class SemanticChunker(DocumentProcessor):
    def __init__(self, embedder: Embedder):
        self.settings = get_settings()
        self.embedder = embedder
        self.threshold = self.settings.SEMANTIC_CHUNK_THRESHOLD

    async def _embed_sentences(self, sentences: List[str]):
        return await self.embedder.embed_documents(sentences)

    def _split_sentences(self, text: str) -> List[str]:
        # Simple regex split for sentences
        return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

    async def process_async(self, content: str, filename: str, metadata: dict) -> List[Chunk]:
        # Semantic chunking requires async embedding, but the interface is sync process()
        # We will need to adapt or rely on the fact that Embedder is async.
        # Since standard DocumentProcessor.process is sync, and semantic needs I/O, 
        # we might violate the interface or need to update the interface to be async.
        # For now, let's assume we can run loop or we update interface.
        # Given potential complexity, I will create a helper and run it.
        sentences = self._split_sentences(content)
        if not sentences:
            return []
            
        embeddings = await self._embed_sentences(sentences)
        
        # Calculate cosine similarity between adjacent sentences
        distances = []
        for i in range(len(embeddings) - 1):
            if embeddings[i] is None or embeddings[i+1] is None:
                distances.append(0)
                continue
            
            v1 = np.array(embeddings[i])
            v2 = np.array(embeddings[i+1])
            
            # cosine sim
            sim = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)
            distances.append(sim)

        # Build chunks based on threshold
        chunks = []
        current_chunk_sentences = [sentences[0]]
        
        doc_id = str(uuid.uuid4())
        
        for i, dist in enumerate(distances):
            if dist > self.threshold:
                # High similarity, keep together
                current_chunk_sentences.append(sentences[i+1])
            else:
                # Low similarity, break chunk
                text = " ".join(current_chunk_sentences)
                chunks.append(Chunk(
                    id=str(uuid.uuid4()),
                    document_id=doc_id,
                    text=text,
                    metadata=DocumentMetadata(filename=filename, extra=metadata)
                ))
                current_chunk_sentences = [sentences[i+1]]
                
        # Last chunk
        if current_chunk_sentences:
            text = " ".join(current_chunk_sentences)
            chunks.append(Chunk(
                id=str(uuid.uuid4()),
                document_id=doc_id,
                text=text,
                metadata=DocumentMetadata(filename=filename, extra=metadata)
            ))
            
        return chunks

    async def process(self, content: str, filename: str, metadata: dict) -> List[Chunk]:
        return await self.process_async(content, filename, metadata)
