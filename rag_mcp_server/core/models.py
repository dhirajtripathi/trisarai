from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
import time

# --- Domain Models (RAG) ---

class DocumentMetadata(BaseModel):
    filename: str
    content_type: str = "text/plain"
    author: Optional[str] = None
    created_at: float = Field(default_factory=time.time)
    extra: Dict[str, Any] = Field(default_factory=dict)

class Document(BaseModel):
    id: str
    content: str
    metadata: DocumentMetadata

class Chunk(BaseModel):
    id: str
    document_id: str
    text: str
    embedding: Optional[List[float]] = None
    metadata: DocumentMetadata

class SearchResult(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    score: float
    metadata: Dict[str, Any]

# --- MCP Protocol Models ---

class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[int] = None

class JsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[int] = None

class Resource(BaseModel):
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None

class Tool(BaseModel):
    name: str
    description: Optional[str] = None
    inputSchema: Dict[str, Any]

class Prompt(BaseModel):
    name: str
    description: Optional[str] = None
    arguments: Optional[List[Dict[str, Any]]] = None
