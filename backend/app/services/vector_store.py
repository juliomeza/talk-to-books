import os
import pickle
import numpy as np
import faiss
from typing import List, Dict, Any, Optional, Tuple
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class FAISSVectorStore:
    """
    A vector store implementation using FAISS for efficient similarity search.
    This is used for the retrieval part of the RAG pipeline.
    """
    
    def __init__(self, dimension: int = 1536, index_path: Optional[str] = None):
        """
        Initialize FAISS vector store.
        
        Args:
            dimension: Dimension of the embedding vectors (default: 1536 for Google's text-embedding-004)
            index_path: Path to save/load the index and metadata
        """
        self.dimension = dimension
        self.index_path = index_path or os.getenv("FAISS_INDEX_PATH", "data/faiss_index")
        self.metadata_path = f"{self.index_path}_metadata.pkl"
        
        # Initialize or load index and metadata
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self._load_from_disk()
        else:
            self.index = faiss.IndexFlatL2(dimension)  # L2 distance
            self.book_chunks: Dict[str, Dict[str, Any]] = {}  # Maps chunk_ids to metadata
            self.book_index: Dict[str, List[str]] = {}  # Maps book_ids to chunk_ids
            logger.info(f"Created new FAISS index with dimension {dimension}")
    
    def _load_from_disk(self):
        """Load index and metadata from disk."""
        try:
            # Load FAISS index
            self.index = faiss.read_index(self.index_path)
            
            # Load metadata
            with open(self.metadata_path, 'rb') as f:
                metadata = pickle.load(f)
                self.book_chunks = metadata.get('book_chunks', {})
                self.book_index = metadata.get('book_index', {})
            
            logger.info(f"Loaded FAISS index from {self.index_path} with {len(self.book_chunks)} chunks")
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
            self.index = faiss.IndexFlatL2(self.dimension)
            self.book_chunks = {}
            self.book_index = {}
    
    def _save_to_disk(self):
        """Save index and metadata to disk."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, self.index_path)
            
            # Save metadata
            metadata = {
                'book_chunks': self.book_chunks,
                'book_index': self.book_index
            }
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
            
            logger.info(f"Saved FAISS index to {self.index_path} with {len(self.book_chunks)} chunks")
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
    
    def add_book_chunks(self, book_id: str, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Add book chunks and their embeddings to the vector store.
        
        Args:
            book_id: ID of the book
            chunks: List of chunk metadata (text, page, etc.)
            embeddings: List of embedding vectors for each chunk
        """
        # Get current chunk IDs for the book
        existing_chunk_ids = self.book_index.get(book_id, [])
        
        # Create new chunk IDs
        chunk_ids = []
        
        # Add each chunk and its embedding
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = f"{book_id}_chunk_{i}"
            chunk_ids.append(chunk_id)
            
            # Store chunk metadata
            self.book_chunks[chunk_id] = {
                "text": chunk["text"],
                "book_id": book_id,
                "page": chunk.get("page"),
                "chunk_id": chunk_id
            }
        
        # Store book index
        self.book_index[book_id] = chunk_ids
        
        # Add embeddings to FAISS
        embeddings_array = np.array(embeddings).astype('float32')
        self.index.add(embeddings_array)
        
        logger.info(f"Added {len(chunks)} chunks for book {book_id}")
        
        # Save to disk
        self._save_to_disk()
    
    def search(self, query_embedding: List[float], book_ids: Optional[List[str]] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using the query embedding.
        
        Args:
            query_embedding: Embedding vector of the query
            book_ids: Optional list of book IDs to restrict the search to
            top_k: Number of results to return
            
        Returns:
            List of chunk metadata for the most similar chunks
        """
        query_embedding_array = np.array([query_embedding]).astype('float32')
        
        # Perform search
        distances, indices = self.index.search(query_embedding_array, top_k)
        
        # Get chunk IDs for all books or specified books
        all_chunk_ids = []
        if book_ids:
            for book_id in book_ids:
                all_chunk_ids.extend(self.book_index.get(book_id, []))
        else:
            all_chunk_ids = list(self.book_chunks.keys())
        
        # Get results
        results = []
        for i in indices[0]:
            if i < len(all_chunk_ids):
                chunk_id = all_chunk_ids[i]
                chunk_metadata = self.book_chunks.get(chunk_id)
                if chunk_metadata:
                    results.append(chunk_metadata)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "total_chunks": len(self.book_chunks),
            "total_books": len(self.book_index),
            "dimension": self.dimension
        }
    
    def save(self, path: Optional[str] = None):
        """
        Save the FAISS index to disk.
        
        Args:
            path: Path to save the index
        """
        if path:
            self.index_path = path
            self.metadata_path = f"{path}_metadata.pkl"
        
        self._save_to_disk()
    
    def load(self, path: str):
        """
        Load the FAISS index from disk.
        
        Args:
            path: Path to load the index from
        """
        self.index_path = path
        self.metadata_path = f"{path}_metadata.pkl"
        self._load_from_disk()
