import json
from ..uam_schema import UAMEnvelope
from ..llm_utils import get_llm, load_prompt
from langchain_core.messages import HumanMessage

class AzureParser:
    def parse(self, config_path: str) -> UAMEnvelope:
        print(f"🤖 [AI Parser] Analyzing Azure Config: {config_path}")
        
        # 1. Read Content
        with open(config_path, "r") as f:
            source_code = f.read()
            
        # 2. Prepare Prompt
        prompt_template = load_prompt("azure", "parser")
        schema_json = UAMEnvelope.model_json_schema()
        
        prompt = prompt_template.format(
            schema=json.dumps(schema_json, indent=2),
            source_code=source_code
        )
        
        # 3. Call LLM
        llm = get_llm()
        if not llm:
            raise Exception("LLM Client not initialized.")
            
        print("   Invoking LLM for Extraction...")
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content
        
        # 4. Parse JSON Output
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        print("   LLM Response received. Parsing JSON...")
        data = json.loads(content)
        
        # 5. Validate
        uam = UAMEnvelope(**data)
        uam.metadata["source"] = "azure (AI-Extracted)"
        return uam
