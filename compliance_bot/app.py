import streamlit as st
import os
from graph_workflow import graph
from config import Config
from rag_knowledge import add_regulation

st.set_page_config(page_title="Compliance & Audit Bot", layout="wide")

st.title("🛡️ Multi-Jurisdictional Compliance & Audit Bot")
st.markdown("""
This bot scans outgoing claim decisions or policy quotes against regulations.
If a violation is detected, the **Guardrail** layer blocks it and rewrites the response.
""")

# Sidebar Config
st.sidebar.header("Configuration")
provider = st.sidebar.selectbox("Select LLM Provider", ["Azure OpenAI", "AWS Bedrock", "Google Gemini"])

# Credentials logic
if provider == "Azure OpenAI":
    api_key = st.sidebar.text_input("Azure OpenAI API Key", value=Config.AZURE_OPENAI_API_KEY if Config.AZURE_OPENAI_API_KEY else "", type="password")
    endpoint = st.sidebar.text_input("Azure Endpoint", value=Config.AZURE_OPENAI_ENDPOINT if Config.AZURE_OPENAI_ENDPOINT else "")
    if api_key: os.environ["AZURE_OPENAI_API_KEY"] = api_key
    if endpoint: os.environ["AZURE_OPENAI_ENDPOINT"] = endpoint
elif provider == "AWS Bedrock":
    st.sidebar.info("Ensure you have AWS credentials set up or provide them below.")
    aws_access_key = st.sidebar.text_input("AWS Access Key ID", value=Config.AWS_ACCESS_KEY_ID if Config.AWS_ACCESS_KEY_ID else "", type="password")
    aws_secret_key = st.sidebar.text_input("AWS Secret Access Key", value=Config.AWS_SECRET_ACCESS_KEY if Config.AWS_SECRET_ACCESS_KEY else "", type="password")
    aws_region = st.sidebar.text_input("AWS Region", value=Config.AWS_DEFAULT_REGION if Config.AWS_DEFAULT_REGION else "us-east-1")
    if aws_access_key: os.environ["AWS_ACCESS_KEY_ID"] = aws_access_key
    if aws_secret_key: os.environ["AWS_SECRET_ACCESS_KEY"] = aws_secret_key
    if aws_region: os.environ["AWS_DEFAULT_REGION"] = aws_region
elif provider == "Google Gemini":
    google_key = st.sidebar.text_input("Google API Key", value=Config.GOOGLE_API_KEY if Config.GOOGLE_API_KEY else "", type="password")
    if google_key: os.environ["GOOGLE_API_KEY"] = google_key

# Knowledge Base Upload
st.sidebar.markdown("---")
st.sidebar.header("Knowledge Base")
uploaded_files = st.sidebar.file_uploader("Upload Regulations (.txt)", accept_multiple_files=True, type=["txt"])
manual_reg_source = st.sidebar.text_input("Source Name (e.g. New Law)")
manual_reg_text = st.sidebar.text_area("Regulation Text")

if st.sidebar.button("Add to Knowledge Base"):
    added_count = 0
    with st.spinner("Updating Vector Store..."):
        # Process Manual Entry
        if manual_reg_source and manual_reg_text:
            add_regulation(manual_reg_text, manual_reg_source)
            added_count += 1
        
        # Process Uploads
        if uploaded_files:
            for uploaded_file in uploaded_files:
                # Read file as string
                string_data = uploaded_file.getvalue().decode("utf-8")
                add_regulation(string_data, uploaded_file.name)
                added_count += 1
    
    if added_count > 0:
        st.sidebar.success(f"Successfully added {added_count} items to the Knowledge Base.")
    else:
        st.sidebar.warning("No valid input provided to add.")


# Main Input
st.subheader(f"Draft Response Check (Model: {provider})")
draft_text = st.text_area("Enter Draft Claim Decision / Policy Quote:", height=150, 
                          value="We are denying your claim because it doesn't meet our internal criteria. We used an AI system to decide this.")

if st.button("Scan for Compliance"):
    # Check credentials existence
    missing_creds = False
    if provider == "Azure OpenAI" and not os.environ.get("AZURE_OPENAI_API_KEY"): missing_creds = True
    if provider == "AWS Bedrock" and not os.environ.get("AWS_ACCESS_KEY_ID"): missing_creds = True
    if provider == "Google Gemini" and not os.environ.get("GOOGLE_API_KEY"): missing_creds = True
    
    if missing_creds:
        st.error(f"Please provide credentials for {provider} in the sidebar.")
    else:
        with st.spinner(f"Scanning regulations and checking compliance using {provider}..."):
            try:
                # Invoke the graph
                initial_state = {
                    "draft_text": draft_text, 
                    "relevant_regulations": [], 
                    "compliance_status": "", 
                    "feedback": "", 
                    "final_output": "",
                    "llm_provider": provider
                }
                result = graph.invoke(initial_state)
                
                # Display Results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info("### 📋 Analysis")
                    st.write(f"**Status:** {result['compliance_status']}")
                    if result['compliance_status'] == "VIOLATION":
                        st.error(f"**Violation Details:** {result['feedback']}")
                    else:
                        st.success("Message is compliant.")
                    
                    st.write("**Relevant Regulations Found:**")
                    if result['relevant_regulations']:
                        for reg in result['relevant_regulations']:
                            st.caption(f"- {reg}")
                    else:
                        st.caption("No specific regulations triggered.")

                with col2:
                    st.info("### 📝 Final Output")
                    if result['compliance_status'] == "VIOLATION":
                        st.warning("Original draft was blocked. Here is the rewritten version:")
                        st.text_area("Final Safe Response", value=result['final_output'], height=200)
                    else:
                        st.success("Original draft approved.")
                        st.text_area("Final Safe Response", value=result['final_output'], height=200)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
