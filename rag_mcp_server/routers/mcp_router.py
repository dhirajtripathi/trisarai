from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from fastapi.responses import JSONResponse
import os
import shutil
from ..services.rag_service import get_rag_service
from ..core.models import Resource, Tool, Prompt, JsonRpcRequest, JsonRpcResponse
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# --- MCP Metadata ---

@router.get("/resources/list")
async def list_resources():
    return [
        Resource(uri="rag://search?q={query}", name="Search RAG Knowledge Base", description="Search the vector database for relevant documentation"),
        Resource(uri="rag://documents/{id}", name="Get Document", description="Retrieve a full document by ID")
    ]

@router.get("/tools/list")
async def list_tools():
    return [
        Tool(
            name="ingest_document",
            description="Ingest a text document into the RAG system",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The text content of the document"},
                    "filename": {"type": "string", "description": "Filename for metadata"},
                    "metadata": {"type": "object", "description": "Optional metadata key-value pairs"}
                },
                "required": ["content", "filename"]
            }
        ),
        Tool(
            name="ingest_file",
            description="Ingest a local file (PDF or Text) into the RAG system",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Absolute path to the file"},
                    "metadata": {"type": "object", "description": "Optional metadata"}
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="ask_question",
            description="Ask a question to the RAG system and get a generated answer based on documents",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The question to ask"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="delete_document",
            description="Delete a document from the RAG system",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "ID of the document to delete"}
                },
                "required": ["document_id"]
            }
        )
    ]

@router.get("/prompts/list")
async def list_prompts():
    return [
        Prompt(
            name="rag-summarize",
            description="Summarize context retrieved from RAG",
            arguments=[
                {"name": "query", "description": "Topic to summarize"}
            ]
        )
    ]

# --- Resource handling ---

@router.get("/resources/read")
async def read_resource(uri: str):
    service = get_rag_service()
    
    # Handle Search Resource
    if uri.startswith("rag://search"):
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(uri)
        qs = parse_qs(parsed.query)
        query = qs.get('q', [''])[0]
        limit = int(qs.get('limit', ['5'])[0])
        
        if not query:
            raise HTTPException(status_code=400, detail="Missing query parameter 'q'")
            
        results = await service.search(query, limit)
        
        # Serialize results to text for the resource content
        content = json.dumps([r.model_dump() for r in results], indent=2)
        return {
            "contents": [{
                "uri": uri,
                "mimeType": "application/json",
                "text": content
            }]
        }

    # Handle Document Resource
    if uri.startswith("rag://documents/"):
        doc_id = uri.split("/")[-1]
        doc = await service.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
            
        return {
            "contents": [{
                "uri": uri,
                "mimeType": "text/plain",
                "text": doc.content
            }]
        }
        
    raise HTTPException(status_code=404, detail="Resource not found")

    raise HTTPException(status_code=404, detail="Resource not found")

# --- UI Helper endpoints ---

@router.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Helper endpoint to save uploaded files to disk so they can be ingested by path.
    """
    try:
        # Save to ./data/uploads
        upload_dir = os.path.join(os.getcwd(), "data", "uploads")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            
        file_path = os.path.join(upload_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {"file_path": file_path, "filename": file.filename}
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# --- Tool handling ---

@router.post("/tools/call")
async def call_tool(request: Request):
    data = await request.json()
    # Basic JSON-RPC validation (simplified for FastAPI convenience)
    method = data.get("name") # MCP uses 'name' in body for HTTP POST usually, or params in JSON-RPC
    arguments = data.get("arguments", {})
    
    service = get_rag_service()
    
    if method == "ingest_document":
        try:
            result = await service.ingest_document(
                content=arguments.get("content"),
                filename=arguments.get("filename"),
                metadata=arguments.get("metadata", {})
            )
            return {"content": [{"type": "text", "text": json.dumps(result)}]}
        except Exception as e:
            logger.error(f"Ingest error: {e}")
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    elif method == "ingest_file":
        try:
            result = await service.ingest_file(
                file_path=arguments.get("file_path"),
                metadata=arguments.get("metadata", {})
            )
            return {"content": [{"type": "text", "text": json.dumps(result)}]}
        except Exception as e:
            logger.error(f"Ingest file error: {e}")
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    elif method == "ask_question":
        try:
            answer = await service.ask_question(arguments.get("query"))
            return {"content": [{"type": "text", "text": answer}]}
        except Exception as e:
            logger.error(f"Ask question error: {e}")
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    elif method == "delete_document":
        try:
            await service.delete_document(arguments.get("document_id"))
            return {"content": [{"type": "text", "text": "Document deleted"}]}
        except Exception as e:
             return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    raise HTTPException(status_code=404, detail="Tool not found")

# --- JSON-RPC (Optional Full Compliance Endpoint) ---
# For true MCP compliance over stdio or SSE, we usually have a dedicated handler.
# This HTTP /tools/call is a simplified HTTP-based MCP pattern often used in POCs.
