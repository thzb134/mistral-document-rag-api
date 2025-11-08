#!/bin/bash

echo "Testing Mistral RAG API Docker Setup"
echo "========================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create .env file with MISTRAL_API_KEY"
    exit 1
fi

# Build and start
echo "Building Docker image..."
docker-compose build

echo "Starting container..."
docker-compose up -d

echo "Waiting for API to be ready..."
sleep 10

# Test health endpoint
echo "Testing health endpoint..."
curl -s http://localhost:8000/api/health | python -m json.tool

echo ""
echo "Docker setup complete!"
echo "API Documentation: http://localhost:8000/docs"
echo "View logs: docker-compose logs -f"
echo "Stop container: docker-compose down"
