from litellm import completion
import json
from ..config import settings

class LLMService:
    def __init__(self):
        # LiteLLM does not require a client init; it's stateless/func-based
        pass

    def generate_sql(self, query: str, schema_context: dict, type: str = "sql") -> dict:
        if not settings.is_real_llm():
            raise ValueError("Mock Mode is active. Do not call LLMService.")

        system_prompt = f"""
You are an expert Data Analyst and Database Engineer.
Your goal is to generate READ-ONLY {type.upper()} queries based on the user's natural language request.

CONTEXT:
{json.dumps(schema_context, indent=2)}

RULES:
1. Return ONLY a JSON object with keys: "query", "reasoning", "confidence".
2. Use ONLY the tables and columns provided in existing Schema Context.
3. For SQL, use standard PostgreSQL dialect (unless tailored by model context).
4. STRICTLY READ-ONLY. NO INSERT, UPDATE, DELETE, DROP.
5. Always LIMIT results to 100 unless asked otherwise.
6. "reasoning" should explain your logic in 1 sentence.

OUTPUT FORMAT:
{{
  "query": "SELECT ...",
  "reasoning": "...",
  "confidence": 0.95
}}
"""

        print(f"🧠 Calling LiteLLM Model: {settings.LLM_MODEL}")
        
        # Unified call for OpenAI, Azure, Bedrock, Gemini, etc.
        response = completion(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        
        # Clean up potential markdown formatting (```json ... ```)
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "")
        elif content.startswith("```"):
            content = content.replace("```", "")
            
        return json.loads(content)
