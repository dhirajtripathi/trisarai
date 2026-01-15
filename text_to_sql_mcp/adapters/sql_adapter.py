from sqlalchemy import create_engine, text
from typing import List, Dict, Any
from text_to_sql_mcp.core.query_guard import QueryGuard

class SQLAdapter:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)

    def execute(self, query: str) -> List[Dict[str, Any]]:
        # 1. Security Check
        is_safe, reason = QueryGuard.validate_sql(query)
        if not is_safe:
            raise ValueError(f"Security Policy Violation: {reason}")
            
        # 2. Execution
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            # Convert keys to list for serialization
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            return rows

    def sample_data(self, table: str, limit: int = 5) -> List[Dict]:
        return self.execute(f"SELECT * FROM {table} LIMIT {limit}")
