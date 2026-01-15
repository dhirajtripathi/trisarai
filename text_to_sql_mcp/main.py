from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os

from text_to_sql_mcp.core.schema_manager import SchemaManager
from text_to_sql_mcp.core.generator import QueryGenerator
from text_to_sql_mcp.core.er_generator import ERDiagramGenerator
from text_to_sql_mcp.adapters.sql_adapter import SQLAdapter
from text_to_sql_mcp.adapters.nosql_adapter import NoSQLAdapter

from text_to_sql_mcp.config import settings

app = FastAPI(title="Text-to-SQL MCP Server")

# --- Globals (for runtime switching) ---
sql_adapter = None
nosql_adapter = None
schema_manager = SchemaManager()

# --- Setup DB Helper ---
def init_db():
    global sql_adapter
    is_real_db = settings.is_real_db()
    
    if is_real_db:
        print(f"🔌 Connecting to Real Database: {settings.DATABASE_URL.split('@')[-1]}")
        CONN_STR = settings.DATABASE_URL
        DB_PATH = None
    else:
        print(f"🧪 Using Demo SQLite Database (Mock Mode)")
        DB_PATH = "demo.db"
        CONN_STR = f"sqlite:///{DB_PATH}"

    # Init Adapters
    sql_adapter = SQLAdapter(CONN_STR)
    
    # Init Demo Data (Only if Mock)
    if not is_real_db and DB_PATH:
        import sqlite3
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, status TEXT)")
            conn.execute("INSERT OR IGNORE INTO users (id, name, status) VALUES (1, 'Alice', 'active')")
            conn.execute("INSERT OR IGNORE INTO users (id, name, status) VALUES (2, 'Bob', 'inactive')")
            conn.execute("CREATE TABLE IF NOT EXISTS orders (order_id INTEGER, amount REAL, user_id INTEGER, FOREIGN KEY(user_id) REFERENCES users(id))")
            conn.execute("INSERT OR IGNORE INTO orders (order_id, amount, user_id) VALUES (101, 50.00, 1)")

    # Scan Schema
    try:
        schema_manager.scan_sql_db("demo_sql", CONN_STR)
        
        # Try to load context
        import json
        if os.path.exists("demo_context.json"):
             with open("demo_context.json", "r") as f:
                context = json.load(f)
                schema_manager.enrich_schema("demo_sql", context)
    except Exception as e:
        print(f"⚠️ DB Scan Error: {e}")

@app.on_event("startup")
def startup():
    global nosql_adapter
    nosql_adapter = NoSQLAdapter({
        "logs": [{"id": 1, "msg": "login"}, {"id": 2, "msg": "logout"}]
    })
    schema_manager.register_nosql_schema("demo_nosql", {"collections": ["logs"]})
    
    init_db()
    print("✅ MCP Server Initialized")


# --- Config API ---

class ConfigUpdate(BaseModel):
    llm_model: Optional[str] = None
    database_url: Optional[str] = None
    api_keys: Optional[Dict[str, str]] = None

@app.get("/mcp/config")
async def get_config():
    return {
        "llm_model": settings.LLM_MODEL,
        "database_url": settings.DATABASE_URL,
        "is_real_llm": settings.is_real_llm(),
        "is_real_db": settings.is_real_db()
    }

@app.post("/mcp/config")
async def update_config(config: ConfigUpdate):
    settings.update(config.llm_model, config.database_url, config.api_keys)
    
    # Re-connect if DB URL changed
    if config.database_url is not None:
        try:
            init_db()
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    return {"status": "updated", "current_model": settings.LLM_MODEL}

@app.post("/mcp/config/test")
async def test_connection():
    try:
        # Test Query
        sql_adapter.execute("SELECT 1")
        return {"status": "ok", "message": "Database Connected Successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# --- MCP Protocol ---

class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]

@app.post("/mcp/tools/call")
async def call_tool(tool: ToolCall):
    name = tool.name
    args = tool.arguments
    
    if name == "generate_query":
        query = args.get("query")
        db_name = args.get("db_name")
        type_ = args.get("type", "sql")
        schema = schema_manager.get_schema(db_name)
        result = QueryGenerator.generate(query, schema, type_)
        return {"content": [{"type": "json", "text": result}]}
        
    elif name == "execute_query":
        script = args.get("script")
        type_ = args.get("type", "sql")
        try:
            if type_ == "sql":
                data = sql_adapter.execute(script)
            else:
                data = nosql_adapter.execute(script)
            return {"content": [{"type": "json", "text": data}]}
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    elif name == "get_schema":
        db_name = args.get("db_name")
        schema = schema_manager.get_schema(db_name)
        return {"content": [{"type": "json", "text": schema}]}
        
    elif name == "get_er_diagram":
        db_name = args.get("db_name")
        schema = schema_manager.get_schema(db_name)
        mermaid = ERDiagramGenerator.generate_mermaid(schema)
        return {"content": [{"type": "text", "text": mermaid}]}

    else:
        raise HTTPException(404, "Tool not found")

@app.get("/mcp/resources/list")
async def list_resources():
    return {
        "resources": [
            {"uri": "schema://demo_sql", "name": "SQL Demo Schema", "mimeType": "application/json"},
            {"uri": "er_diagram://demo_sql", "name": "SQL Demo ER Diagram", "mimeType": "text/vnd.mermaid"},
            {"uri": "schema://demo_nosql", "name": "NoSQL Demo Schema", "mimeType": "application/json"}
        ]
    }
