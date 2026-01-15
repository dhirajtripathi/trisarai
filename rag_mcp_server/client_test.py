import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200
    print("✅ Health check passed")

def test_ingest_document():
    payload = {
        "name": "ingest_document",
        "arguments": {
            "filename": "mcp_guide.txt",
            "content": """
            Model Context Protocol (MCP) is an open standard that enables developers to build secure, 
            two-way connections between AI systems and their data sources. 
            Mcp servers expose resources and tools.
            Resources are read-only data, while tools are actions.
            """,
            "metadata": {"category": "tech_docs"}
        }
    }
    resp = requests.post(f"{BASE_URL}/tools/call", json=payload)
    assert resp.status_code == 200
    r_json = resp.json()
    print(f"✅ Ingest response: {r_json}")
    
    # Parse inner text to get doc ID if needed, but for now just pass
    return r_json

def test_ingest_file():
    import os
    file_path = os.path.abspath("sample.pdf")
    if not os.path.exists(file_path):
        print("⚠️ Sample PDF not found, skipping file ingest test (run pandoc command first)")
        return

    payload = {
        "name": "ingest_file",
        "arguments": {
            "file_path": file_path,
            "metadata": {"category": "test_pdf"}
        }
    }
    resp = requests.post(f"{BASE_URL}/tools/call", json=payload)
    if resp.status_code != 200:
        print(f"❌ Ingest file failed: {resp.text}")
        return
        
    r_json = resp.json()
    print(f"✅ Ingest FILE response: {r_json}")

def test_ask_question():
    payload = {
        "name": "ask_question",
        "arguments": {
            "query": "What is the Model Context Protocol (MCP)?"
        }
    }
    # Note: Requires configured LLM to work, otherwise mock or error
    resp = requests.post(f"{BASE_URL}/tools/call", json=payload)
    if resp.status_code != 200:
        print(f"❌ Ask Question failed: {resp.text}")
        return
        
    r_json = resp.json()
    print(f"✅ Ask Question response: {r_json}")

def test_ask_question_no_context():
    print("\n--- Testing Edge Case: Irrelevant Query ---")
    payload = {
        "name": "ask_question",
        "arguments": {
            "query": "What is the capital of Mars and its relation to cheese production?"
        }
    }
    resp = requests.post(f"{BASE_URL}/tools/call", json=payload)
    if resp.status_code != 200:
        print(f"❌ Ask Question (No Context) failed: {resp.text}")
        return
        
    r_json = resp.json()
    print(f"✅ Ask Question (No Context) response: {r_json}")
    # We expect a specific message if thresholding works and no docs match
    # response text should contain "couldn't find any relevant information"

def test_search_resources():
    # Wait a bit for async indexing if any (here it's sync so no wait needed really)
    # Search for 'MCP'
    params = {"q": "MCP", "limit": 2}
    resp = requests.get(f"{BASE_URL}/resources/read?uri=rag://search", params=params)
    
    # NOTE: The router expects params in the URI itself for correct parsing in the current implementation
    # Let's fix the test to call it exactly as the Resource URI template suggests or how MCP clients do it
    # Client puts full URI in query param 'uri'
    
    # Correct call:
    search_uri = "rag://search?q=MCP&limit=2"
    resp = requests.get(f"{BASE_URL}/resources/read", params={"uri": search_uri})
    
    assert resp.status_code == 200
    data = resp.json()
    print(f"✅ Search response keys: {data.keys()}")
    content_text = data['contents'][0]['text']
    results = json.loads(content_text)
    print(f"✅ Found {len(results)} chunks")
    if len(results) > 0:
        print(f"   Top result score: {results[0]['score']}")
        print(f"   Preview: {results[0]['text'][:50]}...")

def run_tests():
    print("Wait for server to be up...")
    time.sleep(2)
    try:
        test_health()
        test_ingest_document()
        test_ingest_file()
        test_search_resources()
        test_ask_question()
        test_ask_question_no_context()
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    run_tests()
