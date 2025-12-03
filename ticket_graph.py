"""
Guard-Railed Support Ticket Copilot - LangGraph Pipeline

This module implements the end-to-end per-ticket processing pipeline using LangGraph.
"""

from typing import Literal
from langgraph.graph import StateGraph, START, END
from rules_engine import apply_authorization_rules
from employee_lookup import lookup_employee
from support_ticket_rag import SupportTicketRAG
from models import TicketState
from appropriateness_classifier import IntentAppropriatenessClassifier

# Initialize RAG system (singleton)
_rag_system = SupportTicketRAG()

# Initialize classifier (singleton)
_classifier = IntentAppropriatenessClassifier()


# Node functions - implement these one by one

def lookup_employee_profile(state: TicketState) -> dict:
    """
    Lookup employee profile based on employee_id.
    
    Fetches employee profile from users_roles.csv using the employee_lookup module.
    """
    employee_id = state.get("employee_id", "")
    employee_profile = lookup_employee(employee_id)
    
    if employee_profile is None:
        employee_profile = {}
    
    return {"employee_profile": employee_profile}


def classify_intent_and_appropriateness(state: TicketState) -> dict:
    """
    Classify the ticket's intent and check if the request is appropriate.
    
    Uses IntentAppropriatenessClassifier to determine:
    - intent: hardware_issue, software_issue, network_issue, access_request, policy_question, off_scope, ambiguous
    - is_appropriate: True/False
    """
    subject = state.get("subject", "")
    body = state.get("body", "")
    
    # Combine subject and body for classification
    ticket_text = f"{subject}\n{body}"
    
    # Use classifier to get intent and appropriateness
    result = _classifier.classify_intent_and_appropriateness(ticket_text)
    
    return {
        "is_appropriate": result["is_appropriate"],
        "intent": result["intent"]
    }


def check_authorization(state: TicketState) -> dict:
    """
    Check authorization rules based on employee profile and intent.
    
    Uses the rules engine to determine if the employee is authorized
    to perform the requested action based on their role, department, and intent.
    """
    employee_profile = state.get("employee_profile", {})
    intent = state.get("intent", "")
    
    role = employee_profile.get("role", "")
    department = employee_profile.get("department", "")
    
    auth_status, reason = apply_authorization_rules(intent, role, department)
    
    return {
        "auth_decision": auth_status,
        "auth_reason": reason
    }


def rag_and_llm_answering(state: TicketState) -> dict:
    """
    Use RAG to retrieve relevant context and generate an answer using LLM.
    
    Uses SupportTicketRAG to search knowledge base and generate solutions.
    Returns solved_by_rag if answerable, or escalate if no good context.
    """
    employee_id = state.get("employee_id", "")
    subject = state.get("subject", "")
    body = state.get("body", "")
    intent = state.get("intent", "")
    
    # Combine subject and body for the ticket text
    ticket_text = f"{subject}\n{body}"
    
    # Process through RAG system
    result = _rag_system.process_allowed_ticket(employee_id, ticket_text, intent)
    
    # Map RAG result to state
    has_good_context = result["status"] == "solved_by_rag"
    
    return {
        "rag_context": result.get("debug_info", ""),
        "rag_answer": result.get("message", ""),
        "has_good_context": has_good_context
    }


def return_blocked_by_appropriateness(state: TicketState) -> dict:
    """Return blocked_by_appropriateness outcome."""
    return {
        "outcome": "blocked_by_appropriateness",
        "response": "Your request cannot be processed as it is not appropriate for this support channel."
    }


def return_blocked_by_auth(state: TicketState) -> dict:
    """Return blocked_by_auth outcome."""
    return {
        "outcome": "blocked_by_auth",
        "response": "You are not authorized to perform this action."
    }


def return_needs_approval(state: TicketState) -> dict:
    """Return needs_approval outcome."""
    return {
        "outcome": "needs_approval",
        "response": "Your request requires manager approval before it can be processed."
    }


def return_solved_by_rag(state: TicketState) -> dict:
    """Return solved_by_rag outcome with the RAG-generated answer."""
    return {
        "outcome": "solved_by_rag",
        "response": state.get("rag_answer", "")
    }


def return_escalate(state: TicketState) -> dict:
    """Return escalate outcome when no good KB context is found."""
    return {
        "outcome": "escalate",
        "response": "Your request has been escalated to a human support agent."
    }


