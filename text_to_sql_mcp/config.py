import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    _instance = None

    def __init__(self):
        self.LLM_MODEL = os.getenv("LLM_MODEL", "mock")
        self.DATABASE_URL = os.getenv("DATABASE_URL", "")
        # Store API keys in a dict for runtime updates
        self.api_keys = {}
        # Pre-load known keys from env
        for key in ["OPENAI_API_KEY", "AZURE_API_KEY", "AZURE_API_BASE", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION_NAME", "GEMINI_API_KEY", "VERTEX_PROJECT", "VERTEX_LOCATION"]:
             val = os.getenv(key)
             if val:
                 self.api_keys[key] = val

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def update(self, llm_model=None, database_url=None, api_keys=None):
        if llm_model: self.LLM_MODEL = llm_model
        if database_url is not None: self.DATABASE_URL = database_url
        if api_keys: self.api_keys.update(api_keys)
        
        # Important: Update os.environ for LiteLLM to pick up new keys
        if api_keys:
            for k, v in api_keys.items():
                os.environ[k] = v

    def is_real_llm(self):
        return self.LLM_MODEL.lower() != "mock"

    def is_real_db(self):
        return bool(self.DATABASE_URL)

settings = Settings.get_instance()
