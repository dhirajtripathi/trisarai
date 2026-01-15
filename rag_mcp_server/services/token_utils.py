import tiktoken
from typing import List
from ..config import get_settings

def truncate_context(texts: List[str], max_tokens: int, model: str = "gpt-4") -> List[str]:
    """
    Truncates a list of text strings so that their combined token count 
    does not exceed max_tokens. Preserves the order (assuming ranked by relevance).
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
        
    current_tokens = 0
    selected_texts = []
    
    for text in texts:
        tokens = len(encoding.encode(text))
        if current_tokens + tokens > max_tokens:
            # We could try to partially take this chunk, but for RAG it's often safer to drop
            # or we could attempt to split. For simplicity, we stop here.
            break
            
        selected_texts.append(text)
        current_tokens += tokens
        
    return selected_texts
