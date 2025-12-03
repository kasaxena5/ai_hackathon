"""
RAG System for Guard-Railed Support Ticket Copilot
Follows the flowchart: Takes allowed tickets and returns solved_by_rag or escalate
"""
import os
from typing import Dict, List, Tuple
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

class SupportTicketRAG:
    """
    RAG system that processes allowed tickets and determines if they can be solved
    Returns: solved_by_rag (if answerable from KB) or escalate (if no good KB context)
    """
    
    def __init__(self):
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION")
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        # Knowledge base organized by intent category
        self.knowledge_base = self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> Dict[str, List[Dict]]:
        """Load the IT support knowledge base"""
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
   - Contact ISP if issue persists

3. Cannot access specific websites:
   - Clear browser cache and cookies
   - Try different browser or incognito mode
   - Check DNS settings
   - Disable browser extensions temporarily"""
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
   - Check for sticky keys activation

3. Laptop trackpad not working:
   - Check touchpad settings in Windows
   - Update touchpad drivers
   - Clean touchpad surface
   - Try external mouse as backup"""
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
   - Check monitor power and cables

3. Screen resolution or scaling issues:
   - Right-click desktop > Display settings
   - Adjust resolution and scaling
   - Update graphics drivers
   - Check manufacturer recommended settings"""
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
   - Use Teams web version as backup

3. Teams notifications not working:
   - Check Windows notification settings
   - Review Teams notification preferences
   - Ensure Teams is allowed through firewall
   - Restart Windows notification service"""
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
   - No personal cloud storage for work data

