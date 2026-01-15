from typing import Dict, List, Any
from sqlalchemy import create_engine, inspect

class SchemaManager:
    """
    Extracts and standardizes Schema Metadata from DB connections.
    """
    
    def __init__(self):
        self._schemas = {} # Cache
        
    def scan_sql_db(self, db_name: str, connection_string: str) -> Dict[str, Any]:
        """
        Uses SQLAlchemy to inspect a relational DB.
        """
        engine = create_engine(connection_string)
        inspector = inspect(engine)
        
        schema_info = {
            "tables": [],
            "metadata": {}
        }
        
        for table_name in inspector.get_table_names():
            columns = []
            for col in inspector.get_columns(table_name):
                columns.append({
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"]
                })
            
            # Foreign Keys
            fks = inspector.get_foreign_keys(table_name)
            
            table_def = {
                "name": table_name,
                "columns": columns,
                "foreign_keys": [{"constrained_columns": fk["constrained_columns"], "referred_table": fk["referred_table"]} for fk in fks]
            }
            
            schema_info["tables"].append(table_def)
            
        self._schemas[db_name] = schema_info
        return schema_info

    def register_nosql_schema(self, db_name: str, schema_def: Dict):
        """
        Manually register schema for NoSQL (since inspecting schema-less DBs is hard).
        """
        self._schemas[db_name] = schema_def

    def get_schema(self, db_name: str) -> Dict:
        return self._schemas.get(db_name, {})

    def enrich_schema(self, db_name: str, context: Dict[str, Any]):
        """
        Merges business context (descriptions, synonyms) into the schema.
        Context Format:
        {
            "tables": {
                "users": {
                    "description": "Registered customers",
                    "columns": { "status": "Active means logged in last 30 days" }
                }
            }
        }
        """
        schema = self.get_schema(db_name)
        if not schema: return
        
        context_tables = context.get("tables", {})
        
        for table in schema.get("tables", []):
            t_name = table["name"]
            if t_name in context_tables:
                ctx = context_tables[t_name]
                table["description"] = ctx.get("description", "")
                
                # Merge Column Descriptions
                ctx_cols = ctx.get("columns", {})
                for col in table["columns"]:
                    if col["name"] in ctx_cols:
                        col["description"] = ctx_cols[col["name"]]
        
        self._schemas[db_name] = schema
