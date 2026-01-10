import streamlit as st
import os
from graph import app_graph
from config import Config

st.set_page_config(page_title="Autonomous Claims Adjuster", page_icon="🚗", layout="wide")

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Provider Selection
    provider = st.selectbox("LLM Provider", ["Azure OpenAI", "AWS Bedrock", "Google Gemini"])
    
    creds = {}
    
    if provider == "Azure OpenAI":
        api_key = st.text_input("Azure OpenAI Key", type="password", help="Overrides Config")
        endpoint = st.text_input("Azure Endpoint", help="Overrides Config")
        if api_key: creds["azure_key"] = api_key
        if endpoint: creds["azure_endpoint"] = endpoint
        
        # Set env vars for backward compatibility / RAG embeddings
        if api_key: os.environ["AZURE_OPENAI_API_KEY"] = api_key
        if endpoint: os.environ["AZURE_OPENAI_ENDPOINT"] = endpoint
        
    elif provider == "AWS Bedrock":
        creds["aws_access_key"] = st.text_input("AWS Access Key ID", type="password")
        creds["aws_secret_key"] = st.text_input("AWS Secret Access Key", type="password")
        creds["aws_region"] = st.text_input("AWS Region", value="us-east-1")
        creds["aws_model_id"] = st.text_input("Model ID", value="anthropic.claude-v2")
        
    elif provider == "Google Gemini":
        creds["google_key"] = st.text_input("Google API Key", type="password")
        creds["google_model"] = st.text_input("Model Name", value="gemini-pro")

    st.divider()
    st.info("Agent Status: Autopilot Active")

st.title("🚗 Autonomous Claims Adjuster (FNOL)")
st.markdown("### First Notice of Loss - Zero Touch Settlement")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Submit Claim")
    
    # Simulating Multi-Modal Input
    image_quality = st.radio("Simulate Photo Quality", ["Clear", "Blurry"], horizontal=True, help="Simulates VLM output")
    
    transcript = st.text_area(
        "Voice Note Transcript", 
        value="I was driving on the highway and a rock hit my windshield. It's cracked.",
        height=150
    )
    
    submit_btn = st.button("Submit Claim", type="primary")

with col2:
    st.subheader("🤖 Agent Activity")
    
    if submit_btn:
        initial_state = {
            "image_status": image_quality.lower(),
            "voice_transcript": transcript,
            "provider": provider,
            "credentials": creds,
            "intake_result": {},
            "policy_context": "",
            "coverage_verdict": {},
            "estimate_details": {},
            "status": "started",
            "final_message": ""
        }
        
        status_placeholder = st.empty()
        log_container = st.container(border=True)
        
        with st.spinner("Processing Claim..."):
            try:
                result = app_graph.invoke(initial_state)
                
                # 1. Intake Results
                log_container.markdown("#### 👁️ Intake Analysis")
                if result['intake_result'].get('is_valid'):
                    log_container.success(f"Damage Detected: {result['intake_result'].get('damage_detected')}")
                else:
                    log_container.error(f"Intake Failed: {result['intake_result'].get('error_reason')}")
                
                # 2. Verification Results
                if result.get('policy_context'):
                    log_container.markdown("#### 📜 Policy Verification")
                    if result.get('coverage_verdict', {}).get('is_covered'):
                        log_container.success(f"Coverage: {result['coverage_verdict']['reason']}")
                    else:
                        reason = result.get('coverage_verdict', {}).get('reason', 'Unknown')
                        log_container.error(f"Denied: {reason}")

                # 3. Estimation Results
                if result.get('estimate_details'):
                    log_container.markdown("#### 💰 Estimation")
                    est = result['estimate_details']
                    log_container.info(f"Total: ${est['total']:.2f}")
                    log_container.caption(est['breakdown'])
                
                # Final Status Display
                if result['status'] == "needs_input":
                    st.warning("⚠️ **ACTION REQUIRED**: The agent needs a clearer photo. Please re-submit.", icon="📸")
                elif result['status'] == "denied":
                    st.error(f"❌ **CLAIM DENIED**: {result['final_message']}")
                elif result['status'] == "completed":
                    st.balloons()
                    st.success(f"✅ **SETTLED**: {result['final_message']}")
                    
            except Exception as e:
                st.error(f"System Error: {str(e)}")
