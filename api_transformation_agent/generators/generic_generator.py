import json
from ..uam_schema import UAMEnvelope
from ..llm_utils import get_llm, load_prompt
from langchain_core.messages import HumanMessage

class GenericLLMGenerator:
    def __init__(self, platform: str):
        self.platform = platform

    def generate(self, uam: UAMEnvelope) -> str:
        print(f"🤖 [Generic AI Generator] Building {self.platform} Config...")
        
        # 1. Prepare Prompt
        try:
            prompt_template = load_prompt(self.platform, "generator")
        except FileNotFoundError:
             raise Exception(f"No generator prompt found for {self.platform}. Please create prompts/{self.platform}/generator.txt")

        uam_json = uam.model_dump_json(indent=2)
        
        prompt = prompt_template.format(uam_json=uam_json)
        
        # 2. Call LLM
        llm = get_llm()
        if not llm:
            raise Exception("LLM Client not initialized.")
            
        print("   Invoking LLM for Generic Generation...")
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
