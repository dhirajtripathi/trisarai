import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from config import Config

# Dummy Regulatory Data
REGULATIONS = [
    {
        "source": "EU AI Act",
        "text": "Article 5: Prohibited AI Practices. The following AI practices shall be prohibited: (a) the placing on the market, putting into service or use of an AI system that deploys subliminal techniques beyond a person consciousness in order to materially distort a person behaviour in a manner that causes or is likely to cause that person or another person physical or psychological harm."
    },
    {
        "source": "EU AI Act",
        "text": "Article 13: Transparency and provision of information to users. High-risk AI systems shall be designed and developed in such a way to ensure that their operation is sufficiently transparent to enable users to interpret the system output and use it appropriately."
    },
    {
        "source": "Insurance Distribution Directive (IDD)",
        "text": "Article 17: General principle. Member States shall ensure that, when carrying out insurance distribution, insurance distributors always act honestly, fairly and professionally in accordance with the best interests of their customers."
    },
    {
        "source": "Local Insurance Law 42",
        "text": "Section 8: Denial of Claims. Any denial of an insurance claim must be accompanied by a specific reason referencing the policy clause. Vague denials such as 'policy conditions not met' are strictly prohibited."
    },
    {
        "source": "Fair AI Claim Processing Regulation",
        "text": "Rule 10: Automated Decision Making. When a claim is denied primarily by an automated decision system, the claimant has the right to request a human review. The denial letter must explicitly state this right."
    }
]

def get_embeddings():
    # Using specific model as requested (all-MiniLM-L6-v2 is the default for sentence-transformers)
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def load_or_create_vector_db():
    embeddings = get_embeddings()
    if os.path.exists(Config.FAISS_INDEX_PATH):
        try:
            vector_db = FAISS.load_local(Config.FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
            return vector_db
        except Exception as e:
            print(f"Error loading existing DB: {e}. Creating new one.")
    
    # Create new if not exists or failed to load
    docs = [Document(page_content=reg["text"], metadata={"source": reg["source"]}) for reg in REGULATIONS]
    vector_db = FAISS.from_documents(docs, embeddings)
    vector_db.save_local(Config.FAISS_INDEX_PATH)
    return vector_db

def add_regulation(text, source):
    embeddings = get_embeddings()
    vector_db = load_or_create_vector_db()
    
    new_doc = Document(page_content=text, metadata={"source": source})
    vector_db.add_documents([new_doc])
    vector_db.save_local(Config.FAISS_INDEX_PATH)
    return True

def get_retriever():
    db = load_or_create_vector_db()
    return db.as_retriever(search_kwargs={"k": 2})

if __name__ == "__main__":
    print("Building/Refreshing Vector DB...")
    db = load_or_create_vector_db()
    print("Vector DB ready.")
