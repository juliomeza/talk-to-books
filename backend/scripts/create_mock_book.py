"""
Mock book generator script.
This script creates a sample book in the FAISS vector store for testing.
"""
import os
import sys
import json
import logging
import numpy as np
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import services
from app.services.vector_store import FAISSVectorStore

def create_mock_book():
    """Create a mock book in the vector store for testing."""
    logger.info("Creating mock book...")
    
    # Initialize vector store with the same dimension used in the test script
    # Force creating a new index by providing a different path
    vector_store = FAISSVectorStore(dimension=1536, index_path="data/mock_index")
    
    # Mock book data
    book_id = "mock_book_1"
    book_title = "Pride and Prejudice"
    book_author = "Jane Austen"
    
    # Mock chunks
    chunks = [
        {
            "text": "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.",
            "page": 1,
            "chunk_id": f"{book_id}_chunk_1"
        },
        {
            "text": "However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered the rightful property of some one or other of their daughters.",
            "page": 1,
            "chunk_id": f"{book_id}_chunk_2"
        },
        {
            "text": "My dear Mr. Bennet, said his lady to him one day, have you heard that Netherfield Park is let at last?",
            "page": 1,
            "chunk_id": f"{book_id}_chunk_3"
        },
        {
            "text": "Elizabeth Bennet had been obliged, by the scarcity of gentlemen, to sit down for two dances; and during part of that time, Mr. Darcy had been standing near enough for her to hear a conversation between him and Mr. Bingley.",
            "page": 2,
            "chunk_id": f"{book_id}_chunk_4"
        },
        {
            "text": "In vain I have struggled. It will not do. My feelings will not be repressed. You must allow me to tell you how ardently I admire and love you.",
            "page": 34,
            "chunk_id": f"{book_id}_chunk_5"
        }
    ]
    
    # Create mock embeddings (random vectors)
    embeddings = []
    for _ in range(len(chunks)):
        # Create a random unit vector
        vec = np.random.randn(1536)  # Google's text-embedding-004 has 1536 dimensions
        vec = vec / np.linalg.norm(vec)  # Normalize to unit length
        embeddings.append(vec.tolist())
    
    # Add book chunks to vector store
    vector_store.add_book_chunks(book_id, chunks, embeddings)
    logger.info(f"Added {len(chunks)} chunks for book {book_id}")
    
    # Create Firebase book entry (mock)
    book_metadata = {
        "id": book_id,
        "title": book_title,
        "author": book_author,
        "description": "A classic novel of manners by Jane Austen.",
        "is_public": True,
        "characters": [
            {"id": "elizabeth", "name": "Elizabeth Bennet"},
            {"id": "darcy", "name": "Mr. Darcy"},
            {"id": "jane", "name": "Jane Bennet"},
            {"id": "bingley", "name": "Mr. Bingley"}
        ],
        "personality": {
            "tone": "witty",
            "writing_style": "elegant and precise",
            "personality_traits": ["observant", "ironic", "clever", "satirical", "romantic"],
            "voice_characteristics": "Refined, intelligent, and gently mocking of social conventions"
        }
    }
    
    # Save mock book metadata to a JSON file
    os.makedirs("data", exist_ok=True)
    with open(os.path.join("data", f"{book_id}.json"), "w") as f:
        json.dump(book_metadata, f, indent=2)
    
    logger.info(f"Created mock book metadata for {book_title}")
    logger.info("Mock book creation completed successfully")

if __name__ == "__main__":
    create_mock_book()
