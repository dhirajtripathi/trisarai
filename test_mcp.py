import requests
import json
import time

BASE_URL = "http://localhost:8000"

def run_tests():
    print("⏳ Waiting for server...")
    time.sleep(3)
    
    print("\n--- Test 1: Get Schema ---")
    res = requests.post(f"{BASE_URL}/mcp/tools/call", json={
        "name": "get_schema",
        "arguments": {"db_name": "demo_sql"}
    })
    print(json.dumps(res.json(), indent=2))
    
    print("\n--- Test 2: Generate Query (NL -> SQL) ---")
    res = requests.post(f"{BASE_URL}/mcp/tools/call", json={
        "name": "generate_query",
        "arguments": {"query": "Show me active users", "db_name": "demo_sql", "type": "sql"}
    })
    gen_result = res.json()["content"][0]["text"]
    print(f"Generated: {gen_result}")
    
    sql_script = gen_result["query"]
    
    print("\n--- Test 3: Execute Safe Query ---")
    res = requests.post(f"{BASE_URL}/mcp/tools/call", json={
        "name": "execute_query",
        "arguments": {"script": sql_script, "type": "sql"}
    })
    print(f"Result: {res.json()['content'][0]['text']}")

    print("\n--- Test 4: Execute Unsafe Query (Guardrail Check) ---")
    res = requests.post(f"{BASE_URL}/mcp/tools/call", json={
        "name": "execute_query",
        "arguments": {"script": "DROP TABLE users", "type": "sql"}
    })
    print(f"Result (Should be Error): {res.json()}")

if __name__ == "__main__":
    run_tests()
