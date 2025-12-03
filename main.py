"""
FastAPI Backend Service for Support Ticket Processing

This module provides a REST API service for processing support tickets
through the guard-railed support ticket copilot pipeline.
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from ticket_graph import process_ticket
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Support Ticket Copilot API",
    description="A guard-railed support ticket processing service",
    version="1.0.0"
)


# Pydantic models for request/response
class TicketRequest(BaseModel):
    """Request model for ticket submission."""
    employee_id: str = Field(..., description="Employee ID of the ticket submitter")
    subject: str = Field(..., description="Subject/title of the support ticket")
    body: str = Field(..., description="Detailed description of the issue")

class TicketResponse(BaseModel):
    """Response model for ticket processing results."""
    ticket_id: Optional[str] = Field(None, description="Unique identifier for the ticket")
    outcome: str = Field(..., description="Final processing outcome")
    response: str = Field(..., description="Response message to the user")

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service health status")
    message: str = Field(..., description="Health check message")


# API Routes

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with basic service information."""
    return {
        "service": "Support Ticket Copilot API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="Support Ticket Copilot API is running normally"
    )


@app.post("/tickets/process", response_model=TicketResponse, tags=["Tickets"])
async def process_support_ticket(ticket: TicketRequest):
    """
    Process a support ticket through the guard-railed pipeline.
    
    This endpoint:
    1. Validates the employee profile
    2. Checks appropriateness of the request
    3. Applies authorization rules
    4. Attempts RAG-based resolution
    5. Returns the final outcome and response
    
    Args:
        ticket: TicketRequest containing employee_id, subject, and body
    
    Returns:
        TicketResponse: Complete processing results
    
    Raises:
        HTTPException: If processing fails or invalid input is provided
    """
    try:
        logger.info(f"Processing ticket from employee {ticket.employee_id}")
        
        # Validate input
        if not ticket.employee_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID cannot be empty"
            )
        
        if not ticket.subject.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subject cannot be empty"
            )
        
        if not ticket.body.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ticket body cannot be empty"
            )
        
        # Generate a unique ticket ID
        ticket_id = str(uuid.uuid4())
        
        logger.info(f"Generated ticket_id: {ticket_id}")
        
        # Process the ticket through the pipeline
        result = process_ticket(ticket_id, ticket.employee_id, ticket.subject, ticket.body)
        
        logger.info(f"Ticket {ticket_id} processing completed with outcome: {result.get('outcome', 'unknown')}")
        
        # Build response
        response = TicketResponse(
            ticket_id=ticket_id,
            outcome=result.get('outcome', 'unknown'),
            response=result.get('response', 'No response available'),
        )
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing ticket: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the ticket: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)