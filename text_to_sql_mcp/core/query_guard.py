import sqlparse
from typing import Tuple, List

class SecurityViolation(Exception):
    pass

class QueryGuard:
    """
    Enforces security policies on generated SQL/NoSQL queries.
    Focus: READ-ONLY enforcement and Resource Limiting.
    """
    
    ALLOWED_SQL_KEYWORDS = {"SELECT", "WITH", "EXPLAIN", "PRAGMA", "SHOW", "DESCRIBE"}
    FORBIDDEN_SQL_KEYWORDS = {"INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "GRANT", "REVOKE", "CREATE"}
    
    @staticmethod
    def validate_sql(query: str) -> Tuple[bool, str]:
        """
        Parses SQL to ensure it is strictly read-only.
        Returns (is_safe: bool, reason: str)
        """
        parsed = sqlparse.parse(query)
        if not parsed:
            return False, "Empty query"
            
        for statement in parsed:
            tokens = [t for t in statement.flatten() if t.ttype in (sqlparse.tokens.Keyword, sqlparse.tokens.DML, sqlparse.tokens.DDL)]
            
            # Check 1: First keyword must be allowed
            cmd_type = statement.get_type().upper()
            if cmd_type not in QueryGuard.ALLOWED_SQL_KEYWORDS:
                return False, f"Forbidden statement type: {cmd_type}"
                
            # Check 2: Scan all keywords for hidden writes (e.g. DELETE inside a CTE or SPROC?) 
            # Note: sqlparse classification isn't perfect, but checking keyword existence is a strong heuristic
            for token in tokens:
                if token.value.upper() in QueryGuard.FORBIDDEN_SQL_KEYWORDS:
                    return False, f"Forbidden keyword detected: {token.value}"
                    
        return True, "Safe"

    @staticmethod
    def validate_nosql(query: dict) -> Tuple[bool, str]:
        """
        Validates a MongoDB-style query object.
        Supported: find, aggregate, count.
        Forbidden: insert, update, delete, drop.
        """
        if not isinstance(query, dict):
            return False, "NoSQL query must be a dictionary"
            
        op = query.get("operation")
        if not op:
            return False, "Missing 'operation' key"
            
        if op not in ["find", "aggregate", "count", "distinct"]:
            return False, f"Forbidden NoSQL operation: {op}"
            
        return True, "Safe"
