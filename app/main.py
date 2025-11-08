from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api import routes
from app.services.embedding import EmbeddingService
from app.services.document_processor import DocumentProcessor
from app.services.rag import RAGService
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="A RAG-based document analysis API powered by Mistral AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(routes.router, prefix="/api", tags=["RAG"])


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup"""
    try:
        logger.info(f"Starting {settings.app_name}")
        logger.info(f"Debug mode: {settings.debug}")
        
        # Ensure data directory exists
        os.makedirs("./data/chroma", exist_ok=True)
        
        # Initialize embedding service
        routes.embedding_service = EmbeddingService(
            api_key=settings.mistral_api_key,
            model=settings.embedding_model
        )
        logger.info("✓ Embedding service initialized")
        
        # Initialize document processor
        routes.document_processor = DocumentProcessor(
            chunk_size=1000,
            chunk_overlap=200
        )
        logger.info("✓ Document processor initialized")
        
        # Initialize RAG service
        routes.rag_service = RAGService(
            mistral_api_key=settings.mistral_api_key,
            embedding_service=routes.embedding_service,
            model_name=settings.model_name,
            persist_directory="./data/chroma"
        )
        logger.info("✓ RAG service initialized")
        
        logger.info("🚀 All services ready!")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Shutting down application")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Mistral Document RAG API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "endpoints": {
            "upload": "POST /api/upload",
            "query": "POST /api/query",
            "stats": "GET /api/stats"
        }
    }
