# API Transformation Agent
**Usecase Name**: `api_transformation_agent`

## 1. Functional Overview
The **API Transformation Agent** accelerates the modernization of legacy interfaces. It checks WSDL/SOAP services or monolithic RAML specs and automatically refactors them into OpenAPI 3.0 (REST) specifications, while also generating the necessary Infrastructure-as-Code (Terraform) and Gateway Configurations (Kong/Apigee).

### Key Features
*   **Protocol Conversion**: SOAP XML -> REST JSON Auto-mapping.
*   **Infrastructure Generation**: Creates Terraform modules for Azure API Management.
*   **Gateway Config**: Generates Kong `declarative.yaml` or Apigee proxies.
*   **Linting**: Ensures the new spec meets modern standards (Spectral rules).

## 2. Technical Architecture
A pipeline-based agentic workflow.

### Components
1.  **Parsers (`/parsers`)**:
    *   Ingests WSDL, RAML, or Legacy Java Interfaces.
    *   Extracts "Intents" (Operations) and "Entities" (Data Models).
2.  **LLM Mapper (`llm_utils.py`)**:
    *   Uses Few-Shot prompting to map arcane Legacy field names (`CUST_ID_99`) to clean Domain names (`customerId`).
3.  **Generators (`/generators`)**:
    *   `OpenAPI Generator`: Outputs `swagger.yaml`.
    *   `Terraform Generator`: Outputs `main.tf`.

## 3. Implementation Steps

### Prerequisites
*   Python 3.10+
*   Terraform (optional, for deployment)

### Setup & Run
1.  **Navigate**: `cd api_transformation_agent`
2.  **Install**: `pip install -r requirements.txt`
3.  **Run UI**: `streamlit run ui/Home.py`

### Usage
1.  Upload a `.wsdl` file in the UI.
2.  Review the Agent's proposed "Operation Map".
3.  Click **Generate**.
4.  Download the `openapi.json` and `azure_apim.tf` bundle.

## 4. Context Engineering
The primary challenge is preserving business logic during translation. We use:
*   **Semantic Mapping Prompts**: "Given this SOAP XML Logic, what is the equivalent RESTful resource verb/path?"
*   **Context Windowing**: handling massive WSDL files by splitting them into semantic chunks (PortTypes).