3. Communication and availability:
   - Respond to messages within 4 hours
   - Attend required meetings via video
   - Update calendar with availability
   - Manager check-ins as scheduled"""
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
   - Personal accessories not covered

3. Replacement process:
   - Submit damage report form
   - IT assessment within 2 business days
   - Repair vs replacement decision
   - Temporary equipment if needed
   - Return damaged equipment when replaced"""
                }
            ],
            
            "off_scope": [
                {
                    "title": "Non-IT Related Requests",
                    "content": """Guidance for requests outside IT support scope:

1. HR and Personnel Issues:
   - Contact HR directly for policy questions
   - Benefits inquiries: use employee portal
   - Time off requests: submit through manager
   - Performance reviews: discuss with supervisor
   - Workplace conflicts: escalate to HR

2. Facilities and Physical Workspace:
   - Building access issues: contact security
   - HVAC problems: submit facilities request
   - Parking permits: contact building management
   - Office supplies: order through procurement
   - Furniture requests: submit facilities ticket

3. Finance and Procurement:
   - Expense reports: use finance portal
   - Purchase requests: follow procurement process
   - Budget questions: contact finance team
   - Vendor payments: accounts payable department
   - Credit card issues: contact finance

4. External Services and Personal Matters:
   - Personal device issues: contact manufacturer
   - Personal email problems: not supported
   - Home internet issues: contact your ISP
   - Personal software: purchase/support yourself
   - Non-work applications: not IT supported

For these types of requests, IT cannot provide assistance. Please contact the appropriate department directly."""
                }
            ],
            
            "access_request": [
                {
                    "title": "Standard Access Request Process",
                    "content": """Access request procedures and guidelines:

1. Application and System Access:
   - Submit access request form through IT portal
   - Include business justification
   - Manager approval required for all requests
   - Allow 2-3 business days for processing
   - Temporary access available for urgent needs

2. Network Drive and Shared Folder Access:
   - Specify exact folder path needed
   - Provide business reason for access
   - Department head approval may be required
   - Access reviews conducted quarterly
   - Removal of access when role changes

3. Database and Sensitive System Access:
   - Requires additional security clearance
   - Complete data handling training first
   - Multi-level approval process
   - Regular access reviews mandatory
   - Audit trails maintained for compliance

4. Administrative and Elevated Access:
   - Admin access requires special justification
   - C-level or IT director approval needed
   - Temporary admin access only when possible
   - Regular review and revocation
   - Additional security monitoring applied

5. Access Request Status:
   - Check request status in IT portal
   - Email notifications sent for updates
   - Contact IT if urgent (include ticket number)
   - Appeals process available if denied
   - Documentation required for audit purposes

Note: All access requests must follow company security policies and compliance requirements."""
                }
            ]
        }
    
    def search_knowledge_base(self, ticket_text: str, intent: str, threshold: float = 0.3) -> Tuple[str, float]:
        """
        Search knowledge base for relevant information
        Returns: (context, relevance_score)
        """
        if intent not in self.knowledge_base:
            return "", 0.0
        
        ticket_lower = ticket_text.lower()
        ticket_words = set(ticket_lower.split())
        
        best_match = ""
        best_score = 0.0
        
        for article in self.knowledge_base[intent]:
            # Combine title and content for matching
            full_text = (article["title"] + " " + article["content"]).lower()
            content_words = set(full_text.split())
            
            # Calculate word overlap score
            common_words = ticket_words.intersection(content_words)
            if len(ticket_words) > 0:
                overlap_score = len(common_words) / len(ticket_words)
            else:
                overlap_score = 0.0
            
            # Boost score for key technical terms
            key_terms = ["vpn", "outlook", "teams", "keyboard", "monitor", "wifi", "network", "email", "policy", "remote", "hardware", 
                        "access", "permission", "database", "folder", "admin", "security", "approval", "request",
                        "hr", "finance", "facilities", "personal", "procurement", "benefits", "parking"]
            key_matches = sum(1 for term in key_terms if term in ticket_lower and term in full_text)
            key_boost = key_matches * 0.1
            
            final_score = overlap_score + key_boost
            
            if final_score > best_score:
                best_score = final_score
                best_match = f"**{article['title']}**\n\n{article['content']}"
        
        return best_match, best_score
    
    def generate_solution(self, ticket_text: str, intent: str, context: str) -> str:
        """Generate a solution using Azure OpenAI with knowledge base context"""
        
        prompt = f"""You are an IT support specialist. Answer the user's question using ONLY the provided knowledge base information.

KNOWLEDGE BASE INFORMATION:
{context}

USER QUESTION: {ticket_text}

Instructions:
1. Provide a clear, step-by-step solution based ONLY on the knowledge base
2. Be specific and actionable
3. If the knowledge base fully covers the issue, give detailed steps
4. Reference the relevant section from the knowledge base
5. Keep response under 200 words
6. Be professional and helpful

Solution:"""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250,
                temperature=0.2
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating solution: {str(e)}"
    
    def process_allowed_ticket(self, employee_id: str, ticket_text: str, intent: str) -> Dict:
        """
        Main RAG processing function following the flowchart logic
        Input: Allowed ticket (after passing authorization)
        Output: solved_by_rag OR escalate
        """
        
        # Special handling for off_scope requests - provide guidance but always escalate
        if intent == "off_scope":
            context, relevance_score = self.search_knowledge_base(ticket_text, intent)
            if context:
                guidance = self.generate_solution(ticket_text, intent, context)
                return {
                    "status": "escalate",
                    "message": f"This request is outside IT support scope. {guidance}",
                    "employee_id": employee_id,
                    "intent": intent,
                    "kb_relevance": relevance_score,
                    "debug_info": "Off-scope request - provided guidance but escalated"
                }
            else:
                return {
                    "status": "escalate", 
                    "message": "This request appears to be outside IT support scope. Please contact the appropriate department for assistance.",
                    "employee_id": employee_id,
                    "intent": intent,
                    "kb_relevance": 0.0,
                    "debug_info": "Off-scope request - no KB context found"
                }
        
        # Special handling for access_request - provide process guidance but escalate for actual processing
        if intent == "access_request":
            context, relevance_score = self.search_knowledge_base(ticket_text, intent)
            if relevance_score >= 0.2 and context:  # Lower threshold for access requests
                guidance = self.generate_solution(ticket_text, intent, context)
                return {
                    "status": "escalate",
                    "message": f"For access requests, please follow the standard process: {guidance} Your request will be reviewed according to company security policies.",
                    "employee_id": employee_id,
                    "intent": intent,
                    "kb_relevance": relevance_score,
                    "debug_info": "Access request - provided process guidance but escalated for manual processing"
                }
            else:
                return {
                    "status": "escalate",
                    "message": "Please submit your access request through the IT portal with business justification and manager approval. Allow 2-3 business days for processing.",
                    "employee_id": employee_id,
                    "intent": intent, 
                    "kb_relevance": relevance_score,
                    "debug_info": "Access request - standard escalation message"
                }
        
        # Standard processing for other intents
        # Step 1: Search knowledge base for relevant context
        context, relevance_score = self.search_knowledge_base(ticket_text, intent)
        
        # Step 2: Determine if we have sufficient context (threshold for "good KB context")
        kb_threshold = 0.25  # Minimum relevance score to consider "good context"
        
        if relevance_score >= kb_threshold and context:
            # We have good KB context - generate solution
            solution = self.generate_solution(ticket_text, intent, context)
            
            # Check if solution is meaningful (not an error or "don't know" response)
            if (len(solution) > 50 and 
                not any(phrase in solution.lower() for phrase in [
                    "don't have", "cannot answer", "insufficient", "error generating", "not enough information"
                ])):
                
                return {
                    "status": "solved_by_rag",
                    "message": solution,
                    "employee_id": employee_id,
                    "intent": intent,
                    "kb_relevance": relevance_score,
                    "debug_info": f"KB match found with score {relevance_score:.3f}"
                }
        
        # No good KB context or solution failed - escalate
        return {
            "status": "escalate",
            "message": "This issue requires human attention. Your ticket has been escalated to our IT support team who will contact you within 4 business hours.",
            "employee_id": employee_id,
            "intent": intent,
            "kb_relevance": relevance_score,
            "debug_info": f"KB context insufficient (score: {relevance_score:.3f}) or solution quality poor"
        }


