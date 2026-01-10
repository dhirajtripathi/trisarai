from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_aws import BedrockEmbeddings
import os

class RAGEngine:
    def __init__(self, provider="Azure OpenAI", creds=None):
        self.vector_store = None
        self.provider = provider
        self.creds = creds or {}
        
    def _get_embeddings(self):
        if self.provider == "Azure OpenAI":
             return AzureOpenAIEmbeddings(
                api_key=self.creds.get("azure_key"),
                azure_endpoint=self.creds.get("azure_endpoint"),
                azure_deployment="text-embedding-ada-002", # Typical default
                api_version="2023-05-15"
            )
        elif self.provider == "Google Gemini":
            return GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=self.creds.get("google_key")
            )
        # Fallbacks or AWS implementation would go here
        return None

    def ingest_files(self, file_contents: dict, platform: str = None):
        """
        Ingest dictionary of filename -> content.
        Also loads files from knowledge_base/{platform} if provided.
        """
        docs = []
        # 1. Case Files
        for fname, content in file_contents.items():
            docs.append(Document(page_content=content, metadata={"source": fname, "type": "case_file"}))
            
        # 2. Knowledge Base Files
        if platform:
            kb_path = os.path.join("knowledge_base", platform)
            if os.path.exists(kb_path):
                for fname in os.listdir(kb_path):
                    fpath = os.path.join(kb_path, fname)
                    if os.path.isfile(fpath):
                        try:
                            with open(fpath, "r", encoding="utf-8") as f:
                                content = f.read()
                                docs.append(Document(page_content=content, metadata={"source": fname, "type": "kb_file"}))
                        except Exception as e:
                            print(f"Skipping KB file {fname}: {e}")

        embeddings = self._get_embeddings()
        if embeddings and docs:
            try:
                self.vector_store = FAISS.from_documents(docs, embeddings)
                print(f"RAG Index built with {len(docs)} documents.")
            except Exception as e:
                print(f"Embedding failed (likely creds): {e}")
                self.vector_store = None
        else:
             # Fallback: No embeddings (just raw context)
             print("No embedding provider valid or no docs, RAG disabled.")

    def retrieve_context(self, query: str, k=3) -> str:
        if not self.vector_store:
            return ""
        
        docs = self.vector_store.similarity_search(query, k=k)
        return "\n\n".join([d.page_content for d in docs])
