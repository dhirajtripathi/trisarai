from typing import List, Dict, Any
from text_to_sql_mcp.core.query_guard import QueryGuard

class NoSQLAdapter:
    """
    Mock Adapter resembling PyMongo.
    """
    def __init__(self, mock_data: Dict[str, List[Dict]]):
        self.db = mock_data # { "users": [...], "orders": [...] }

    def execute(self, query: Dict) -> List[Dict[str, Any]]:
        # 1. Security Check
        is_safe, reason = QueryGuard.validate_nosql(query)
        if not is_safe:
            raise ValueError(f"Security Policy Violation: {reason}")
            
        collection = query.get("collection")
        op = query.get("operation")
        filter_dict = query.get("filter", {})
        
        if collection not in self.db:
            return []
            
        data = self.db[collection]
        
        # Very simple Mock implementation of 'find' with equality filter
        if op == "find":
            results = []
            for item in data:
                match = True
                for k, v in filter_dict.items():
                    if item.get(k) != v:
                        match = False
                        break
                if match:
                    results.append(item)
            return results
        
        return [{"error": "Operation not supported in Mock"}]

    def sample_data(self, collection: str, limit: int = 5) -> List[Dict]:
        if collection in self.db:
            return self.db[collection][:limit]
        return []
