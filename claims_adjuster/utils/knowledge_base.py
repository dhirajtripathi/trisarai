from langchain_community.document_loaders import TextLoader
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
from config import Config
import os

# Initialize Embeddings
# embeddings = AzureOpenAIEmbeddings(...) # DEFERS INIT

def get_embeddings():
    api_key = os.getenv("AZURE_OPENAI_API_KEY") or Config.AZURE_OPENAI_API_KEY
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") or Config.AZURE_OPENAI_ENDPOINT
    
    if not api_key or not endpoint:
        # Fallback for when keys aren't set yet (app startup)
        # using a dummy wrapper or raising a clearer error later
        return None 

    return AzureOpenAIEmbeddings(
        azure_endpoint=endpoint,
        api_key=api_key,
        azure_deployment=Config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        openai_api_version=Config.AZURE_OPENAI_API_VERSION
    )

def build_vector_store():
    """
    Ingests the policies.md file and builds a local FAISS index.
    """
    embeddings = get_embeddings()
    if not embeddings:
        return None
        
    file_path = os.path.join(os.path.dirname(__file__), "../data/policies.md")
    # ...
    
    loader = TextLoader(file_path)
    documents = loader.load()
    
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)
    
    db = FAISS.from_documents(docs, embeddings)
    return db

# Cache the database in memory for this PoC
_vector_db = None

def get_policy_context(query: str) -> str:
    """
    Retrieves relevant policy sections based on the claim description.
    """
    global _vector_db
    if _vector_db is None:
        _vector_db = build_vector_store()
    
    if _vector_db is None:
        return "POLICY CONTEXT UNAVAILABLE: Azure OpenAI Credentials missing for Embeddings."

    docs = _vector_db.similarity_search(query, k=2)
    return "\n\n".join([d.page_content for d in docs])
