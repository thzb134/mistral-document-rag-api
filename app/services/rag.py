import chromadb
from chromadb.config import Settings
from mistralai import Mistral
from typing import List, Dict, Tuple
import logging
import uuid

from app.services.embedding import EmbeddingService

logger = logging.getLogger(__name__)

class RAGService:
    """RAG service combining embeddings, vector storage, and LLM"""
    
    def __init__(
        self,
        mistral_api_key: str,
        embedding_service: EmbeddingService,
        model_name: str = "mistral-small-latest",
        persist_directory: str = "./data/chroma"
    ):
        """
        Initialize RAG service
        
        Args:
            mistral_api_key: Mistral AI API key
            embedding_service: Instance of EmbeddingService
            model_name: Chat model name
            persist_directory: Directory to persist ChromaDB data
        """
        self.embedding_service = embedding_service
        self.model_name = model_name
        self.mistral_client = Mistral(api_key=mistral_api_key)
        
        # Initialize ChromaDB with persistence
        self.chroma_client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create or get collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"description": "Document chunks for RAG"}
        )
        
        logger.info(f"Initialized RAGService with model: {model_name}")
    
    def index_document(
        self,
        chunks: List[str],
        document_id: str,
        metadata: Dict = None
    ) -> int:
        """
        Index document chunks into vector database
        
        Args:
            chunks: List of text chunks
            document_id: Unique document identifier
            metadata: Optional metadata for the document
            
        Returns:
            Number of chunks indexed
        """
        try:
            # Generate embeddings for all chunks
            embeddings = self.embedding_service.embed_texts(chunks)
            
            # Prepare data for ChromaDB
            ids = [f"{document_id}_{i}" for i in range(len(chunks))]
            metadatas = [
                {
                    "document_id": document_id,
                    "chunk_index": i,
                    **(metadata or {})
                }
                for i in range(len(chunks))
            ]
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas
            )
            
            logger.info(f"Indexed {len(chunks)} chunks for document {document_id}")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Error indexing document: {e}")
            raise
    
    def query(
        self,
        question: str,
        top_k: int = 3
    ) -> Tuple[str, List[str]]:
        """
        Query the RAG system
        
        Args:
            question: User question
            top_k: Number of relevant chunks to retrieve
            
        Returns:
            Tuple of (answer, source_chunks)
        """
        try:
            # Generate embedding for the question
            question_embedding = self.embedding_service.embed_text(question)
            
            # Query vector database
            results = self.collection.query(
                query_embeddings=[question_embedding],
                n_results=top_k
            )
            
            # Extract relevant chunks
            if not results['documents'] or not results['documents'][0]:
                return "I don't have enough information to answer this question.", []
            
            source_chunks = results['documents'][0]
            context = "\n\n".join(source_chunks)
            
            # Generate answer using Mistral AI
            response = self.mistral_client.chat.complete(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on the provided context. If the context doesn't contain relevant information, say so clearly."
                    },
                    {
                        "role": "user",
                        "content": f"Context:\n{context}\n\nQuestion: {question}\n\nProvide a clear and concise answer based on the context above."
                    }
                ]
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Generated answer for question: {question[:50]}...")
            
            return answer, source_chunks
            
        except Exception as e:
            logger.error(f"Error querying RAG system: {e}")
            raise
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        count = self.collection.count()
        return {
            "total_chunks": count,
            "collection_name": self.collection.name
        }
