from pydantic import BaseModel, Field
from typing import List, Optional

class DocumentUploadResponse(BaseModel):
    """Response after document upload"""
    document_id: str
    filename: str
    chunks_created: int
    message: str

class QueryRequest(BaseModel):
    """Request model for querying documents"""
    question: str = Field(..., min_length=1, description="Question to ask about the documents")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of relevant chunks to retrieve")

class QueryResponse(BaseModel):
    """Response model for queries"""
    question: str
    answer: str
    sources: List[str]
    
class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    mistral_connection: bool
    message: str
