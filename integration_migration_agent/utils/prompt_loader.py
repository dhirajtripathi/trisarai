import os
from ..config import PROMPTS_DIR

def load_prompt(stage: str, system_name: str, direction: str = "source") -> str:
    """
    Load a prompt template from the file system.
    
    Args:
        stage (str): 'srs_generation', 'architecture', or 'code_generation'
        system_name (str): e.g., 'webmethods', 'springboot', 'tibco'
        direction (str): 'source' or 'target'
    """
    path = os.path.join(PROMPTS_DIR, direction, system_name, f"{stage}.txt")
    
    if not os.path.exists(path):
        # Fallback to a generic prompt if specific one doesn't exist
        return f"Please perform {stage} for a {system_name} system."
        
    with open(path, "r") as f:
        return f.read()
