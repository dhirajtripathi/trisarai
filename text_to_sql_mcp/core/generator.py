import json
from ..config import settings
from .llm_service import LLMService

class QueryGenerator:
    """
    Hybrid Query Generator: Mock vs Real LLM.
    """
    
    _llm_service = None

    @classmethod
    def get_llm(cls):
        if not cls._llm_service:
            cls._llm_service = LLMService()
        return cls._llm_service
    
    @staticmethod
    def generate(nl_query: str, schema: dict, db_type: str = "sql") -> dict:
        # 1. Real LLM Mode
        if settings.is_real_llm():
            try:
                print(f"🧠 Using Real LLM ({settings.LLM_MODEL})")
                return QueryGenerator.get_llm().generate_sql(nl_query, schema, db_type)
            except Exception as e:
                print(f"⚠️ LLM Error: {e}. Falling back to Mock.")
                # Fallthrough to Mock
        
        # 2. Mock Mode (Heuristic)
        print("🤖 Using Mock Generator")
        nl_query = nl_query.lower()
        
        # Scenario 1: "Show users"
        if "users" in nl_query:
            if db_type == "sql":
                return {
                    "query": "SELECT * FROM users LIMIT 10",
                    "reasoning": "User asked for users. Selected all columns with a safety limit.",
                    "confidence": 0.95
                }
            else:
                 return {
                    "query": {"collection": "users", "operation": "find", "filter": {}},
                    "reasoning": "NoSQL find on users collection.",
                    "confidence": 0.95
                }
                
        # Scenario 2: "Where status is active"
        if "active" in nl_query:
            if db_type == "sql":
                return {
                    "query": "SELECT * FROM users WHERE status = 'active' LIMIT 10",
                    "reasoning": "Detected filter condition on 'status'.",
                    "confidence": 0.90
                }
        
        # Scenario 3: Aggregation "Count orders"
        if "count" in nl_query and "orders" in nl_query:
            if db_type == "sql":
                return {
                    "query": "SELECT count(*) FROM orders",
                    "reasoning": "Aggregation request detected.",
                    "confidence": 0.98
                }

        # Scenario 4: Join "Orders with user names"
        if "orders" in nl_query and ("user" in nl_query or "name" in nl_query):
            if db_type == "sql":
                return {
                    "query": "SELECT o.order_id, o.amount, u.name FROM orders o JOIN users u ON o.user_id = u.id LIMIT 20",
                    "reasoning": "Detected relationship request. Joining 'orders' with 'users' on 'user_id'.",
                    "confidence": 0.92
                }
                
        return {
            "query": "-- Could not generate query",
            "reasoning": "Query logic not found in Mock Rules. Try 'Show active users' or 'Count orders'.",
            "confidence": 0.1
        }
