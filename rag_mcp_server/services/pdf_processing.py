from typing import List
import pymupdf4llm
from ..core.interfaces import DocumentProcessor
from ..core.models import Chunk, DocumentMetadata
from ..services.text_processing import DefaultDocumentProcessor
import uuid
import os

class PDFProcessor(DocumentProcessor):
    def __init__(self):
        # We can reuse the default processor's logic for chunking the markdown output
        self.text_processor = DefaultDocumentProcessor()

    async def process(self, content: str, filename: str, metadata: dict) -> List[Chunk]:
        """
        Processes a PDF file path.
        'content' here is expected to be a file path for PDFs.
        """
        if not os.path.exists(content):
             raise FileNotFoundError(f"PDF file not found: {content}")

        # Convert PDF to Markdown (tables preserved)
        # pymupdf4llm.to_markdown returns a string
        md_text = pymupdf4llm.to_markdown(content)
        
        # Now process the markdown text using the standard text chunker
        # We tag it as 'extracted_markdown' in metadata
        metadata["original_format"] = "pdf"
        metadata["extracted_via"] = "pymupdf4llm"
        
        return await self.text_processor.process(md_text, filename, metadata)
