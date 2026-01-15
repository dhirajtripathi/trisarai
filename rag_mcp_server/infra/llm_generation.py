from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional
from openai import AsyncOpenAI
import logging
from ..config import get_settings
from ..core.retry_utils import with_retry

logger = logging.getLogger(__name__)

class LLMGenerator(ABC):
    @abstractmethod
    async def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """Generate a complete text response."""
        pass

class OpenAICompatibleGenerator(LLMGenerator):
    def __init__(self, provider: str = "openai"):
        settings = get_settings()
        self.provider = provider
        
        if provider == "ollama":
            self.client = AsyncOpenAI(
                base_url=settings.OLLAMA_BASE_URL,
                api_key="ollama"
            )
            self.model = settings.LLM_MODEL
        else: # default openai
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.LLM_MODEL

    @with_retry
    async def generate_response(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM generation failed ({self.provider}): {e}")
            return f"Error generating response: {str(e)}"

def get_llm_generator() -> LLMGenerator:
    settings = get_settings()
    provider = settings.LLM_PROVIDER.lower()
    
    # We use the same class for OpenAI/Anthropic-via-wrapper/Ollama
    # as mostly they follow similar chat completion patterns or use openai-lib compatible endpoints (like Ollama)
    return OpenAICompatibleGenerator(provider=provider)
