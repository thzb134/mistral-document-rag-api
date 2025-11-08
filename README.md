# Mistral Document RAG API

A production-ready Retrieval Augmented Generation (RAG) API powered by Mistral AI, enabling intelligent document analysis and question-answering capabilities.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Project Overview

This project implements a sophisticated RAG (Retrieval Augmented Generation) system that allows users to upload documents (PDF, TXT, Markdown) and query them using natural language. The system leverages Mistral AI's powerful language models and embeddings to provide accurate, context-aware responses.

**Key Features:**
- Multi-format document support (PDF, TXT, MD)
- Intelligent semantic search using Mistral embeddings
- Context-aware question answering
- Fully containerized with Docker
- Production-ready FastAPI implementation
- Persistent vector storage with ChromaDB
- Secure API key management

## Architecture
┌─────────────┐      ┌───────────────────────┐      ┌──────────────┐
│   Client    │────▶│   FastAPI Application  │────▶│  Mistral AI  │
│             │      │                       │      │     API      │
└─────────────┘      └───────────┬───────────┘      └──────────────┘
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │      ChromaDB         │
                     │     Vector Store      │
                     └───────────────────────┘

**Tech Stack:**
- **Framework**: FastAPI (async, high-performance)
- **LLM**: Mistral AI (`mistral-small-latest`)
- **Embeddings**: Mistral Embeddings (`mistral-embed`)
- **Vector DB**: ChromaDB (persistent storage)
- **Document Processing**: PyPDF2
- **Containerization**: Docker + Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Mistral AI API key ([Get one here](https://console.mistral.ai/))

### Installation with Docker (Recommended)

1.  **Clone the repository**
    ```bash
    git clone https://github.com/YOUR_USERNAME/mistral-document-rag-api.git
    cd mistral-document-rag-api
    ```

2.  **Set up environment variables**
    Copy the example `.env` file.
    ```bash
    cp .env.example .env
    ```
    Edit `.env` and add your Mistral API key:
    ```ini
    MISTRAL_API_KEY=your_api_key_here
    MODEL_NAME=mistral-small-latest
    EMBEDDING_MODEL=mistral-embed
    ```

3.  **Build and run with Docker**
    ```bash
    docker-compose up --build
    ```

4.  **Access the API**
    -   **API Documentation**: http://localhost:8000/docs
    -   **Health Check**: http://localhost:8000/api/health

### Local Installation (Alternative)

1.  **Create virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows: venv\Scripts\activate
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables** (same as above)

4.  **Run the application**
    ```bash
    uvicorn app.main:app --reload
    ```

## API Usage

### Upload a Document

curl -X POST "http://localhost:8000/api/upload" \
-F "file=@your_document.pdf"

#### Response:

{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "your_document.pdf",
  "chunks_created": 15,
  "message": "Document uploaded and indexed successfully"
}

### Query Documents

curl -X POST "http://localhost:8000/api/query" \
-H "Content-Type: application/json" \
-d '{
  "question": "What is the main topic of the document?",
  "top_k": 3
}'

#### Response:

{
  "question": "What is the main topic of the document?",
  "answer": "The document discusses...",
  "sources": ["chunk1...", "chunk2...", "chunk3..."]
}

### Check Health

curl http://localhost:8000/api/health


## Project Structure

mistral-document-rag-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Configuration management
│   ├── models.py               # Pydantic models
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py             # API endpoints
│   └── services/
│       ├── __init__.py
│       ├── embedding.py          # Mistral embedding service
│       ├── document_processor.py # Document chunking
│       └── rag.py                # RAG implementation
├── data/                       # ChromaDB persistence
├── uploads/                    # Uploaded documents
├── tests/                      # Unit tests
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose orchestration
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── .gitignore
├── .dockerignore
└── README.md


## Development

### Running Tests

    ```bash
    # Install dev dependencies
    pip install -r requirements.txt

    # Run tests
    pytest tests/
    ```

### Code Quality

    ```bash
    # Format code
    black app/

    # Lint
    flake8 app/
    ```

### Docker Commands

    ```bash
    # Build image
    docker-compose build

    # Run in background
    docker-compose up -d

    # View logs
    docker-compose logs -f

    # Stop containers
    docker-compose down

    # Rebuild from scratch
    docker-compose build --no-cache
    ```

## Configuration

Environment variables can be configured in the .env file:

**Variable**        **Description**	            **Default**
MISTRAL_API_KEY	    Your Mistral AI API         key	Required
MODEL_NAME	        Chat completion model	    mistral-small-latest
EMBEDDING_MODEL	    Embedding model	            mistral-embed
APP_NAME	        Application name	        Mistral Document RAG API
DEBUG	            Debug mode	                false


## Features in Detail

### Document Processing

- Automatic text extraction from PDFs, TXT, and Markdown files.
- Intelligent chunking with configurable size and overlap.
- Sentence-boundary aware splitting for better context.

### RAG System

- Semantic search using Mistral embeddings (1024 dimensions).
- Persistent vector storage with ChromaDB.
- Configurable top-k retrieval for context.
- Context-aware answer generation.

### API Design

- RESTful endpoints with proper HTTP methods.
- Request/response validation with Pydantic.
- Comprehensive error handling and status codes.
- Automatic interactive API documentation.
- CORS support for web clients.

### Infrastructure

- Multi-stage Docker builds for optimized and secure images.
- Health checks for service monitoring.
- Volume persistence for database and uploaded files.
- Environment-based configuration for flexibility.
- Production-ready logging setup.


## Best Practices Implemented

- Code: Clean structure with separation of concerns, extensive type hints, dependency injection pattern, and async/await for performance.
- Security: API keys managed via environment variables, non-root Docker user, and no secrets committed to Git.
- DevOps: Consistent environments with Docker, detailed .gitignore and .dockerignore, and easy-to-run setup.
- Testing: Clear structure for adding unit and integration tests.
- Documentation: Comprehensive README and auto-generated API docs.


## Author

Thibault Gougeon, student at ESIEE Paris, Data Sciences & AI program - Internship Application Project for Mistral AI


**Note:** This project was developed as part of an internship application for Mistral AI, demonstrating proficiency in:
    
    - Modern Python development (FastAPI, async programming)
    - AI/ML integration (RAG systems, embeddings, LLMs)
    - Infrastructure & DevOps (Docker, containerization)
    - API design and documentation
    - Production-ready code practices