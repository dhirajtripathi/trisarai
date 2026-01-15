@app.get("/prompts")
def list_prompts():
    """
    Lists all available prompts categorized by platform.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompts_dir = os.path.join(base_dir, "prompts")
    
    result = {}
    if os.path.exists(prompts_dir):
        for platform in os.listdir(prompts_dir):
            plat_path = os.path.join(prompts_dir, platform)
            if os.path.isdir(plat_path):
                files = [f for f in os.listdir(plat_path) if f.endswith(".txt")]
                result[platform] = files
    return result

@app.get("/prompts/{platform}/{name}")
def get_prompt_content(platform: str, name: str):
    """
    Reads the content of a specific prompt.
    """
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
    """
    Updates the content of a specific prompt.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(base_dir, "prompts", platform, name)
    
    # Security check: prevent traversal
    if ".." in platform or ".." in name:
        raise HTTPException(status_code=400, detail="Invalid path")
        
    # Ensure dir exists (though it should if we are updating)
    os.makedirs(os.path.dirname(prompt_path), exist_ok=True)
    
    with open(prompt_path, "w") as f:
        f.write(req.content)
        
    return {"status": "updated"}
