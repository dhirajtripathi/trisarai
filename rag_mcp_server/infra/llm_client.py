from typing import List
import os
from openai import AsyncOpenAI
from ..core.interfaces import Embedder
from ..config import get_settings
from ..core.retry_utils import with_retry
import numpy as np

class OpenAIEmbedder(Embedder):
    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.EMBEDDING_MODEL

    @with_retry
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        response = await self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        return [data.embedding for data in response.data]

    @with_retry
    async def embed_query(self, text: str) -> List[float]:
        response = await self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding

class OllamaEmbedder(Embedder):
    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(
            base_url=settings.OLLAMA_BASE_URL,
            api_key="ollama" 
        )
        self.model = settings.EMBEDDING_MODEL

    @with_retry
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            response = await self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            print(f"Ollama embedding error: {e}")
            return [[] for _ in texts]

    @with_retry
    async def embed_query(self, text: str) -> List[float]:
        try:
            response = await self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Ollama embedding error: {e}")
            return []

class SentenceTransformerEmbedder(Embedder):
    def __init__(self):
        settings = get_settings()
        try:
            from sentence_transformers import SentenceTransformer
            # 'all-MiniLM-L6-v2' is a good default
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL or "all-MiniLM-L6-v2")
        except ImportError:
            raise ImportError("sentence-transformers not installed. Please pip install sentence-transformers")

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Run in executor to avoid blocking event loop (model inference is CPU intensive)
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(None, self.model.encode, texts)
        return embeddings.tolist()

    async def embed_query(self, text: str) -> List[float]:
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(None, self.model.encode, text)
        return embedding.tolist()

class MockEmbedder(Embedder):
    """Generates random embeddings for testing without API keys."""
    def __init__(self, dim: int = 1536):
        self.dim = dim
        import random
        self.rng = random.Random(42)

    async def embed_query(self, text: str) -> List[float]:
        return [self.rng.random() for _ in range(self.dim)]

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [[self.rng.random() for _ in range(self.dim)] for _ in texts]

def get_embedder() -> Embedder:
    settings = get_settings()
    provider = settings.EMBEDDING_PROVIDER.lower()
    
    if provider == "openai":
        return OpenAIEmbedder()
    elif provider == "ollama":
        return OllamaEmbedder()
    elif provider == "sentence_transformer":
        return SentenceTransformerEmbedder()
    else:
        return MockEmbedder()
