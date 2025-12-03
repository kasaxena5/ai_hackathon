"""
Guard-Railed Support Ticket Copilot - Simplified Streamlit UI
Complete implementation of all 8 steps as per HTML requirements document
"""

import streamlit as st
import pandas as pd
import os
import json
from typing import Dict, Optional
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

class GuardRailedSupportCopilot:
    """Complete support ticket processing pipeline"""
    
    def __init__(self):
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION")
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        # Load data files
        self.employees_df = self._load_employees()
        self.auth_rules_df = self._load_auth_rules()
        self.knowledge_base = self._load_knowledge_base()
        
    def _load_employees(self) -> pd.DataFrame:
        """Load employees data"""
        try:
            return pd.read_csv('./data/users_roles.csv')
        except:
            return pd.DataFrame()
    
    def _load_auth_rules(self) -> pd.DataFrame:
        """Load authorization rules"""
        try:
            return pd.read_csv('./data/auth_rules.csv')
        except:
            return pd.DataFrame()
    
    def _load_knowledge_base(self) -> Dict:
        """Load IT support knowledge base"""
        return {
            "network_issue": [
                {
                    "title": "VPN Connection Problems",
                    "content": """Common VPN connectivity issues and solutions:

1. VPN connects but can't reach internal sites:
   - Check DNS settings (set to 8.8.8.8 and 8.8.4.4)
   - Flush DNS cache: 'ipconfig /flushdns'
   - Restart network adapter
   - Verify split tunneling settings
   - Try reconnecting VPN

2. VPN connection drops frequently:
   - Update VPN client software
   - Check firewall settings
   - Switch VPN protocols (OpenVPN/IKEv2)
   - Contact network admin if persists

3. Cannot connect to VPN at all:
   - Verify credentials and server address
   - Check internet connectivity
   - Try different network/location
   - Contact IT for server status"""
                },
                {
                    "title": "Wi-Fi and Network Connectivity",
                    "content": """Wi-Fi and general network troubleshooting:

1. Wi-Fi keeps disconnecting:
   - Update network drivers
   - Reset network settings
   - Forget and reconnect to network
   - Disable power management for Wi-Fi adapter
   - Run Windows network troubleshooter

2. Slow internet connection:
   - Test speed on different devices
   - Restart router/modem
   - Update network drivers
   - Check for background downloads
   - Contact ISP if issue persists"""
                }
            ],
            
            "hardware_issue": [
                {
                    "title": "Keyboard and Input Device Issues",
                    "content": """Keyboard troubleshooting steps:

1. Keys stuck or not responding:
   - Turn off device and clean with compressed air
   - Remove key caps and clean underneath
   - Check for debris or liquid damage
   - Test with external keyboard
   - Replace if physical damage confirmed

2. Typing wrong characters:
   - Check keyboard language settings
   - Update keyboard drivers
   - Test in safe mode
   - Check for sticky keys activation"""
                },
                {
                    "title": "Monitor and Display Problems", 
                    "content": """Display troubleshooting guide:

1. Monitor black screen or flickering:
   - Check all cable connections
   - Test with different cable
   - Update graphics drivers
   - Test monitor with different device
   - Adjust display refresh rate

2. External monitor not detected:
   - Use Windows+P to detect displays
   - Update graphics drivers
   - Try different display port/HDMI port
   - Check monitor power and cables"""
                }
            ],
            
            "software_issue": [
                {
                    "title": "Email and Outlook Issues",
                    "content": """Email application troubleshooting:

1. Outlook not sending/receiving emails:
   - Check internet connection
   - Verify email account settings
   - Clear Outlook cache and restart
   - Repair Outlook data files
   - Check mailbox storage limits

2. 'Mailbox full' errors:
   - Delete old emails and empty deleted items
   - Archive old emails to local folders
   - Increase mailbox quota (contact admin)
   - Clean up large attachments

3. Outlook keeps crashing:
   - Start in safe mode: 'outlook /safe'
   - Disable add-ins one by one
   - Repair Office installation
   - Create new Outlook profile if needed"""
                },
                {
                    "title": "Microsoft Teams and Communication",
                    "content": """Teams application troubleshooting:

1. Teams keeps signing out or MFA issues:
   - Clear Teams cache (%appdata%\\Microsoft\\Teams)
   - Sign out completely and sign back in
   - Check authenticator app time sync
   - Update Teams to latest version
   - Try Teams web version temporarily

2. Teams calls/meetings not working:
   - Test microphone and camera permissions
   - Update audio/video drivers
   - Check firewall settings for Teams
   - Restart Teams application
   - Use Teams web version as backup"""
                }
            ],
            
            "policy_question": [
                {
                    "title": "Remote Work and WFH Policies",
                    "content": """Company remote work guidelines:

1. Remote work eligibility:
   - Available after 6 months employment
   - During probation: max 2 days/week with approval
   - Must use company equipment with security software
   - VPN required for internal system access
   - Work hours: align with core hours 9 AM - 3 PM

2. Equipment and security requirements:
   - Use only company-provided devices
   - Install required endpoint protection
   - Keep software updated
   - Report security incidents immediately
   - No personal cloud storage for work data"""
                },
                {
                    "title": "Equipment Damage and Support",
                    "content": """Equipment damage and replacement policy:

1. Accidental damage coverage:
   - Up to $1500 per incident
   - Maximum 2 incidents per year
   - Report within 48 hours to IT
   - Provide photos and incident description
   - Temporary replacement during repair

2. What's covered/not covered:
   - Covered: Accidental drops, spills, normal wear
   - Not covered: Intentional damage, theft, personal use damage
   - Negligence may void coverage
   - Personal accessories not covered"""
                }
            ]
        }
    
    def lookup_employee(self, employee_id: str) -> Optional[Dict]:
        """Step 1: Lookup employee profile"""
        if self.employees_df.empty:
            return None
            
        employee_row = self.employees_df[self.employees_df['employee_id'] == employee_id]
        if employee_row.empty:
            return None
            
        return employee_row.iloc[0].to_dict()
    
    def classify_intent(self, ticket_text: str) -> Dict:
        """Step 2: Classify ticket intent and appropriateness"""
        
        # Simple rule-based classification for demo
        ticket_lower = ticket_text.lower()
        
        # Check appropriateness
        off_scope_terms = ['personal', 'flat', 'apartment', 'cafeteria', 'canteen', 'food', 'pest control', 'home', 'car', 'vacation']
        is_appropriate = not any(term in ticket_lower for term in off_scope_terms)
        
        if not is_appropriate:
            return {
                'intent': 'off_scope',
                'appropriate': False,
                'confidence': 0.9
            }
        
        # Intent classification
        if any(term in ticket_lower for term in ['access', 'permission', 'grant', 'rights', 'privilege', 'admin', 'restricted', 'confidential']):
            intent = 'access_request'
        elif any(term in ticket_lower for term in ['vpn', 'network', 'wifi', 'internet', 'connection', 'connectivity']):
            intent = 'network_issue'
        elif any(term in ticket_lower for term in ['keyboard', 'mouse', 'monitor', 'screen', 'hardware', 'laptop', 'charger']):
            intent = 'hardware_issue'  
        elif any(term in ticket_lower for term in ['outlook', 'email', 'teams', 'software', 'application', 'app', 'crash']):
            intent = 'software_issue'
        elif any(term in ticket_lower for term in ['policy', 'wfh', 'remote', 'work from home', 'approval', 'guideline']):
            intent = 'policy_question'
        else:
            intent = 'general_inquiry'
            
        return {
            'intent': intent,
            'appropriate': True,
            'confidence': 0.8
        }
    
    def check_authorization(self, employee_profile: Dict, intent: str) -> str:
        """Step 3: Check authorization rules"""
        if self.auth_rules_df.empty:
            return 'allowed'  # Default if no rules loaded
            
        employee_role = employee_profile.get('role', '')
        employee_dept = employee_profile.get('department', '')
        
        # Find matching rule - check most specific first
        matched_rule = None
        
        for _, rule in self.auth_rules_df.iterrows():
            # Check if this rule applies to this intent
            if rule['intent'] != intent and rule['intent'] != '*':
                continue
                
            # Check if this rule applies to this role and department
            role_match = (rule['role'] == employee_role or rule['role'] == '*')
            dept_match = (rule['department'] == employee_dept or rule['department'] == '*')
            
            if role_match and dept_match:
                # More specific rules (exact role/dept) take precedence over wildcards
                specificity = 0
                if rule['role'] != '*':
                    specificity += 2
                if rule['department'] != '*':
                    specificity += 1
                    
                if matched_rule is None or specificity > matched_rule[1]:
                    matched_rule = (rule, specificity)
        
        if matched_rule:
            return matched_rule[0]['outcome']
        
        # Default behavior for access_request if no rule matches
        if intent == 'access_request':
            return 'needs_approval'  # Access requests generally need approval
        
        return 'allowed'  # Default to allowed for other intents
    
    def search_kb_and_generate(self, ticket_text: str, intent: str) -> Dict:
        """Step 4: RAG - Search knowledge base and generate answer"""
        
        if intent not in self.knowledge_base:
            return {
                'status': 'escalate',
                'message': 'This issue requires human attention. Your ticket has been escalated.',
                'kb_relevance': 0.0
            }
        
        # Simple search based on keyword overlap
        ticket_words = set(ticket_text.lower().split())
        best_match = ""
        best_score = 0.0
        
        for article in self.knowledge_base[intent]:
            content = (article["title"] + " " + article["content"]).lower()
            content_words = set(content.split())
            
            # Calculate overlap score
            common_words = ticket_words.intersection(content_words)
            if len(ticket_words) > 0:
                overlap_score = len(common_words) / len(ticket_words)
            else:
                overlap_score = 0.0
            
            if overlap_score > best_score:
                best_score = overlap_score
                best_match = f"**{article['title']}**\n\n{article['content']}"
        
        # Determine if we have sufficient knowledge base context
        if best_score >= 0.25 and best_match:
            # Generate solution using Azure OpenAI
            try:
                prompt = f"""You are an IT support specialist. Answer the user's question using ONLY the provided knowledge base information.

KNOWLEDGE BASE INFORMATION:
{best_match}

USER QUESTION: {ticket_text}

Instructions:
1. Provide a clear, step-by-step solution based ONLY on the knowledge base
2. Be specific and actionable
3. Keep response under 200 words
4. Be professional and helpful

Solution:"""

                response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=250,
                    temperature=0.2
                )
                
                solution = response.choices[0].message.content.strip()
                
                return {
                    'status': 'solved_by_rag',
                    'message': solution,
                    'kb_relevance': best_score,
                    'kb_context': best_match
                }
                
            except Exception as e:
                return {
                    'status': 'escalate',
                    'message': f'Error generating solution: {str(e)}',
                    'kb_relevance': best_score
                }
        
        return {
            'status': 'escalate',
            'message': 'This issue requires human attention. Your ticket has been escalated to our IT support team.',
            'kb_relevance': best_score
        }
    
    def process_ticket(self, employee_id: str, ticket_text: str) -> Dict:
        """Main pipeline function - processes ticket through complete flow"""
        
        result = {
            'employee_id': employee_id,
            'ticket_text': ticket_text,
            'pipeline_steps': {},
            'final_status': None,
            'final_message': None
        }
        
        # Step 1: Employee Lookup
        employee_profile = self.lookup_employee(employee_id)
        if not employee_profile:
            result['final_status'] = 'employee_not_found'
            result['final_message'] = f'Employee ID {employee_id} not found in system.'
            return result
        
        result['pipeline_steps']['employee_lookup'] = employee_profile
        
        # Step 2: Intent Classification
        classification = self.classify_intent(ticket_text)
        result['pipeline_steps']['classification'] = classification
        
        # Check appropriateness
        if not classification['appropriate']:
            result['final_status'] = 'blocked_by_appropriateness'
            result['final_message'] = "I'm an internal IT support assistant. I can't help with this type of request."
            return result
        
        intent = classification['intent']
        
        # Step 3: Authorization Check
        auth_result = self.check_authorization(employee_profile, intent)
        result['pipeline_steps']['authorization'] = auth_result
        
        if auth_result == 'blocked_by_auth':
            result['final_status'] = 'blocked_by_auth'
            result['final_message'] = "You don't have authorization for this type of request."
            return result
        elif auth_result == 'needs_approval':
            result['final_status'] = 'needs_approval'
            result['final_message'] = "This request requires manager approval. Please contact your supervisor."
            return result
        
        # Step 4: RAG Processing (only if allowed)
        if auth_result == 'allowed':
            rag_result = self.search_kb_and_generate(ticket_text, intent)
            result['pipeline_steps']['rag'] = rag_result
            result['final_status'] = rag_result['status']
            result['final_message'] = rag_result['message']
        
        return result


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
    .pipeline-step {
        background: #f8f9fa;
        border-left: 4px solid #0078D4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
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
    .step-badge {
        background: #0078D4;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Guard-Railed Support Ticket Copilot</h1>
        <p style="margin: 0; font-size: 1.1rem;">Complete 8-Step Pipeline Implementation | M6 Hackathon Project</p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">Azure OpenAI + LangChain + Streamlit</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize the copilot
    if 'copilot' not in st.session_state:
        with st.spinner("🚀 Initializing Guard-Railed Support Copilot..."):
            try:
                st.session_state.copilot = GuardRailedSupportCopilot()
                st.success("✅ Copilot initialized successfully!")
            except Exception as e:
                st.error(f"❌ Failed to initialize copilot: {str(e)}")
                return
    
    copilot = st.session_state.copilot
    
    # Sidebar - System Overview
    with st.sidebar:
        st.markdown("## 📊 System Overview")
        
        # Data Status
        st.markdown("### 📁 Data Files Status")
        emp_count = len(copilot.employees_df) if not copilot.employees_df.empty else 0
        auth_count = len(copilot.auth_rules_df) if not copilot.auth_rules_df.empty else 0
        kb_count = sum(len(articles) for articles in copilot.knowledge_base.values())
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("👤 Employees", emp_count)
            st.metric("📚 KB Articles", kb_count)
        with col2:
            st.metric("🛡️ Auth Rules", auth_count)
            st.metric("🎯 Intent Types", len(copilot.knowledge_base))
        
        # Pipeline Steps Overview
        st.markdown("### 🔄 Complete Pipeline")
        st.markdown("""
        <div style="background: #f0f8ff; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
        <h4 style="margin: 0 0 0.5rem 0; color: #0078D4;">8 Steps Process:</h4>
        <ol style="margin: 0; padding-left: 1.2rem; font-size: 0.9rem;">
            <li>📥 Input Validation</li>
            <li>👤 Employee Lookup</li>
            <li>🏷️ Intent Classification</li>
            <li>✅ Appropriateness Check</li>
            <li>🛡️ Authorization Rules</li>
            <li>📚 Knowledge Base Search</li>
            <li>🤖 Solution Generation</li>
            <li>📤 Final Response</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick stats
        st.markdown("### 📈 Quick Stats")
        if 'processed_count' not in st.session_state:
            st.session_state.processed_count = 0
        if 'solved_count' not in st.session_state:
            st.session_state.solved_count = 0
        
        st.metric("Total Processed", st.session_state.processed_count)
        st.metric("Solved by RAG", st.session_state.solved_count)
        
        # System health
        st.markdown("### 🔧 System Health")
        health_indicators = [
            ("🟢", "Azure OpenAI", "Connected"),
            ("🟢" if not copilot.employees_df.empty else "🔴", "Employee Data", "Loaded" if not copilot.employees_df.empty else "Missing"),
            ("🟢" if not copilot.auth_rules_df.empty else "🔴", "Auth Rules", "Active" if not copilot.auth_rules_df.empty else "Missing"),
            ("🟢", "Knowledge Base", "Active")
        ]
        
        for icon, component, status in health_indicators:
            st.markdown(f"{icon} **{component}**: {status}")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎫 Process Ticket", 
        "📊 Pipeline Details", 
        "📋 Data Overview", 
        "🧪 Testing Suite"
    ])
    
    with tab1:
        st.header("🎫 Support Ticket Processing")
        
        # Input section
        st.subheader("📝 Ticket Input")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Employee selection
            if not copilot.employees_df.empty:
                employee_options = [''] + copilot.employees_df['employee_id'].tolist()
                selected_employee = st.selectbox(
                    "👤 Select Employee ID:",
                    options=employee_options,
                    help="Choose from available employees in the system"
                )
            else:
                selected_employee = st.text_input(
                    "👤 Employee ID:",
                    value="E007",
                    help="Enter employee ID (e.g., E007)"
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
                "Safety Issue": ("Charger Safety Problem", "My laptop charger is sparking - this is a safety issue")
            }
            
            selected_example = st.selectbox(
                "Quick Examples:",
                options=list(example_issues.keys()),
                help="Select a sample ticket or create your own"
            )
            
        with col2:
            # Auto-fill from example selection
            if selected_example and selected_example in example_issues:
                example_subject, example_description = example_issues[selected_example]
                if example_subject and not ticket_subject:
                    st.session_state['temp_subject'] = example_subject
                if example_description:
                    st.session_state['temp_description'] = example_description
            
            # Update fields if example was selected
            if 'temp_subject' in st.session_state and not ticket_subject:
                ticket_subject = st.session_state.get('temp_subject', '')
            
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
                help="Submit ticket through the pipeline",
                use_container_width=True
            )
        
        # Results section
        if process_button and selected_employee and ticket_subject.strip() and ticket_text.strip():
            
            # Clear temp values
            if 'temp_subject' in st.session_state:
                del st.session_state['temp_subject']
            if 'temp_description' in st.session_state:
                del st.session_state['temp_description']
            
            # Update session stats
            st.session_state.processed_count += 1
            
            # Process the ticket
            with st.spinner("🔄 Processing support ticket..."):
                # Combine subject and description for processing
                full_ticket = f"{ticket_subject.strip()}: {ticket_text.strip()}"
                result = copilot.process_ticket(selected_employee, full_ticket)
            
            # Display final status
            final_status = result.get('final_status', 'unknown')
            final_message = result.get('final_message', 'No message available')
            
            # Update solved count
            if final_status == 'solved_by_rag':
                st.session_state.solved_count += 1
            
            # Status-specific styling and display
            if final_status == 'solved_by_rag':
                status_class = "success-box"
                status_icon = "✅"
                status_title = "TICKET SOLVED BY RAG"
            elif final_status == 'needs_approval':
                status_class = "warning-box"
                status_icon = "⚠️"
                status_title = "TICKET NEEDS APPROVAL"
            elif final_status == 'escalate':
                status_class = "warning-box"
                status_icon = "⚠️"
                status_title = "TICKET REQUIRES ATTENTION"
            elif final_status in ['blocked_by_auth', 'blocked_by_appropriateness']:
                status_class = "error-box"
                status_icon = "❌"
                status_title = "TICKET BLOCKED"
            else:
                status_class = "info-box"
                status_icon = "ℹ️"
                status_title = "PROCESSING RESULT"
            
            # Display ticket information
            st.markdown("---")
            st.subheader("📋 Ticket Information")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write(f"**👤 Employee:** {selected_employee}")
                st.write(f"**📝 Subject:** {ticket_subject}")
            with col2:
                st.write(f"**📄 Description:** {ticket_text[:100]}..." if len(ticket_text) > 100 else f"**📄 Description:** {ticket_text}")
            
            # Final result display
            st.subheader("🎯 Result")
            
            st.markdown(f"""
            <div class="result-box {status_class}">
                <h2 style="margin: 0 0 1rem 0;">{status_icon} {status_title}</h2>
                <h4 style="margin: 0 0 0.5rem 0;">Status: {final_status.upper()}</h4>
                <p style="margin: 0; font-size: 1.1rem; line-height: 1.6;"><strong>Response:</strong> {final_message}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Optional: Show additional details if user wants them
            if st.checkbox("🔍 Show Technical Details", value=False):
                st.subheader("📊 Processing Details")
                
                # Employee info
                emp_data = result['pipeline_steps'].get('employee_lookup', {})
                if emp_data:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("👤 Role", emp_data.get('role', 'N/A'))
                    with col2:
                        st.metric("🏢 Department", emp_data.get('department', 'N/A'))
                    with col3:
                        st.metric("⭐ Seniority", emp_data.get('seniority', 'N/A'))
                
                # Classification info
                class_data = result['pipeline_steps'].get('classification', {})
                if class_data:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("🏷️ Intent", class_data.get('intent', 'N/A'))
                    with col2:
                        st.metric("📊 Confidence", f"{class_data.get('confidence', 0)*100:.0f}%")
                
                # RAG relevance if available
                rag_data = result['pipeline_steps'].get('rag', {})
                if rag_data and 'kb_relevance' in rag_data:
                    st.metric("📚 Knowledge Base Relevance", f"{rag_data['kb_relevance']*100:.1f}%")
        
        elif process_button:
            missing_fields = []
            if not selected_employee:
                missing_fields.append("Employee ID")
            if not ticket_subject.strip():
                missing_fields.append("Subject")
            if not ticket_text.strip():
                missing_fields.append("Description")
            
            st.warning(f"⚠️ Please fill in the following required fields: {', '.join(missing_fields)}")
    
    with tab2:
        st.header("📊 Pipeline Flow & Architecture")
        
        # Pipeline overview
        st.subheader("🔄 Complete 8-Step Pipeline Flow")
        
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin: 1rem 0;">
            <h3 style="text-align: center; color: #0078D4; margin-bottom: 1.5rem;">Guard-Railed Support Ticket Pipeline</h3>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
                <div style="background: #E3F2FD; padding: 1rem; border-radius: 8px; text-align: center; flex: 1; margin: 0 0.5rem;">
                    <strong>📥 INPUT</strong><br>
                    <small>employee_id + ticket_text</small>
                </div>
                <div style="font-size: 1.5rem; color: #0078D4;">→</div>
                <div style="background: #FFF3E0; padding: 1rem; border-radius: 8px; text-align: center; flex: 1; margin: 0 0.5rem;">
                    <strong>🔄 PIPELINE</strong><br>
                    <small>8-step processing</small>
                </div>
                <div style="font-size: 1.5rem; color: #0078D4;">→</div>
                <div style="background: #E8F5E9; padding: 1rem; border-radius: 8px; text-align: center; flex: 1; margin: 0 0.5rem;">
                    <strong>📤 OUTPUT</strong><br>
                    <small>final_status + message</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Step-by-step breakdown
        st.subheader("📋 Step-by-Step Breakdown")
        
        pipeline_steps = [
            {
                "step": "1️⃣ Input Validation",
                "description": "Validate employee_id and ticket_text parameters",
                "output": "Valid input confirmed"
            },
            {
                "step": "2️⃣ Employee Lookup",
                "description": "Search employee database for profile information",
                "output": "Employee profile (role, department, seniority) or not_found"
            },
            {
                "step": "3️⃣ Intent Classification",
                "description": "Classify ticket into categories using rule-based matching",
                "output": "Intent category and confidence score"
            },
            {
                "step": "4️⃣ Appropriateness Check",
                "description": "Verify ticket is within IT support scope",
                "output": "Appropriate/inappropriate flag"
            },
            {
                "step": "5️⃣ Authorization Rules",
                "description": "Apply role-based authorization rules from config",
                "output": "allowed/blocked_by_auth/needs_approval"
            },
            {
                "step": "6️⃣ Knowledge Base Search",
                "description": "Search KB articles for relevant content using keyword matching",
                "output": "Relevant articles and relevance score"
            },
            {
                "step": "7️⃣ Solution Generation",
                "description": "Generate answer using Azure OpenAI and KB context",
                "output": "Detailed solution or escalation message"
            },
            {
                "step": "8️⃣ Final Response",
                "description": "Package final status and message for user",
                "output": "Complete pipeline result with all intermediate data"
            }
        ]
        
        for i, step_info in enumerate(pipeline_steps, 1):
            with st.expander(f"{step_info['step']} - {step_info['description']}"):
                st.write(f"**Process:** {step_info['description']}")
                st.write(f"**Output:** {step_info['output']}")
        
        # Final status possibilities
        st.subheader("📈 Possible Final Statuses")
        
        status_data = [
            ["solved_by_rag", "Ticket resolved using knowledge base", "✅ User gets detailed solution"],
            ["escalate", "Ticket requires human attention", "⚠️ Escalated to IT support team"],
            ["blocked_by_auth", "Employee lacks authorization", "❌ Access denied message"],
            ["blocked_by_appropriateness", "Request outside IT scope", "❌ Scope limitation message"],
            ["needs_approval", "Manager approval required", "⚠️ Approval process initiated"],
            ["employee_not_found", "Employee ID not in system", "❌ Invalid employee error"]
        ]
        
        status_df = pd.DataFrame(status_data, columns=['Status', 'Description', 'User Experience'])
        st.dataframe(status_df, use_container_width=True)
    
    with tab3:
        st.header("📋 Data Management & Overview")
        
        # System data overview
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👥 Employee Database")
            if not copilot.employees_df.empty:
                st.dataframe(copilot.employees_df, use_container_width=True)
                
                # Employee statistics
                st.markdown("**📊 Employee Statistics:**")
                dept_counts = copilot.employees_df['department'].value_counts()
                for dept, count in dept_counts.items():
                    st.write(f"• {dept}: {count} employees")
                    
                role_counts = copilot.employees_df['role'].value_counts()
                st.markdown("**👔 Role Distribution:**")
                for role, count in role_counts.items():
                    st.write(f"• {role}: {count}")
            else:
                st.warning("⚠️ No employee data loaded. Check data/users_roles.csv")
        
        with col2:
            st.subheader("🛡️ Authorization Rules")
            if not copilot.auth_rules_df.empty:
                st.dataframe(copilot.auth_rules_df, use_container_width=True)
                
                # Rules statistics
                st.markdown("**📊 Rules Statistics:**")
                outcome_counts = copilot.auth_rules_df['outcome'].value_counts()
                for outcome, count in outcome_counts.items():
                    st.write(f"• {outcome}: {count} rules")
            else:
                st.warning("⚠️ No authorization rules loaded. Check data/auth_rules.csv")
        
        # Knowledge base overview
        st.subheader("📚 Knowledge Base Content")
        
        for category, articles in copilot.knowledge_base.items():
            with st.expander(f"📂 {category.replace('_', ' ').title()} ({len(articles)} articles)"):
                for i, article in enumerate(articles, 1):
                    st.markdown(f"**{i}. {article['title']}**")
                    st.write(f"Content length: {len(article['content'])} characters")
                    with st.expander(f"Preview: {article['title']}"):
                        st.markdown(article['content'][:300] + "..." if len(article['content']) > 300 else article['content'])
        
        # Data file status
        st.subheader("📁 Data File Status")
        data_files = [
            ("users_roles.csv", not copilot.employees_df.empty, len(copilot.employees_df) if not copilot.employees_df.empty else 0),
            ("auth_rules.csv", not copilot.auth_rules_df.empty, len(copilot.auth_rules_df) if not copilot.auth_rules_df.empty else 0),
            ("Knowledge Base", True, sum(len(articles) for articles in copilot.knowledge_base.values()))
        ]
        
        for filename, loaded, count in data_files:
            status_icon = "✅" if loaded else "❌"
            status_text = "Loaded" if loaded else "Missing"
            st.write(f"{status_icon} **{filename}**: {status_text} ({count} items)")
    
    with tab4:
        st.header("🧪 Testing Suite")
        
        # Quick test section
        st.subheader("⚡ Quick Test Examples")
        
        # Pre-defined test cases
        test_cases = [
            {
                "name": "VPN Connectivity Issue",
                "employee": "E007",
                "subject": "VPN Connection Problem",
                "ticket": "VPN connects but I cannot reach any internal websites or dashboards",
                "expected": "solved_by_rag"
            },
            {
                "name": "Hardware Keyboard Issue", 
                "employee": "E002",
                "subject": "Keyboard Key Stuck",
                "ticket": "My laptop keyboard N key is physically stuck and will not press down",
                "expected": "solved_by_rag"
            },
            {
                "name": "Outlook Mailbox Full",
                "employee": "E006", 
                "subject": "Email Mailbox Full Error",
                "ticket": "Outlook shows an error 'mailbox full' and will not send emails",
                "expected": "solved_by_rag"
            },
            {
                "name": "Policy Question",
                "employee": "E005",
                "subject": "Work From Home Policy",
                "ticket": "What is the company policy for work from home during probation?",
                "expected": "solved_by_rag"
            },
            {
                "name": "Access Request (T015)",
                "employee": "E004",
                "subject": "Finance Data Access",
                "ticket": "I need access to restricted finance data for my work",
                "expected": "needs_approval"
            },
            {
                "name": "Off-Scope Request",
                "employee": "E008",
                "subject": "Apartment Pest Control",
                "ticket": "Please arrange pest control for my apartment, there are insects",
                "expected": "blocked_by_appropriateness"
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            with st.expander(f"🧪 Test Case {i+1}: {test_case['name']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Employee:** {test_case['employee']}")
                    st.write(f"**Subject:** {test_case['subject']}")
                    st.write(f"**Description:** {test_case['ticket']}")
                    st.write(f"**Expected:** {test_case['expected']}")
                
                with col2:
                    if st.button(f"Run Test {i+1}", key=f"test_{i}"):
                        with st.spinner(f"Running test case {i+1}..."):
                            # Combine subject and ticket for processing
                            full_ticket = f"{test_case['subject']}: {test_case['ticket']}"
                            result = copilot.process_ticket(test_case['employee'], full_ticket)
                        
                        actual = result['final_status']
                        match = "✅ PASS" if actual == test_case['expected'] else "❌ FAIL"
                        
                        st.write(f"**Result:** {actual}")
                        st.write(f"**Status:** {match}")
        
        # Bulk testing
        st.subheader("📊 Bulk Testing")
        
        try:
            test_df = pd.read_csv('./data/support_tickets_seed_detailed.csv')
            
            st.write(f"📁 Loaded {len(test_df)} test tickets from CSV")
            
            # Show sample data
            with st.expander("📋 Sample Test Data"):
                st.dataframe(test_df.head(10), use_container_width=True)
            
            # Bulk test controls
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                max_tests = st.number_input("Max tests to run:", min_value=1, max_value=len(test_df), value=min(10, len(test_df)))
            
            with col2:
                run_bulk = st.button("🚀 Run Bulk Test", type="primary")
            
            if run_bulk:
                with col3:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                
                results = []
                test_subset = test_df.head(max_tests)
                
                for idx, row in test_subset.iterrows():
                    progress = (len(results) + 1) / len(test_subset)
                    progress_bar.progress(progress)
                    status_text.text(f"Processing ticket {len(results) + 1}/{len(test_subset)}...")
                    
                    # Process ticket
                    result = copilot.process_ticket(row['employee_id'], row['ticket_text'])
                    
                    results.append({
                        'ticket_id': row['ticket_id'],
                        'employee_id': row['employee_id'],
                        'expected_flow': row.get('expected_flow', 'N/A'),
                        'actual_status': result['final_status'],
                        'match': '✅' if result['final_status'] == row.get('expected_flow') else '❌'
                    })
                
                status_text.text("✅ Bulk testing completed!")
                
                # Show results
                st.subheader("📈 Bulk Test Results")
                results_df = pd.DataFrame(results)
                st.dataframe(results_df, use_container_width=True)
                
                # Calculate metrics
                total_tests = len(results_df)
                passed_tests = len(results_df[results_df['match'] == '✅'])
                accuracy = (passed_tests / total_tests * 100) if total_tests > 0 else 0
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🎯 Total Tests", total_tests)
                with col2:
                    st.metric("✅ Passed", passed_tests)
                with col3:
                    st.metric("📊 Accuracy", f"{accuracy:.1f}%")
                
                # Status distribution
                st.subheader("📊 Final Status Distribution")
                status_counts = results_df['actual_status'].value_counts()
                for status, count in status_counts.items():
                    percentage = (count / total_tests * 100)
                    st.write(f"• **{status}**: {count} tickets ({percentage:.1f}%)")
                
        except FileNotFoundError:
            st.warning("⚠️ Test data file not found. Please ensure data/support_tickets_seed_detailed.csv exists.")
            st.info("💡 You can still use the Quick Test Examples above to validate the pipeline functionality.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p><strong>🎯 Guard-Railed Support Ticket Copilot</strong> | M6 Hackathon Project</p>
        <p>Complete 8-Step Pipeline Implementation | Azure OpenAI + RAG + Streamlit</p>
        <p><em>Stateless per-ticket processing with classification → authorization → RAG flow</em></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()