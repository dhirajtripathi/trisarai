import streamlit as st
import os
from datetime import datetime
from agent import agent_graph, AgentState
from data_models import CustomerProfile, LifeEvent
from config import Config

# Page Config
st.set_page_config(page_title="Policy Lifecycle Manager", layout="wide")

# Sidebar - Config & Simulation
st.sidebar.title("Configuration")
api_key = st.sidebar.text_input("Azure OpenAI API Key", value=Config.AZURE_OPENAI_API_KEY if Config.AZURE_OPENAI_API_KEY else "", type="password")
endpoint = st.sidebar.text_input("Azure Endpoint", value=Config.AZURE_OPENAI_ENDPOINT if Config.AZURE_OPENAI_ENDPOINT else "")

if api_key: os.environ["AZURE_OPENAI_API_KEY"] = api_key
if endpoint: os.environ["AZURE_OPENAI_ENDPOINT"] = endpoint

st.sidebar.markdown("---")
st.sidebar.title("Simulate Life Event")

# Initialize Session State for Customer
if "customer" not in st.session_state:
    st.session_state.customer = CustomerProfile(
        id="CUST-101",
        name="Alex Doe",
        age=29,
        existing_policies=["Renters"],
        annual_premium=250.00,
        risk_score=20
    )

selected_event = None
if st.sidebar.button("💍 Getting Married"):
    selected_event = LifeEvent(event_type="Marriage", description="Got married to Sarah.", timestamp=str(datetime.now()))
if st.sidebar.button("🏠 Buying a Home"):
    selected_event = LifeEvent(event_type="New Home", description="Purchased a 3-bedroom house in fanwood, NJ.", timestamp=str(datetime.now()))
if st.sidebar.button("🚗 Buying a New Car"):
    selected_event = LifeEvent(event_type="New Car", description="Bought a 2025 Tesla Model Y.", timestamp=str(datetime.now()))

# Main Layout
st.title("🛡️ Hyper-Personalized Policy Lifecycle Manager")
st.markdown("Proactively monitoring customer life events to recommend tailored coverage.")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Customer Profile")
    c = st.session_state.customer
    st.info(f"""
    **Name:** {c.name}  
    **Age:** {c.age}  
    **Risk Score:** {c.risk_score}  
    **Current Policies:** {", ".join(c.existing_policies)}  
    **Annual Premium:** ${c.annual_premium:.2f}
    """)
    
    st.markdown("### Integration Status")
    st.success("🟢 FinTech Data Feed Active")
    st.success("🟢 CRM Connected")

with col2:
    st.subheader("Agent Activity Feed")
    
    if selected_event:
        st.write(f"**Detected Event:** {selected_event.event_type} - {selected_event.description}")
        
        with st.spinner("Agent analysing risk profile and calculating pricing..."):
            try:
                # Run Agent
                initial_state = {
                    "customer": st.session_state.customer,
                    "event": selected_event,
                    "proposal": None,
                    "draft_message": ""
                }
                
                result = agent_graph.invoke(initial_state)
                proposal = result["proposal"]
                message = result["draft_message"]
                
                # Update Session Customer (Simulated)
                # In real app, we would wait for approval
                
                # Display Proposal
                st.markdown(f"### 💡 Recommendation: {proposal.recommended_action}")
                
                # Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Policy Type", proposal.policy_type)
                m2.metric("Premium Change", f"${proposal.premium_change:+.2f}")
                m3.metric("New Total", f"${proposal.new_total_premium:.2f}")
                
                st.write(f"**Reasoning:** {proposal.reasoning}")
                
                st.markdown("### 📧 Draft Communication")
                st.text_area("To Customer:", value=message, height=200)
                
                if st.button("Approve & Send"):
                    st.toast("Message sent to customer!", icon="🚀")
                    
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.write("Waiting for life events...")
        st.write("*(Use the sidebar to simulate an event)*")
