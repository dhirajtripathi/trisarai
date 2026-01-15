import json
from ..uam_schema import UAMEnvelope
from ..llm_utils import get_llm, load_prompt
from langchain_core.messages import HumanMessage

class GenericLLMParser:
    def __init__(self, platform: str):
        self.platform = platform

    def parse(self, config_path: str) -> UAMEnvelope:
        print(f"🤖 [Generic AI Parser] Analyzing {self.platform} Config: {config_path}")
        
        # 1. Read Content (Assume single file text)
        try:
            with open(config_path, "r") as f:
                source_code = f.read()
        except UnicodeDecodeError:
            raise Exception(f"Generic Parser only supports text files. Binary file detected at {config_path}.")
            
        # 2. Prepare Prompt
        try:
            prompt_template = load_prompt(self.platform, "parser")
        except FileNotFoundError:
            # Fallback to a generic extraction prompt if specific one missing?
            # For now, strict:
            raise Exception(f"No parser prompt found for {self.platform}. Please create prompts/{self.platform}/parser.txt")

        schema_json = UAMEnvelope.model_json_schema()
        
        prompt = prompt_template.format(
            schema=json.dumps(schema_json, indent=2),
            source_code=source_code
        )
        
        # 3. Call LLM
        llm = get_llm()
        if not llm:
            raise Exception("LLM Client not initialized.")
            
        print("   Invoking LLM for Generic Extraction...")
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content
        
        # 4. Parse JSON Output
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        data = json.loads(content)
        
        # 5. Validate
        uam = UAMEnvelope(**data)
        uam.metadata["source"] = f"{self.platform} (Generic AI)"
        return uam
