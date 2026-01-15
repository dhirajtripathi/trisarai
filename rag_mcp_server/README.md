# RAG MCP Server

A production-grade Model Context Protocol (MCP) server that provides Retrieval-Augmented Generation (RAG) capabilities to agentic clients.

## Features

- **Document Ingestion**: Supports text ingestion with configurable chunking (sliding window).
- **Vector Storage**: Pluggable storage backend (currently In-Memory + Numpy for portability).
- **Sematic Search**: Cosine similarity search with metadata filtering.
- **MCP Protocol**:
  - `rag://search` (Resource): Search the knowledge base.
  - `rag://documents/{id}` (Resource): Retrieve full documents.
  - `ingest_document` (Tool): Add new content.
  - `delete_document` (Tool): Remove content.
- **Enterprise Ready**: Structured for RBAC, Audit Logging, and Tenant Isolation.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration**:
   Copy `.env.example` (if provided) or set env vars.
   - `OPENAI_API_KEY`: Required if using OpenAI embeddings (default).
   - `EMBEDDING_PROVIDER`: Set to `local_mock` for testing without OpenAI.

3. **Run Server**:
   ```bash
   uvicorn rag_mcp_server.main:app --host 0.0.0.0 --port 8000
   ```

## API Usage (MCP)

### Tools
**`ingest_document`**
```json
{
  "name": "ingest_document",
  "arguments": {
    "filename": "guide.txt",
    "content": "MCP is great...",
    "metadata": {"category": "tech"}
  }
}
```

### Resources
**Search**
`GET rag://search?q=MCP&limit=5`

**Get Document**
`GET rag://documents/{uuid}`

## Architecture
- **Core**: Interfaces and Domain Models
- **Services**: RAG orchestration
- **Infra**: Vector Store and Embedder implementations
- **Routers**: FastAPI routes mapping to MCP protocol

## Testing
Run the client simulation:
```bash
python rag_mcp_server/client_test.py
```
