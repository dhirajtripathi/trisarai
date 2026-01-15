import json
from ..uam_schema import UAMEnvelope
from ..llm_utils import get_llm, load_prompt
from langchain_core.messages import HumanMessage

class AzureGenerator:
    def generate(self, uam: UAMEnvelope) -> str:
        print("🤖 [AI Generator] Building Azure Terraform Config...")
        
        # 1. Prepare Prompt
        prompt_template = load_prompt("azure", "generator")
        uam_json = uam.model_dump_json(indent=2)
        
        prompt = prompt_template.format(uam_json=uam_json)
        
        # 2. Call LLM
        llm = get_llm()
        if not llm:
            raise Exception("LLM Client not initialized.")
            
        print("   Invoking LLM for Generation...")
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content
        
        # 3. Extract HCL/Terraform
        if "```hcl" in content:
            content = content.split("```hcl")[1].split("```")[0].strip()
        elif "```terraform" in content:
            content = content.split("```terraform")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        return content
