"""
Guard-Railed Support Ticket Copilot - Streamlit UI Client
Frontend interface that calls the FastAPI backend for ticket processing
"""

import streamlit as st
import pandas as pd
import requests
import json
from typing import Dict, Optional

# Configuration
FASTAPI_BASE_URL = "http://localhost:8000"

class SupportTicketClient:
    """Client to interact with FastAPI backend"""
    
    def __init__(self):
        # Load data files for UI display purposes
        self.employees_df = self._load_employees()
        
    def _load_employees(self) -> pd.DataFrame:
        """Load employees data for UI purposes"""
        try:
            return pd.read_csv('./data/users_roles.csv')
        except:
            return pd.DataFrame()
    
    def process_ticket_via_api(self, employee_id: str, subject: str, body: str) -> Dict:
        """Call FastAPI endpoint to process ticket"""
        try:
            # Prepare request payload
            payload = {
                "employee_id": employee_id,
                "subject": subject,
                "body": body
            }
            
            # Make API call
            response = requests.post(
                f"{FASTAPI_BASE_URL}/tickets/process",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                api_response = response.json()
                return {
                    'success': True,
                    'outcome': api_response.get('outcome', 'unknown'),
                    'response': api_response.get('response', 'No response available')
                }
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else 'Server error'
                return {
                    'success': False,
                    'error': f"API Error ({response.status_code}): {error_detail}"
                }
                
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': "Cannot connect to FastAPI server. Please ensure the server is running on http://localhost:8000"
            }
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': "Request timeout. The server took too long to respond."
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }
    
    def check_api_health(self) -> bool:
        """Check if FastAPI server is running"""
        try:
            response = requests.get(f"{FASTAPI_BASE_URL}/health", timeout=5)
            return response.status_code == 200
        except:
            return False


