import uuid
from typing import List
from ..core.interfaces import DocumentProcessor
from ..core.models import Chunk, DocumentMetadata
from ..config import get_settings

class DefaultDocumentProcessor(DocumentProcessor):
    def __init__(self):
        self.settings = get_settings()

    async def process(self, content: str, filename: str, metadata: dict) -> List[Chunk]:
        """
        Splits text into chunks using a simple overlap strategy.
        In production, this would use tiktoken for token-based splitting.
        """
        chunk_size = self.settings.CHUNK_SIZE
        overlap = self.settings.CHUNK_OVERLAP
        
        chunks = []
        doc_id = str(uuid.uuid4())
        
        # Simple character-based splitting for now (robust enough for POC)
        # TODO: Upgrade to tiktoken based splitter
        start = 0
        text_len = len(content)
        
        while start < text_len:
            end = start + chunk_size
            chunk_text = content[start:end]
            
            # Adjust end to nearest space to avoid breaking words if possible
            if end < text_len:
                last_space = chunk_text.rfind(' ')
                if last_space != -1 and len(chunk_text) - last_space < 50:
                    end = start + last_space + 1
                    chunk_text = content[start:end]
            
            chunk_id = str(uuid.uuid4())
            chunks.append(Chunk(
                id=chunk_id,
                document_id=doc_id,
                text=chunk_text,
                metadata=DocumentMetadata(
                    filename=filename,
                    extra=metadata
                )
            ))
            
            start = end - overlap
            if start < 0: # Should not happen but safety check
                start = end
        
        return chunks