def test_rag_system():
    """Test the RAG system with various allowed tickets"""
    
    print("🎯 Testing Support Ticket RAG System")
    print("=" * 60)
    
    rag = SupportTicketRAG()
    
    # Test cases - these should all be "allowed" tickets after authorization
    test_cases = [
        {
            "employee_id": "E007", 
            "ticket": "VPN connects but I cannot reach any internal websites or dashboards.",
            "intent": "network_issue",
            "expected": "solved_by_rag"
        },
        {
            "employee_id": "E002", 
            "ticket": "My Lenovo ThinkPad laptop's N key is physically stuck and will not press down fully.",
            "intent": "hardware_issue", 
            "expected": "solved_by_rag"
        },
        {
            "employee_id": "E006", 
            "ticket": "Outlook shows an error 'mailbox full' and will not send any new emails.",
            "intent": "software_issue",
            "expected": "solved_by_rag"
        },
        {
            "employee_id": "E006", 
            "ticket": "What is the official policy for work from home during probation?",
            "intent": "policy_question",
            "expected": "solved_by_rag"
        },
        {
            "employee_id": "E003", 
            "ticket": "My laptop charger is sparking and there is a burning smell when I plug it in.",
            "intent": "hardware_issue",
            "expected": "escalate"  # Safety issue - should escalate
        },
        {
            "employee_id": "E005",
            "ticket": "I need access to the finance database to complete my quarterly report.",
            "intent": "access_request", 
            "expected": "escalate"  # Access requests should always escalate with guidance
        },
        {
            "employee_id": "E008",
            "ticket": "Can you help me book a conference room for next week's meeting?",
            "intent": "off_scope",
            "expected": "escalate"  # Off-scope requests should escalate with guidance
        },
        {
            "employee_id": "E010", 
            "ticket": "How do I submit an expense report for my business travel?",
            "intent": "off_scope",
            "expected": "escalate"  # Finance-related, should provide guidance and escalate
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Employee: {test_case['employee_id']}")
        print(f"Intent: {test_case['intent']}")
        print(f"Ticket: {test_case['ticket'][:60]}...")
        print(f"Expected: {test_case['expected']}")
        
        # Process the ticket
        result = rag.process_allowed_ticket(
            test_case['employee_id'],
            test_case['ticket'], 
            test_case['intent']
        )
        
        print(f"✅ Result: {result['status']}")
        print(f"📝 Message: {result['message'][:100]}...")
        print(f"🔍 Debug: {result['debug_info']}")
        
        # Check if it matches expected
        match_icon = "✅" if result['status'] == test_case['expected'] else "❌"
        print(f"{match_icon} Expected vs Actual: {test_case['expected']} vs {result['status']}")

if __name__ == "__main__":
    test_rag_system()
    print(f"\n🎉 RAG Testing completed!")