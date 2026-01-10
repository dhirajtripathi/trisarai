import streamlit as st
import os
from graph import app_graph
from config import Config

# Page Config
st.set_page_config(page_title="Fraud 'Private Investigator'", page_icon="🕵️", layout="wide")

# Sidebar - Settings
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Provider Selection
    provider = st.selectbox("LLM Provider", ["Azure OpenAI", "AWS Bedrock", "Google Gemini"])
    
    creds = {}
    
    if provider == "Azure OpenAI":
        api_key = st.text_input("Azure OpenAI Key", type="password", help="Overrides Config")
        endpoint = st.text_input("Azure Endpoint", help="Overrides Config")
        if api_key: creds["azure_key"] = api_key
        if endpoint: creds["azure_endpoint"] = endpoint
        
    elif provider == "AWS Bedrock":
        creds["aws_access_key"] = st.text_input("AWS Access Key ID", type="password")
        creds["aws_secret_key"] = st.text_input("AWS Secret Access Key", type="password")
        creds["aws_region"] = st.text_input("AWS Region", value="us-east-1")
        creds["aws_model_id"] = st.text_input("Model ID", value="anthropic.claude-v2")
        
    elif provider == "Google Gemini":
        creds["google_key"] = st.text_input("Google API Key", type="password")
        creds["google_model"] = st.text_input("Model Name", value="gemini-pro")
        
    st.divider()
    st.caption("Investigator Controls")
    auto_dismiss_threshold = st.slider("Auto-Dismiss Score", 0, 50, 20)
    st.caption(f"Scores below {auto_dismiss_threshold} are auto-approved.")

# Main Layout
st.title("🕵️ Real-Time Fraud Investigator")
st.markdown("### Counter-Intelligence Unit")

col1, col2 = st.columns([1, 2])

# Left Column - Incoming Feed
with col1:
    st.subheader("📡 Incoming Claims")
    
    # Simulation Data
    claims = [
        {
            "id": "CLM-2026-001",
            "name": "John Doe Fake",
            "date": "2026-05-12",
            "desc": "Kitchen fire caused by toaster malfunction.",
            "photo": "kitchen_fire_001",
            "risk_label": "High Risk" # Hidden label for demo context
        },
        {
            "id": "CLM-2026-002",
            "name": "Sarah Smith",
            "date": "2026-06-20",
            "desc": "Rear-ended at stop light.",
            "photo": "bumper_dent_04",
            "risk_label": "Low Risk"
        },
        {
            "id": "CLM-2026-003",
            "name": "Project X Party",
            "date": "2026-07-04",
            "desc": "House destroyed by accidental fire while on vacation.",
            "photo": "house_fire_09",
            "risk_label": "Med Risk"
        }
    ]
    
    selected_claim = None
    
    for claim in claims:
        with st.container(border=True):
            st.markdown(f"**{claim['id']}**")
            st.caption(f"{claim['name']} | {claim['date']}")
            if st.button("Investigate", key=claim['id']):
                selected_claim = claim

# Right Column - Investigation Board
with col2:
    if not selected_claim:
        st.info("Select a claim from the feed to begin investigation.")
        st.image("https://placehold.co/600x400?text=Waiting+for+Assignment", width=600)
    else:
        st.subheader(f"📂 Case File: {selected_claim['id']}")
        
        # 1. Run Agent
        with st.status("🕵️ Agent is gathering intelligence...", expanded=True) as status:
            input_state = {
                "claim_id": selected_claim['id'],
                "claimant_name": selected_claim['name'],
                "claim_date": selected_claim['date'],
                "claim_description": selected_claim['desc'],
                "photo_id": selected_claim['photo'],
                "provider": provider,
                "credentials": creds
            }
            
            try:
                result = app_graph.invoke(input_state)
                
                st.write("✅ Social Media Scan Complete")
                st.write("✅ Ghost Broking DB Cross-Reference Complete")
                st.write("✅ Visual Anomaly Detection Complete")
                status.update(label="Investigation Complete", state="complete", expanded=False)

                # 2. Evidence Board
                st.divider()
                st.markdown("### 🧩 Evidence Board")
                
                for log in result['evidence_log']:
                    if "CRITICAL" in log or "Red Flag" in log:
                        st.error(log, icon="🚨")
                    elif "Found post" in log:
                        st.warning(log, icon="⚠️")
                    else:
                        st.success(log, icon="✅")

                # 3. Final Assessment & Human Actions
                st.divider()
                score = result['fraud_score']
                
                # Color coding the score dial
                delta_color = "normal"
                if score > 70: delta_color = "inverse"
                
                st.metric(label="Fraud Probability Score", value=f"{score}/100", delta="High Risk" if score > 70 else "Low Risk", delta_color=delta_color)
                
                st.markdown(f"**Agent Reasoning:**")
                st.info(result['risk_reasoning'])

                # HITL Logic
                if result['requires_human_review']:
                    st.warning("⚠️ **INTERVENTION REQUIRED**: Fraud Score exceeds threshold.")
                    
                    action_col1, action_col2 = st.columns(2)
                    with action_col1:
                        if st.button("🔴 CONFIRM FRAUD & REJECT", use_container_width=True, type="primary"):
                            st.success("Claim Rejected. User flagged in Ghost Broking DB.")
                    with action_col2:
                        if st.button("🟢 DISMISS & APPROVE", use_container_width=True):
                            st.success("Claim Approved. False Alarm logged.")
                else:
                    st.balloons()
                    st.success("✅ **AUTO-APPROVED**: Claim meets safety standards.")
                    
            except Exception as e:
                st.error(f"Error running investigation: {str(e)}")
                st.write("Please check your credentials in the sidebar.")
                status.update(label="Investigation Failed", state="error", expanded=True)
