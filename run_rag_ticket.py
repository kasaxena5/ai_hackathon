"""
Parameterized RAG Support Ticket Processing
Usage: python run_rag_ticket.py <employee_id> <intent> "<ticket_text>"
Example: python run_rag_ticket.py E007 network_issue "VPN connects but cannot reach internal sites"
"""

import sys
import argparse
from support_ticket_rag import SupportTicketRAG

def print_result_banner(result):
    """Print formatted result with clear visual separation"""
    print("\n" + "="*80)
    print("🎯 GUARD-RAILED SUPPORT TICKET COPILOT - RAG RESULT")
    print("="*80)
    
    # Employee and ticket info
    print(f"👤 Employee ID: {result['employee_id']}")
    print(f"🏷️  Intent Category: {result['intent']}")
    print(f"📊 Knowledge Base Relevance: {result['kb_relevance']:.3f}")
    
    # Main result
    status_icon = "✅" if result['status'] == 'solved_by_rag' else "🔄"
    print(f"\n{status_icon} STATUS: {result['status'].upper()}")
    
    print(f"\n📝 RESPONSE:")
    print("-" * 60)
    print(result['message'])
    print("-" * 60)
    
    # Debug information
    print(f"\n🔍 Debug Info: {result['debug_info']}")
    print("="*80)

def main():
    parser = argparse.ArgumentParser(
        description="Process support tickets through RAG system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_rag_ticket.py E007 network_issue "VPN connects but cannot reach internal sites"
  python run_rag_ticket.py E002 hardware_issue "My laptop keyboard N key is stuck"
  python run_rag_ticket.py E006 software_issue "Outlook shows mailbox full error"
  python run_rag_ticket.py E005 policy_question "What is the WFH policy during probation?"

Available Intent Categories:
  - network_issue: VPN, WiFi, connectivity problems
  - hardware_issue: Laptop, keyboard, monitor, physical device issues  
  - software_issue: Outlook, Teams, application problems
  - policy_question: Company policies, procedures, guidelines
        """
    )
    
    parser.add_argument('employee_id', help='Employee ID (e.g., E007)')
    parser.add_argument('intent', 
                       choices=['network_issue', 'hardware_issue', 'software_issue', 'policy_question'],
                       help='Ticket intent category')
    parser.add_argument('ticket_text', help='Full ticket description')
    
    # Handle case where user runs without arguments
    if len(sys.argv) == 1:
        print("🎯 Guard-Railed Support Ticket Copilot - RAG Processor")
        print("\nUsage: python run_rag_ticket.py <employee_id> <intent> \"<ticket_text>\"")
        print("\nFor full help: python run_rag_ticket.py --help")
        return
    
    try:
        args = parser.parse_args()
        
        print("🚀 Initializing RAG System...")
        rag = SupportTicketRAG()
        
        print(f"📥 Processing ticket from {args.employee_id}...")
        print(f"🏷️  Intent: {args.intent}")
        print(f"📝 Ticket: {args.ticket_text}")
        
        # Process the ticket
        result = rag.process_allowed_ticket(
            employee_id=args.employee_id,
            ticket_text=args.ticket_text,
            intent=args.intent
        )
        
        # Display formatted result
        print_result_banner(result)
        
        # Exit code based on result
        exit_code = 0 if result['status'] == 'solved_by_rag' else 1
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"❌ Error processing ticket: {str(e)}")
        sys.exit(2)

if __name__ == "__main__":
    main()