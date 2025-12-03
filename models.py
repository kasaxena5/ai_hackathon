"""
Data models for the Guard-Railed Support Ticket Copilot.
"""

from typing import TypedDict


class TicketState(TypedDict):
    """State schema for the ticket processing pipeline."""
    
    # Input fields
    employee_id: str
    subject: str
    body: str
    
    # Employee profile (populated by lookup_employee_profile)
    employee_profile: dict | None
    
    # Classification results
    is_appropriate: bool | None
    intent: str | None
    
    # Authorization results
    auth_decision: str | None  # "allowed", "blocked_by_auth", "needs_approval"
    auth_reason: str | None  # Reason for the authorization decision
    
    # RAG results
    rag_context: str | None
    rag_answer: str | None
    has_good_context: bool | None
    
    # Final outcome
    outcome: str | None  # "blocked_by_appropriateness", "blocked_by_auth", "needs_approval", "solved_by_rag", "escalate"
    response: str | None
