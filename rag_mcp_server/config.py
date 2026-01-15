import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "RAG MCP Server"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Vector Components
    VECTOR_STORE_TYPE: str = "memory"  # memory, chroma, qdrant, postgres
    EMBEDDING_PROVIDER: str = "openai"  # openai, local_mock
    
    # Vector DB Settings
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    POSTGRES_URL: str = "postgresql://user:password@localhost:5432/vectordb"
    
    # Text Processing
    CHUNKING_STRATEGY: str = "recursive" # recursive, semantic, sliding
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    SEMANTIC_CHUNK_THRESHOLD: float = 0.8 # Similarity threshold for semantic splitting
    
    # Embedding Configuration
    EMBEDDING_PROVIDER: str = "openai" # openai, ollama, local_mock, sentence_transformer
    EMBEDDING_MODEL: str = "text-embedding-3-small" # or 'all-MiniLM-L6-v2' for sentence_transformer
    
    # LLM Configuration
    LLM_PROVIDER: str = "openai" # openai, ollama
    LLM_MODEL: str = "gpt-4-turbo-preview"
    
    # Robustness & Edge Cases
    MIN_SCORE_THRESHOLD: float = 0.5 # Minimum similarity score to consider a chunk relevant
    MAX_CONTEXT_TOKENS: int = 4000 # Safety limit for context injection
    API_MAX_RETRIES: int = 3
    
    # API Keys & Endpoints
    OPENAI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1" # Standard wrapper API url
    
    
    # Vector DB Configs
    VECTOR_STORE_TYPE: str = "memory" # memory, chroma, qdrant, postgres, faiss
    
    # Storage Paths
    STORAGE_DIR: str = "./data"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
