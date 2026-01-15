# User Guide: Integration Migration Agent

## 1. Functional Overview
The **Integration Migration Agent** targets the specific niche of "Middleware Replatforming". Many large enterprises are moving away from expensive, proprietary Enterprise Service Buses (TIBCO, webMethods, MuleSoft) toward lightweight, cloud-native microservices (Spring Boot, Camel, Logic Apps). This tool reverse-engineers the proprietary logic and rewrites it in open standards.

### Business Value
*   **Vendor Lock-in Removal**: Eliminates dependency on expensive legacy licensing by moving to open-source or cloud-native targets.
*   **Logic Extraction**: Legacy logic is often undocumented ("Black Box"). The agent extracts the flow and explains *what* it does in plain English before converting it.
*   **Test Generation**: A major risk in migration is regression. This agent auto-generates JUnit tests based on the inferred logic to ensure the new code behaves exactly like the old code.

### Key Capabilities
*   **Pattern Recognition**: Identifying integration patterns like "Scatter-Gather", "Circuit Breaker", or "Content-Based Router" in the legacy XML.
*   **Polyglot Generation**: Can output Java (Spring Boot), Python (FastAPI), or Azure Logic Apps (JSON).
*   **Complexity Scoring**: Estimates the "Difficulty of Migration" (Low/Med/High) to help project managers plan sprints.

### System Workflow
```mermaid
graph TD
    XML[Legacy XML Flow] -->|Ingest| Graph[Flow Graph]
    Graph -->|Identify Patterns| Analysis[Pattern Matcher]
    
    Analysis -->|Scatter-Gather| Target[Spring Boot Generator]
    Target -->|Convert| Java[Java Code]
    Target -->|Convert| Unit[JUnit Tests]
    
    Java -->|Verify| Build[Compiler Check]
```

## 2. Launching the Tool
*   **Direct URL**: `http://localhost:5178` (UI)

## 3. Step-by-Step Walkthrough

### A. Assessment
1.  **Upload**: Provide a `flow.xml` from the legacy ESB.
2.  **Dashboard**: See the Complexity Score.
    *   *Lines of Code*: 200.
    *   *Nodes*: 15.
    *   *External Calls*: 3 (Database, CRM, SAP).

### B. Conversion
1.  **Target**: Choose "Java Spring Boot".
2.  **Run**: The agent writes the code class-by-class.
3.  **Inspect**:
    *   The `Database Connector` in XML becomes a `JPA Repository` in Java.
    *   The `Transformer` mapping becomes a `MapStruct` mapper.

### C. Refactoring
1.  **Prompt**: "Make this code reactive using WebFlux."
2.  **Result**: The agent rewrites the synchronous `RestTemplate` calls to asynchronous `WebClient` chains.

## 4. Limitations
*   Complex custom scripts (e.g., embedded Groovy/Java in the XML) may require manual review as the agent might not have the full context.
