import os
import json
import xml.etree.ElementTree as ET
from typing import List
from ..uam_schema import UAMEnvelope
from ..llm_utils import get_llm, load_prompt
from langchain_core.messages import HumanMessage

class ApigeeParser:
    def parse(self, bundle_path: str) -> UAMEnvelope:
        print(f"🤖 [AI Parser] Scanning Apigee Bundle: {bundle_path}")
        
        # 1. Aggregate Source Code
        source_code_snippet = ""
        
        # Walk through important folders
        for root_dir, _, files in os.walk(bundle_path):
            for file in files:
                if file.endswith(".xml"):
                    file_path = os.path.join(root_dir, file)
                    rel_path = os.path.relpath(file_path, bundle_path)
                    
                    # Read content
                    with open(file_path, "r") as f:
                        content = f.read()
                        
                    source_code_snippet += f"\n--- FILE: {rel_path} ---\n{content}\n"
        
        # 2. Prepare Prompt
        try:
            prompt_template = load_prompt("apigee", "parser")
            schema_json = UAMEnvelope.model_json_schema()
            
            prompt = prompt_template.format(
                schema=json.dumps(schema_json, indent=2),
                source_code=source_code_snippet
            )
            
            # 3. Call LLM
            llm = get_llm()
            if not llm:
                raise Exception("LLM Client not initialized. Check API Keys.")
                
            print("   Invoking LLM for Extraction...")
            response = llm.invoke([HumanMessage(content=prompt)])
            content = response.content
            
            # 4. Parse JSON Output
            # Strip markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
                
            print("   LLM Response received. Parsing JSON...")
            data = json.loads(content)
            
            # 5. Validate with Pydantic
            uam = UAMEnvelope(**data)
            uam.metadata["source"] = "apigee (AI-Extracted)"
            return uam
            
        except Exception as e:
            print(f"❌ AI Parsing Failed: {e}")
            # Fallback? OR Re-raise
            raise e