def main():
    """Main Streamlit application"""
    
    # Page configuration
    st.set_page_config(
        page_title="Guard-Railed Support Ticket Copilot",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #0078D4 0%, #0063B1 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,120,212,0.3);
    }
    .result-box {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .success-box {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border-left: 4px solid #4CAF50;
        color: #2E7D32;
    }
    .warning-box {
        background: linear-gradient(135deg, #FFF9E6 0%, #FFF3D6 100%);
        border-left: 4px solid #FF8C00;
        color: #E65100;
    }
    .error-box {
        background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
        border-left: 4px solid #F44336;
        color: #C62828;
    }
    .info-box {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        border-left: 4px solid #2196F3;
        color: #1565C0;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Guard-Railed Support Ticket Copilot</h1>
        <p style="margin: 0; font-size: 1.1rem;">FastAPI Backend + Streamlit Frontend | M6 Hackathon Project</p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">Complete Guard-Railed Pipeline Processing</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize the client
    if 'client' not in st.session_state:
        with st.spinner("🚀 Initializing Support Ticket Client..."):
            try:
                st.session_state.client = SupportTicketClient()
                st.session_state.initialization_success = True
            except Exception as e:
                st.session_state.initialization_success = False
                st.session_state.initialization_error = str(e)
    
    client = st.session_state.client
    
    # Check API health
    api_healthy = client.check_api_health()
    
    # Sidebar - System Status
    with st.sidebar:
        st.markdown("## 📊 System Status")
        
        # API Status
        if api_healthy:
            st.markdown("🟢 **FastAPI Backend**: ✅ Connected")
        else:
            st.markdown("🔴 **FastAPI Backend**: ❌ Disconnected")
            st.warning("⚠️ FastAPI server is not running. Please start it using: `uvicorn main:app --reload`")
        
        # Data Status
        st.markdown("### 📁 Data Status")
        emp_count = len(client.employees_df) if not client.employees_df.empty else 0
        st.metric("👤 Employees Loaded", emp_count)
        
        # System health indicators
        st.markdown("### 🔧 System Health")
        health_indicators = [
            ("🟢" if api_healthy else "🔴", "FastAPI Backend", "Connected" if api_healthy else "Disconnected"),
            ("🟢" if not client.employees_df.empty else "🔴", "Employee Data", "Loaded" if not client.employees_df.empty else "Missing"),
        ]
        
        for icon, component, status in health_indicators:
            st.markdown(f"{icon} **{component}**: {status}")
        
        # Instructions
        st.markdown("### 📋 Instructions")
        st.info("""
        **To use this application:**
        
        1. Start the FastAPI server:
        ```bash
        uvicorn main:app --reload
        ```
        
        2. Select an employee ID
        3. Enter ticket details
        4. Click "Process Support Ticket"
        
        The UI will call the FastAPI backend which processes the ticket through the complete guard-railed pipeline.
        """)
    
    # Main content
    st.header("🎫 Support Ticket Processing")
    
    if not api_healthy:
        st.error("❌ **Cannot connect to FastAPI backend!** Please start the server first.")
        st.code("uvicorn main:app --reload", language="bash")
        return
    
    # Input section
    st.subheader("📝 Ticket Input")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Employee selection
        if not client.employees_df.empty:
            employee_options = [''] + client.employees_df['employee_id'].tolist()
            selected_employee = st.selectbox(
                "👤 Select Employee ID:",
                options=employee_options,
                help="Choose the employee submitting the ticket"
            )
        else:
            selected_employee = st.text_input(
                "👤 Employee ID:",
                placeholder="Enter employee ID (e.g., E007)",
                help="Employee ID not available - enter manually"
            )
        
        # Subject field
        ticket_subject = st.text_input(
            "📝 Subject:",
            placeholder="Brief description of the issue...",
            help="Enter a short subject line for the ticket"
        )
        
        # Example tickets
        st.markdown("**💡 Example Issues:**")
        example_issues = {
            "": ("", ""),
            "VPN Connectivity Issue": ("VPN Connection Problem", "VPN connects but I cannot reach internal websites or dashboards"),
            "Hardware Keyboard Issue": ("Keyboard Key Stuck", "My laptop keyboard N key is physically stuck and won't press down"),
            "Email Mailbox Full": ("Outlook Mailbox Full Error", "Outlook shows mailbox full error and won't send emails"),
            "WFH Policy Question": ("Work From Home Policy", "What is the company policy for work from home during probation?"),
            "Access Request": ("Finance Data Access", "I need access to restricted finance data for my work"),
            "Off-Scope Request": ("Apartment Pest Control", "Please arrange pest control for my apartment, there are insects")
        }
        
        selected_example = st.selectbox(
            "Quick Examples:",
            options=list(example_issues.keys()),
            help="Select a sample ticket or create your own"
        )
        
    with col2:
        # Auto-fill from example selection
        if selected_example and selected_example in example_issues:
            st.session_state.temp_subject = example_issues[selected_example][0]
            st.session_state.temp_description = example_issues[selected_example][1]
        
        # Update fields if example was selected
        if 'temp_subject' in st.session_state and not ticket_subject:
            ticket_subject = st.session_state.temp_subject
        
        initial_text = st.session_state.get('temp_description', '') if selected_example else ""
        
        # Ticket text input
        ticket_text = st.text_area(
            "📝 Detailed Description:",
            value=initial_text,
            placeholder="Describe your IT support issue in detail...",
            height=150,
            help="Enter a detailed description of the issue"
        )
        
        # Process button
        process_button = st.button(
            "🚀 Process Support Ticket",
            type="primary",
            use_container_width=True,
            disabled=not api_healthy
        )
    
    # Results section
    if process_button and selected_employee and ticket_subject.strip() and ticket_text.strip():
        
        with st.spinner("🔄 Processing ticket through FastAPI backend..."):
            
            # Call FastAPI backend
            result = client.process_ticket_via_api(selected_employee, ticket_subject, ticket_text)
            
            if result['success']:
                # Success - display results
                outcome = result['outcome']
                response_message = result['response']
                
                # Display outcome with appropriate styling
                if outcome == 'solved_by_rag':
                    st.markdown(f"""
                    <div class="result-box success-box">
                        <h3>✅ Ticket Resolved</h3>
                        <p><strong>Status:</strong> {outcome}</p>
                        <p><strong>Solution:</strong></p>
                        <p>{response_message}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                elif outcome in ['blocked_by_auth', 'blocked_by_appropriateness']:
                    st.markdown(f"""
                    <div class="result-box error-box">
                        <h3>❌ Request Blocked</h3>
                        <p><strong>Status:</strong> {outcome}</p>
                        <p><strong>Reason:</strong> {response_message}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                elif outcome == 'needs_approval':
                    st.markdown(f"""
                    <div class="result-box warning-box">
                        <h3>⚠️ Approval Required</h3>
                        <p><strong>Status:</strong> {outcome}</p>
                        <p><strong>Action Required:</strong> {response_message}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                elif outcome == 'escalate':
                    st.markdown(f"""
                    <div class="result-box info-box">
                        <h3>📢 Escalated to IT Team</h3>
                        <p><strong>Status:</strong> {outcome}</p>
                        <p><strong>Next Steps:</strong> {response_message}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                else:
                    st.markdown(f"""
                    <div class="result-box info-box">
                        <h3>📋 Ticket Processed</h3>
                        <p><strong>Status:</strong> {outcome}</p>
                        <p><strong>Response:</strong> {response_message}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Display request details
                with st.expander("📄 Request Details"):
                    st.write(f"**Employee ID:** {selected_employee}")
                    st.write(f"**Subject:** {ticket_subject}")
                    st.write(f"**Description:** {ticket_text}")
                
            else:
                # Error occurred
                st.markdown(f"""
                <div class="result-box error-box">
                    <h3>❌ Processing Error</h3>
                    <p><strong>Error:</strong> {result['error']}</p>
                    <p>Please check the FastAPI server logs for more details.</p>
                </div>
                """, unsafe_allow_html=True)
        
    elif process_button:
        st.warning("⚠️ Please fill in all required fields: Employee ID, Subject, and Description")
    
    # API Documentation section
    st.header("📖 API Integration Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔌 FastAPI Endpoint")
        st.code(f"""
POST {FASTAPI_BASE_URL}/tickets/process

Request Body:
{{
    "employee_id": "E007",
    "subject": "VPN Issue", 
    "body": "Cannot connect to VPN"
}}

Response:
{{
    "outcome": "solved_by_rag",
    "response": "Here's how to fix your VPN..."
}}
        """, language="json")
    
    with col2:
        st.subheader("🔄 Processing Flow")
        st.markdown("""
        **Complete Pipeline Steps:**
        
        1. 📥 **Input Validation** - Validate request data
        2. 👤 **Employee Lookup** - Find employee profile  
        3. 🏷️ **Intent Classification** - Categorize the issue
        4. ✅ **Appropriateness Check** - Verify IT scope
        5. 🛡️ **Authorization Rules** - Check permissions
        6. 📚 **Knowledge Base Search** - Find relevant info
        7. 🤖 **Solution Generation** - Generate response
        8. 📤 **Final Response** - Return result to UI
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p><strong>🎯 Guard-Railed Support Ticket Copilot</strong> | M6 Hackathon Project</p>
        <p>FastAPI Backend + Streamlit Frontend | Complete Guard-Railed Pipeline</p>
        <p><em>Backend processes tickets through: Classification → Authorization → RAG → Response</em></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()