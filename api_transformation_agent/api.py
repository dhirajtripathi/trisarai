from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
from typing import Optional
import uvicorn
import tempfile
import zipfile

# Agent Imports
from api_transformation_agent.graph import graph, TransformationState

# Imports
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import shutil
import tempfile
import zipfile
from api_transformation_agent.llm_utils import get_config

app = FastAPI(title="API Transformation Agent", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TransformResponse(BaseModel):
    status: str
    target: str
    config_content: str
    metadata: dict

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/transform", response_model=TransformResponse)
async def transform(
    file: UploadFile = File(...),
    source_type: str = Form("apigee"),
    target_type: str = Form("kong")
):
    """
    Agentic Transformation using LangGraph.
    """
    print(f"🚀 [API] Agentic Transform Request: {source_type} -> {target_type}")
    
    # Load Config (for LLM init in graph)
    config = get_config() # reused from existing function or logic

    # Create temp directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save uploaded file
        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        source_path = file_path
        
        # Handle Zip extraction (legacy logic preserved)
        if source_type == "apigee" and file.filename.endswith(".zip"):
            extract_dir = os.path.join(temp_dir, "extracted")
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            source_path = extract_dir
            for root, dirs, files in os.walk(extract_dir):
                if "apiproxy" in dirs:
                    source_path = root
                    break

        # --- Invoke Agentic Graph ---
        initial_state: TransformationState = {
            "source_type": source_type,
            "target_type": target_type,
            "source_path": source_path,
            "config": config,
            "uam": None,
            "critique": None,
            "generated_config": None,
            "error": None
        }
        
        thread_id = "request-" + file.filename # Simple thread ID
        run_config = {"configurable": {"thread_id": thread_id}}
        
        # Execute Graph
        final_state = graph.invoke(initial_state, run_config)
        
        if final_state.get("error"):
             raise HTTPException(status_code=500, detail=f"Agent Error: {final_state['error']}")

        return TransformResponse(
            status="SUCCESS",
            target=target_type,
            config_content=final_state["generated_config"] or "",
            metadata=final_state["uam"].metadata if final_state["uam"] else {}
        )

@app.get("/prompts")
def list_prompts():
    """
    Lists all available prompts categorized by platform.
    Used for Dynamic UI Dropdowns.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompts_dir = os.path.join(base_dir, "prompts")
    
    result = {}
    if os.path.exists(prompts_dir):
        for platform in os.listdir(prompts_dir):
            plat_path = os.path.join(prompts_dir, platform)
            if os.path.isdir(plat_path) and not platform.startswith("__"):
                files = [f for f in os.listdir(plat_path) if f.endswith(".txt")]
                result[platform] = files
    return result

@app.post("/platforms/{name}")
def create_platform(name: str):
    """
    Creates a new platform profile (folder + default prompts).
    """
    # Security check
    if ".." in name or "/" in name or "\\" in name:
        raise HTTPException(status_code=400, detail="Invalid platform name")
        
    base_dir = os.path.dirname(os.path.abspath(__file__))
    plat_path = os.path.join(base_dir, "prompts", name)
    
    if os.path.exists(plat_path):
        raise HTTPException(status_code=400, detail="Platform already exists")
        
    os.makedirs(plat_path)
    
    # Create default empty prompts
    with open(os.path.join(plat_path, "parser.txt"), "w") as f:
        f.write("# Parser Prompt for " + name + "\n# Instructions...\n")
        
    with open(os.path.join(plat_path, "generator.txt"), "w") as f:
        f.write("# Generator Prompt for " + name + "\n# Instructions...\n")
        
    return {"status": "created", "platform": name}

@app.get("/prompts/{platform}/{name}")
def get_prompt_content(platform: str, name: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(base_dir, "prompts", platform, name)
    if not os.path.exists(prompt_path):
        raise HTTPException(status_code=404, detail="Prompt not found")
    with open(prompt_path, "r") as f:
        return {"content": f.read()}

class PromptUpdate(BaseModel):
    content: str

@app.post("/prompts/{platform}/{name}")
def update_prompt_content(platform: str, name: str, req: PromptUpdate):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(base_dir, "prompts", platform, name)
    if ".." in platform or ".." in name:
        raise HTTPException(status_code=400, detail="Invalid path")
    os.makedirs(os.path.dirname(prompt_path), exist_ok=True)
    with open(prompt_path, "w") as f:
        f.write(req.content)
    return {"status": "updated"}

    with open(prompt_path, "w") as f:
        f.write(req.content)
    return {"status": "updated"}

# --- Config Management ---

# --- Config Management ---

@app.get("/config")
def get_config_route():
    """
    Returns the current LLM configuration.
    """
    return get_config()

@app.post("/config")
def update_config(config: dict):
    """
    Updates the LLM configuration.
    """
    config_path = "config.json"
    
    # Merge with existing to avoid losing other keys
    current_conf = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            current_conf = json.load(f)
            
    current_conf.update(config)
    
    with open(config_path, "w") as f:
        json.dump(current_conf, f, indent=2)
        
    return {"status": "updated"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8007)