# Conditional edge functions

def route_after_appropriateness(state: TicketState) -> Literal["appropriate", "not_appropriate"]:
    """Route based on appropriateness classification."""
    if state.get("is_appropriate"):
        return "appropriate"
    return "not_appropriate"


def route_after_authorization(state: TicketState) -> Literal["allowed", "blocked_by_auth", "needs_approval"]:
    """Route based on authorization decision."""
    auth_decision = state.get("auth_decision", "blocked_by_auth")
    if auth_decision == "allowed":
        return "allowed"
    elif auth_decision == "needs_approval":
        return "needs_approval"
    return "blocked_by_auth"


def route_after_rag(state: TicketState) -> Literal["answerable", "no_good_context"]:
    """Route based on whether good KB context was found."""
    if state.get("has_good_context"):
        return "answerable"
    return "no_good_context"


# Build the graph
def build_ticket_graph() -> StateGraph:
    """Build and return the ticket processing graph."""
    
    # Create the graph with the state schema
    graph = StateGraph(TicketState)
    
    # Add nodes
    graph.add_node("lookup_employee_profile", lookup_employee_profile)
    graph.add_node("classify_intent_and_appropriateness", classify_intent_and_appropriateness)
    graph.add_node("check_authorization", check_authorization)
    graph.add_node("rag_and_llm_answering", rag_and_llm_answering)
    graph.add_node("return_blocked_by_appropriateness", return_blocked_by_appropriateness)
    graph.add_node("return_blocked_by_auth", return_blocked_by_auth)
    graph.add_node("return_needs_approval", return_needs_approval)
    graph.add_node("return_solved_by_rag", return_solved_by_rag)
    graph.add_node("return_escalate", return_escalate)
    
    # Add edge from START
    graph.add_edge(START, "lookup_employee_profile")
    
    # Add edges
    graph.add_edge("lookup_employee_profile", "classify_intent_and_appropriateness")
    
    # Conditional edge after appropriateness classification
    graph.add_conditional_edges(
        "classify_intent_and_appropriateness",
        route_after_appropriateness,
        {
            "appropriate": "check_authorization",
            "not_appropriate": "return_blocked_by_appropriateness"
        }
    )
    
    # Conditional edge after authorization check
    graph.add_conditional_edges(
        "check_authorization",
        route_after_authorization,
        {
            "allowed": "rag_and_llm_answering",
            "blocked_by_auth": "return_blocked_by_auth",
            "needs_approval": "return_needs_approval"
        }
    )
    
    # Conditional edge after RAG
    graph.add_conditional_edges(
        "rag_and_llm_answering",
        route_after_rag,
        {
            "answerable": "return_solved_by_rag",
            "no_good_context": "return_escalate"
        }
    )
    
    # Terminal nodes go to END
    graph.add_edge("return_blocked_by_appropriateness", END)
    graph.add_edge("return_blocked_by_auth", END)
    graph.add_edge("return_needs_approval", END)
    graph.add_edge("return_solved_by_rag", END)
    graph.add_edge("return_escalate", END)
    
    return graph


# Compile the graph
def get_compiled_graph():
    """Build and compile the graph for execution."""
    graph = build_ticket_graph()
    return graph.compile()


def process_ticket(ticket_id: str, employee_id: str, subject: str, body: str) -> dict:
    """
    Process a support ticket through the pipeline.
    
    Args:
        ticket_id: Unique identifier for the ticket
        employee_id: The ID of the employee submitting the ticket
        subject: The subject line of the ticket
        body: The body/description of the ticket
        
    Returns:
        The final state after processing, including outcome and response
    """
    # Get the compiled graph
    app = get_compiled_graph()
    
    # Create initial state
    initial_state: TicketState = {
        "ticket_id": ticket_id,
        "employee_id": employee_id,
        "subject": subject,
        "body": body,
        "employee_profile": None,
        "is_appropriate": None,
        "intent": None,
        "auth_decision": None,
        "auth_reason": None,
        "rag_context": None,
        "rag_answer": None,
        "has_good_context": None,
        "outcome": None,
        "response": None
    }
    
    # Run the graph
    final_state = app.invoke(initial_state)
    
    return final_state
