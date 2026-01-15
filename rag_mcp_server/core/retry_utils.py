import asyncio
import logging
from functools import wraps
from ..config import get_settings

logger = logging.getLogger(__name__)

def with_retry(func):
    """
    Decorator to retry async functions with exponential backoff.
    Reads API_MAX_RETRIES from settings.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        settings = get_settings()
        max_retries = settings.API_MAX_RETRIES
        delay = 1.0
        
        for attempt in range(max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # In production, check for specific exceptions (e.g. RateLimitError, 503)
                if attempt == max_retries:
                    logger.error(f"Function {func.__name__} failed after {max_retries} retries. Error: {e}")
                    raise e
                
                logger.warning(f"Retrying {func.__name__} (attempt {attempt+1}/{max_retries}) due to: {e}")
                await asyncio.sleep(delay)
                delay *= 2 # Exponential backoff
                
    return wrapper
