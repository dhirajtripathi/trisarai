import os
import json
from langchain_openai import AzureChatOpenAI, ChatOpenAI
# Try imports, handle missing libs gracefully
try:
    from langchain_community.chat_models import ChatBedrock
except ImportError:
    ChatBedrock = None

try:
    from langchain_google_vertexai import ChatVertexAI
except ImportError:
    try:
        from langchain_community.chat_models import ChatVertexAI
    except ImportError:
        ChatVertexAI = None

from langchain_core.prompts import PromptTemplate

def get_config():
    """
    Returns the current LLM configuration.
    """
    # Go up one level from 'api_transformation_agent' package
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config.json")
    
    if not os.path.exists(config_path):
        return {"llm_provider": "openai"}
        
    with open(config_path, "r") as f:
        config = json.load(f)
    return config

def get_llm(temperature=0):
    """
    Returns a configured LLM instance based on ../config.json
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config.json")
    
    config = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
            
    provider = config.get("llm_provider", "azure")
    
    print(f"🔌 [LLM Utils] Initializing Provider: {provider}")
    
    if provider == "azure":
        az_conf = config.get("azure_config", {})
        return AzureChatOpenAI(
            api_key=az_conf.get("api_key"),
            azure_endpoint=az_conf.get("endpoint"),
            deployment_name=az_conf.get("deployment_name", "gpt-4"),
            api_version=az_conf.get("api_version", "2023-05-15"),
            temperature=temperature
        )

    elif provider == "aws":
        if not ChatBedrock:
            raise ImportError("AWS Bedrock dependencies missing. Install langchain-aws or langchain-community.")
        aws_conf = config.get("aws_config", {})
        
        # Optional: Direct Credentials
        if aws_conf.get("access_key_id") and aws_conf.get("secret_access_key"):
            return ChatBedrock(
                region_name=aws_conf.get("region", "us-east-1"),
                model_id=aws_conf.get("model_id", "anthropic.claude-3-sonnet-20240229-v1:0"),
                aws_access_key_id=aws_conf.get("access_key_id"),
                aws_secret_access_key=aws_conf.get("secret_access_key"),
                model_kwargs={"temperature": temperature}
            )
            
        return ChatBedrock(
            credentials_profile_name=aws_conf.get("profile_name", "default"),
            region_name=aws_conf.get("region", "us-east-1"),
            model_id=aws_conf.get("model_id", "anthropic.claude-3-sonnet-20240229-v1:0"),
            model_kwargs={"temperature": temperature}
        )
        
    elif provider == "google":
        if not ChatVertexAI:
             raise ImportError("Google Vertex dependencies missing.")
        gcp_conf = config.get("google_config", {})
        return ChatVertexAI(
            project=gcp_conf.get("project_id"),
            location=gcp_conf.get("location", "us-central1"),
            model_name=gcp_conf.get("model_name", "gemini-pro"),
            temperature=temperature
        )

    # Fallback to standard OpenAI Env Vars
    print("   Using Standard OpenAI (Env)")
    return ChatOpenAI(
        model="gpt-4",
        temperature=temperature
    )

def load_prompt(platform: str, name: str) -> PromptTemplate:
    """
    Loads text content from api_transformation_agent/prompts/{platform}/{name}.txt
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(base_dir, "prompts", platform, f"{name}.txt")
    
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        
    with open(prompt_path, "r") as f:
        template = f.read()
        
    return PromptTemplate.from_template(template)
