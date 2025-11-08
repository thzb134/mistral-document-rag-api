from mistralai import Mistral
from typing import List
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating embeddings using Mistral AI"""
    
    def __init__(self, api_key: str, model: str = "mistral-embed"):
        """
        Initialize the embedding service
        
        Args:
            api_key: Mistral AI API key
            model: Embedding model name (default: mistral-embed)
        """
        self.client = Mistral(api_key=api_key)
        self.model = model
        logger.info(f"Initialized EmbeddingService with model: {model}")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                inputs=texts
            )
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text string to embed
            
        Returns:
            Embedding vector
        """
        embeddings = self.embed_texts([text])
        return embeddings[0]
