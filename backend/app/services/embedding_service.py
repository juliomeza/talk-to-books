import os
import logging
from typing import List, Dict, Any, Optional
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Service for generating text embeddings using Google's embedding API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize embedding service.
        
        Args:
            api_key: Google API key (defaults to environment variable GOOGLE_API_KEY)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("No Google API key provided. Embedding functionality will be limited.")
        
        self.model = "text-embedding-004"  # Latest Google embedding model
        self.api_url = f"https://generativelanguage.googleapis.com/v1/models/{self.model}:embedContent"
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a text.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            Embedding vector or None if failed
        """
        if not self.api_key:
            logger.error("Cannot generate embedding: No API key")
            return None
        
        try:
            headers = {"Content-Type": "application/json"}
            params = {"key": self.api_key}
            
            data = {
                "model": self.model,
                "content": {"parts": [{"text": text}]}
            }
            
            response = requests.post(self.api_url, headers=headers, params=params, json=data)
            
            if response.status_code == 200:
                result = response.json()
                embedding = result.get("embedding", {}).get("values", [])
                return embedding
            else:
                logger.error(f"Error generating embedding: {response.status_code} {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Exception generating embedding: {e}")
            return None
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List of embedding vectors (or None for failed ones)
        """
        return [self.generate_embedding(text) for text in texts]
