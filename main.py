"""
CLI Client for Support Ticket Processing

This module provides a command-line interface for users to submit support tickets
and get responses through the guard-railed support ticket copilot pipeline.
"""

import sys
from ticket_graph import process_ticket


def get_user_input():
    """
    Collect ticket information from the user via command line input.
    
    Returns:
        tuple: (employee_id, subject, body)
    """
    print("=" * 60)
    print("    SUPPORT TICKET COPILOT - CLI CLIENT")
    print("=" * 60)
    print()
    
    # Get employee ID
    while True:
        employee_id = input("Enter your Employee ID: ").strip()
        if employee_id:
            break
        print("Employee ID cannot be empty. Please try again.")
    
    # Get subject
    while True:
        subject = input("Enter ticket subject: ").strip()
        if subject:
            break
        print("Subject cannot be empty. Please try again.")
    
    # Get body/description
    print("\nEnter ticket description (press Enter twice when finished):")
    body_lines = []
    empty_line_count = 0
    
    while True:
        line = input()
        if line.strip() == "":
            empty_line_count += 1
            if empty_line_count >= 2:
                break
        else:
            empty_line_count = 0
            body_lines.append(line)
    
    body = "\n".join(body_lines).strip()
    
    if not body:
        print("Description cannot be empty. Please try again.")
        return get_user_input()
    
    return employee_id, subject, body


def display_result(result):
    """
    Display the processing result to the user.
    
    Args:
        result (dict): The final state from process_ticket containing outcome and response
    """
    print("\n" + "=" * 60)
    print("    TICKET PROCESSING RESULT")
    print("=" * 60)
    
    outcome = result.get('outcome', 'Unknown')
    response = result.get('response', 'No response available')
    
    print(f"\nFinal Status: {outcome.upper()}")
    print(f"\nMessage:")
    print("-" * 40)
    print(response)
    print("-" * 40)
    
    # Add some context based on the outcome
    outcome_context = {
        'blocked_by_appropriateness': "🚫 Your request was blocked due to inappropriateness.",
        'blocked_by_auth': "🔒 You don't have the required authorization.",
        'needs_approval': "⏳ Your request requires additional approval.",
        'solved_by_rag': "✅ Your request has been resolved automatically.",
        'escalate': "📞 Your request has been escalated to human support."
    }
    
    if outcome in outcome_context:
        print(f"\nNote: {outcome_context[outcome]}")


def main():
    """
    Main function to run the CLI client.
    """
    try:
        # Get input from user
        employee_id, subject, body = get_user_input()
        
        # Confirm submission
        print(f"\nSubmitting ticket for Employee ID: {employee_id}")
        print(f"Subject: {subject}")
        print("\nProcessing your ticket...")
        print("-" * 60)
        
        # Process the ticket
        result = process_ticket(employee_id, subject, body)
        
        # Display the result
        display_result(result)
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred while processing your ticket: {str(e)}")
        print("Please try again or contact system administrator.")
        sys.exit(1)


def interactive_mode():
    """
    Run the client in interactive mode, allowing multiple ticket submissions.
    """
    print("Welcome to Support Ticket Copilot!")
    print("Type 'quit' or 'exit' to stop the program.")
    
    while True:
        try:
            # Ask if user wants to submit a ticket
            print("\n" + "=" * 60)
            action = input("Would you like to submit a ticket? (y/n/quit): ").strip().lower()
            
            if action in ['quit', 'exit', 'q']:
                print("Thank you for using Support Ticket Copilot!")
                break
            elif action in ['y', 'yes']:
                main()
                input("\nPress Enter to continue...")
            elif action in ['n', 'no']:
                continue
            else:
                print("Please enter 'y' for yes, 'n' for no, or 'quit' to exit.")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nAn unexpected error occurred: {str(e)}")
            print("Please try again.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        main()