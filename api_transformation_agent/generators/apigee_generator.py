import json
from ..uam_schema import UAMEnvelope
from ..llm_utils import get_llm, load_prompt
from langchain_core.messages import HumanMessage

class ApigeeGenerator:
    def generate(self, uam: UAMEnvelope) -> str:
        print("🤖 [AI Generator] Building Apigee XML Bundle...")
        
        # 1. Prepare Prompt
        prompt_template = load_prompt("apigee", "generator")
        uam_json = uam.model_dump_json(indent=2)
        
        prompt = prompt_template.format(uam_json=uam_json)
        
        # 2. Call LLM
        llm = get_llm()
        if not llm:
            raise Exception("LLM Client not initialized.")
            
        print("   Invoking LLM for Generation...")
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content
        
        # 3. Return Raw Markdown (containing XMLs)
        # We don't parse strictly here because the prompt asks for multiple files.
        # The user will see the block of proposed XMLs.
        return content
