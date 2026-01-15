# Agentic Compliance Bot
**Usecase Name**: `compliance_bot`

## 1. Functional Overview
The **Compliance Bot** is an always-on guardian that checks business processes against regulatory documents (GDPR, HIPAA, Internal Policies). It can operate as a chat assistant for employees or as a passive scanner for documents.

### Key Features
*   **Regulatory RAG**: Answers "Is this allowed?" by citing specific paragraphs from PDF uploads.
*   **Contract Review**: Upload a Vendor Contract -> Agent flags "Missing Liability Clause".
*   **Audit Prep**: Generates "Compliance Certification" reports.

## 2. Technical Architecture
A specialized RAG application with **Reasoning Loops**.

### Core Flow (`graph_workflow.py`)
1.  **Retrieval**: Fetches relevant policy sections.
2.  **Reasoning**: "Does the contract text VIOLATE policy section 3.2?"
    *   *Note*: Simple RAG retrieves similar text. This agent compares conflicting text.
3.  **Conclusion**: Generates a Pass/Fail verdict with Citations.

## 3. Implementation Steps

### Prerequisites
*   Python 3.10+
*   Vector DB (Chroma/FAISS) embedded.

### Setup & Run
1.  **Navigate**: `cd compliance_bot`
2.  **Install**: `pip install -r requirements.txt`
3.  **Run**: `streamlit run app.py`

### Usage
Upload a PDF policy (e.g., "Travel Expense Policy"). Then ask: "Can I fly Business Class to London?" -> Agent checks distance rules in policy and answers.
