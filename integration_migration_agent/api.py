from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, List
import uuid
import uvicorn
import io
import os
from .graph import app as graph_app
from .config import DB_PATH, PROMPTS_DIR

app = FastAPI()

class StartRequest(BaseModel):
    source_system: str
    target_system: str
    provider: str
    credentials: Dict[str, str]
    # Files handled via separate endpoint or multipart

# In-memory store for file content (simplified for PoC)
# In prod, upload to S3 or disk
file_storage = {} 

@app.post("/cases")
async def start_case(
    source_system: str = Form(...),
    target_system: str = Form(...),
    provider: str = Form(...),
    # Credentials passed as JSON string or individual fields - simplified here to generic dict via form parsing in real app 
    # For simplicity in this demo, we'll accept basic auth fields directly if easy, but JSON body is cleaner.
    # We will use a mixed approach: File upload + metadata
    files: List[UploadFile] = File(...)
):
    thread_id = str(uuid.uuid4())
    
    # Read files
    file_contents = {}
    for file in files:
        content = await file.read()
        file_contents[file.filename] = content.decode("utf-8") # Assuming text
        
    # Initialize State
    config = {"configurable": {"thread_id": thread_id}}
    
    # NOTE: Credentials would ideally come from secure storage or request. 
    # For this PoC, we default to Env Vars or assume the UI sends them in a secondary calls, 
    # OR we can assume headers. 
    # To keep it simple matching other agents: The UI form will send everything.
    # But since UploadFile forces multipart/form-data, json body is partial.
    # We will assume credentials are updated via a subsequent call or default envs if missing.
    
    # Simple workaround: The prompt asked for uploads.
    # We will start the thread with files.
    
    initial_state = {
        "source_files": file_contents,
        "source_system": source_system,
        "target_system": target_system,
        "provider": provider,
        "credentials": {} # Populated by UI in updates or headers
    }
    
    # Run until interrupt (after SRS Gen)
    graph_app.invoke(initial_state, config)
    
    return {"thread_id": thread_id, "status": "SRS_GENERATED"}

@app.post("/cases/{thread_id}/credentials")
async def update_credentials(thread_id: str, creds: Dict[str, str]):
    config = {"configurable": {"thread_id": thread_id}}
    state = graph_app.get_state(config).values
    if not state:
        raise HTTPException(status_code=404, detail="Case not found")
        
    # Update state with creds
    # We need to re-invoke or update state directly
    graph_app.update_state(config, {"credentials": creds})
    return {"status": "UPDATED"}

@app.get("/cases/{thread_id}")
async def get_case(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    state_snapshot = graph_app.get_state(config)
    if not state_snapshot.values:
        return {"status": "NOT_FOUND"}
    
    return {
        "next": state_snapshot.next,
        "values": state_snapshot.values
    }

@app.post("/cases/{thread_id}/approve")
async def approve_srs(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    
    # Resume graph (it stopped after reverse_engineer)
    # Just sending None to proceed provided no feedback loop logic requires input
    graph_app.invoke(None, config)
    
    return {"status": "PROCESSING_TARGET_CODE"}

# --- Prompt Management ---

class PromptUpdate(BaseModel):
    path: str
    content: str

@app.get("/prompts")
async def list_prompts():
    """Recursively list all prompt files"""
    prompts = []
    base_len = len(PROMPTS_DIR) + 1
    for root, _, files in os.walk(PROMPTS_DIR):
        for file in files:
            if file.endswith(".txt"):
                full_path = os.path.join(root, file)
                rel_path = full_path[base_len:]
                prompts.append(rel_path)
    return {"prompts": sorted(prompts)}

@app.post("/prompts/content")
async def get_prompt_content(path: str = Form(...)):
    """Get content of a specific prompt"""
    # Security check: ensure path is within PROMPTS_DIR
    target_path = os.path.abspath(os.path.join(PROMPTS_DIR, path))
    if not target_path.startswith(os.path.abspath(PROMPTS_DIR)):
        raise HTTPException(403, "Invalid path")
    
    if not os.path.exists(target_path):
        raise HTTPException(404, "Prompt not found")
        
    with open(target_path, "r") as f:
        return {"content": f.read()}

@app.post("/prompts/save")
async def save_prompt(update: PromptUpdate):
    """Update prompt content"""
    target_path = os.path.abspath(os.path.join(PROMPTS_DIR, update.path))
    if not target_path.startswith(os.path.abspath(PROMPTS_DIR)):
        raise HTTPException(403, "Invalid path")
        
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w") as f:
        f.write(update.content)
    
    return {"status": "SAVED"}

    return {"status": "SAVED"}

# --- Knowledge Base (VectorDB) ---

@app.get("/kb/{platform}")
async def list_kb_files(platform: str):
    """List files in the knowledge base for a platform"""
    kb_path = os.path.join("knowledge_base", platform)
    if not os.path.exists(kb_path):
         return {"files": []}
    
    files = [f for f in os.listdir(kb_path) if os.path.isfile(os.path.join(kb_path, f))]
    return {"files": sorted(files)}

@app.post("/kb/{platform}/upload")
async def upload_kb_file(platform: str, file: UploadFile = File(...)):
    """Upload a file to the knowledge base"""
    kb_path = os.path.join("knowledge_base", platform)
    os.makedirs(kb_path, exist_ok=True)
    
    file_path = os.path.join(kb_path, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    return {"status": "UPLOADED", "filename": file.filename}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
