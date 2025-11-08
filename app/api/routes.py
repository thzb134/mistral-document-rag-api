from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Optional
import os
import uuid
import logging
from pathlib import Path

from app.models import (
    DocumentUploadResponse,
    QueryRequest,
    QueryResponse,
    HealthCheckResponse
)
from app.config import get_settings
from app.services.embedding import EmbeddingService
from app.services.document_processor import DocumentProcessor
from app.services.rag import RAGService

logger = logging.getLogger(__name__)
router = APIRouter()

# Global service instances (initialized in main.py startup)
embedding_service: Optional[EmbeddingService] = None
document_processor: Optional[DocumentProcessor] = None
rag_service: Optional[RAGService] = None

# Ensure upload directory exists
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def get_services():
    """Dependency to get initialized services"""
    if not all([embedding_service, document_processor, rag_service]):
        raise HTTPException(
            status_code=503,
            detail="Services not initialized. Please check server startup."
        )
    return {
        "embedding": embedding_service,
        "processor": document_processor,
        "rag": rag_service
    }


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    services: dict = Depends(get_services)
):
    """
    Upload and process a document for RAG
    
    Accepts PDF, TXT, or MD files
    """
    try:
        allowed_extensions = [".pdf", ".txt", ".md"]
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Allowed: {', '.join(allowed_extensions)}"
            )
        
        doc_id = str(uuid.uuid4())
        
        file_path = UPLOAD_DIR / f"{doc_id}_{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Saved file: {file_path}")
        
        processor: DocumentProcessor = services["processor"]
        chunks = processor.process_file(str(file_path))
        
        rag: RAGService = services["rag"]
        chunks_indexed = rag.index_document(
            chunks=chunks,
            document_id=doc_id,
            metadata={"filename": file.filename, "file_type": file_ext}
        )
        
        logger.info(f"Successfully indexed document {doc_id} with {chunks_indexed} chunks")
        
        return DocumentUploadResponse(
            document_id=doc_id,
            filename=file.filename,
            chunks_created=chunks_indexed,
            message="Document uploaded and indexed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    services: dict = Depends(get_services)
):
    """
    Query the RAG system with a question
    
    Returns an answer based on indexed documents
    """
    try:
        rag: RAGService = services["rag"]
        
        answer, sources = rag.query(
            question=request.question,
            top_k=request.top_k
        )
        
        logger.info(f"Answered query: {request.question[:50]}...")
        
        return QueryResponse(
            question=request.question,
            answer=answer,
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint
    
    Verifies that services are initialized and ready
    """
    try:
        services_ready = all([embedding_service, document_processor, rag_service])
        
        if not services_ready:
            return HealthCheckResponse(
                status="unhealthy",
                mistral_connection=False,
                message="Services not fully initialized"
            )
        
        stats = rag_service.get_collection_stats()
        
        return HealthCheckResponse(
            status="healthy",
            mistral_connection=True,
            message=f"All systems operational. {stats['total_chunks']} chunks indexed."
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            mistral_connection=False,
            message=f"Error: {str(e)}"
        )


@router.get("/stats")
async def get_stats(services: dict = Depends(get_services)):
    """Get statistics about the RAG system"""
    try:
        rag: RAGService = services["rag"]
        stats = rag.get_collection_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
