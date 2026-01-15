# RAG Knowledge Base Server
**Usecase Name**: `rag_mcp_server`

## 1. Functional Overview
The **RAG (Retrieval-Augmented Generation) Knowledge Base** is an MCP-compliant server designed to answer questions based on private, unstructured enterprise data (PDFs, Docs, txt). It turns static documents into an interactive knowledge agent.

### Key Features
*   **Document Ingestion**: Uploads and chunks documents for vector search.
*   **Semantic Search**: Retrieves context using Cosine Similarity on embeddings.
*   **Evidence-Based Answers**: LLM answers *only* using retrieved context, creating a "Hallucination Firewall".
*   **Audit Logging**: Tracks every query and document access for compliance.

## 2. Technical Architecture (MCP & RAG)
This agent adheres to the **Model Context Protocol (MCP)** to expose "Knowledge" as a specialized toolset.

### Core Components
1.  **Vector Store Abstraction**:
    *   Supports pluggable backends: `ChromaDB`, `Qdrant`, `PGVector`, or In-Memory (FAISS/numpy).
2.  **Embedding Service**:
    *   Generates vectors using `OpenAI text-embedding-3` or local `SentenceTransformers`.
3.  **RAG Pipeline**:
    *   **Retrieve**: Fetch Top-K chunks ($k=5$).
    *   **Rerank** (Optional): Refine results for relevance.
    *   **Generate**: Synthesize answer with LLM.
4.  **MCP Tools**:
    *   `ingest_document(file)`: add knowledge.
    *   `ask_question(query)`: retrieve & answer.

## 3. Implementation Steps

### Backend Setup
1.  **Navigate**: `cd rag_mcp_server`
2.  **Install**: `pip install -r requirements.txt` (fastapi, chromadb, openai, tiktoken)
3.  **Configure**:
    ```ini
    VECTOR_STORE=chroma
    CHROMA_DB_PATH=./data
    OPENAI_API_KEY=sk-...
    ```
4.  **Run**: `python main.py`

### Testing via MCP
Send a request to the server:
```json
// Tool Call
{
  "name": "ask_question",
  "arguments": { "query": "What is the policy on remote work?" }
}
```

## 4. Context Engineering
The quality of RAG depends on **Chunking Strategy**:
*   **Recursive Character Split**: We don't just split by length; we respect paragraph/sentence boundaries to keep semantic meaning intact.
*   **Metadata Injection**: We inject file headers (Filename, Author, Date) into the chunk text so the LLM understands the source context.
*   **System Prompt**:
    > "You are a helpful assistant. Answer the user's question using ONLY the content provided below in the <context> block. If the answer is not there, say 'I do not know'."
