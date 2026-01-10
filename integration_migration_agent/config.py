import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
DB_PATH = os.path.join(BASE_DIR, "state.db")

# Default Models
AZURE_OPENAI_API_VERSION = "2023-05-15"
AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-4"

# RAG Configuration
VECTOR_STORE_PATH = os.path.join(BASE_DIR, "vector_store")
