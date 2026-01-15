from typing import Dict, Optional, List
from ..core.interfaces import Embedder, VectorStore, Document
from ..core.models import SearchResult
from ..services.text_processing import DefaultDocumentProcessor
from ..services.pdf_processing import PDFProcessor
from ..services.processor_factory import get_document_processor
from ..services.token_utils import truncate_context
from ..infra.llm_client import get_embedder
from ..infra.llm_generation import get_llm_generator, LLMGenerator
# from ..infra.vector_store import _vector_store_instance  <-- Removed this invalid import
from ..config import get_settings

# Global
_vector_store_instance = None
_embedder_instance = None
_llm_instance = None
_text_processor = None
_pdf_processor = PDFProcessor() 

def get_rag_service():
    global _embedder_instance, _vector_store_instance, _text_processor, _llm_instance
    
    if _embedder_instance is None:
        _embedder_instance = get_embedder()
        
    if _llm_instance is None:
        _llm_instance = get_llm_generator()
        
    if _vector_store_instance is None:
        from ..infra.factory import get_vector_store
        _vector_store_instance = get_vector_store()
        
    if _text_processor is None:
        # Pass embedder to factory for semantic chunking support
        _text_processor = get_document_processor(_embedder_instance)
        # Also need to make sure PDF processor uses the configured text strategy?
        # Typically PDF extracts text then chunks it. 
        # Our PDFProcessor currently hardcodes DefaultDocumentProcessor.
        # Let's inject the dynamic one into PDFProcessor if possible or rely on RAGService to pass it
        _pdf_processor.text_processor = _text_processor # HACK: Direct injection to reusing simple wrapper

    return RAGService(
        text_processor=_text_processor,
        pdf_processor=_pdf_processor,
        embedder=_embedder_instance,
        vector_store=_vector_store_instance,
        llm=_llm_instance
    )

class RAGService:
    def __init__(self, text_processor: DefaultDocumentProcessor, pdf_processor: PDFProcessor, embedder: Embedder, vector_store: VectorStore, llm: LLMGenerator):
        self.text_processor = text_processor
        self.pdf_processor = pdf_processor
        self.embedder = embedder
        self.vector_store = vector_store
        self.llm = llm

    async def ingest_file(self, file_path: str, metadata: dict = {}) -> Dict[str, str]:
        if not os.path.exists(file_path):
             return {"status": "error", "message": f"File not found: {file_path}"}
             
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == ".pdf":
            chunks = await self.pdf_processor.process(file_path, filename, metadata)
        else:
            # Assume text based
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                chunks = await self.text_processor.process(content, filename, metadata)
            except Exception as e:
                return {"status": "error", "message": f"Failed to read text file: {e}"}

        if not chunks:
            return {"status": "error", "message": "No content to process"}

        # 2. Embedding
        texts = [c.text for c in chunks]
        embeddings = await self.embedder.embed_documents(texts)
        
        for i, chunk in enumerate(chunks):
            chunk.embedding = embeddings[i]

        # 3. Storage
        await self.vector_store.add_chunks(chunks)
        
        return {
            "status": "success",
            "document_id": chunks[0].document_id,
            "chunks_count": str(len(chunks)),
            "filename": filename
        }

    async def ingest_document(self, content: str, filename: str, metadata: dict = {}) -> Dict[str, str]:
        # Legacy method for direct text string
        chunks = await self.text_processor.process(content, filename, metadata)
        if not chunks:
            return {"status": "error", "message": "No content to process"}

        # 2. Embedding
        texts = [c.text for c in chunks]
        embeddings = await self.embedder.embed_documents(texts)
        
        for i, chunk in enumerate(chunks):
            chunk.embedding = embeddings[i]

        # 3. Storage
        await self.vector_store.add_chunks(chunks)
        
        return {
            "status": "success",
            "document_id": chunks[0].document_id,
            "chunks_count": str(len(chunks))
        }

    async def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        query_embedding = await self.embedder.embed_query(query)
        results = await self.vector_store.search(query_embedding, limit=limit)
        
        # Score Thresholding
        settings = get_settings()
        filtered_results = [
            r for r in results 
            if r.score >= settings.MIN_SCORE_THRESHOLD
        ]
        return filtered_results

    async def delete_document(self, document_id: str):
        await self.vector_store.delete_document(document_id)
        
    async def get_document(self, document_id: str) -> Optional[Document]:
        return await self.vector_store.get_document(document_id)

    async def ask_question(self, query: str) -> str:
        # 1. Search for relevant context
        results = await self.search(query, limit=10)
        
        if not results:
             return "I couldn't find any relevant information in the documents to answer your question."
        
        # 2. Context Construction & Truncation
        settings = get_settings()
        
        # Extract text snippets
        snippets = [f"Source ({r.metadata.get('filename')}): {r.text}" for r in results]
        
        # Truncate to fit context window
        valid_snippets = truncate_context(
            snippets, 
            max_tokens=settings.MAX_CONTEXT_TOKENS,
            model=settings.LLM_MODEL
        )
        
        if not valid_snippets:
             return "I found some documents, but they are too large to process."

        context_str = "\n\n".join(valid_snippets)
            
        system_prompt = "You are a helpful RAG assistant. Answer the question based ONLY on the provided context. If the answer is not in the context, say so."
        user_prompt = f"Context:\n{context_str}\n\nQuestion: {query}"
        
        # 3. Generate Answer
        return await self.llm.generate_response(user_prompt, system_prompt)
