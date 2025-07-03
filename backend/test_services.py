"""
Test script for BookTalk backend services.
Run this script to test the functionality of various services.
"""
import os
import sys
import logging
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
from app.services.book_parser import BookParser
from app.services.embedding_service import EmbeddingService
from app.services.personality_extractor import PersonalityExtractor
from app.services.vector_store import FAISSVectorStore
from app.services.rag_service import RAGService

def test_book_parser():
    """Test the book parser service."""
    logger.info("Testing BookParser service...")
    
    parser = BookParser()
    
    # Test with a sample text file
    sample_text = """
    This is a sample text file.
    It contains multiple paragraphs.
    
    This is the second paragraph.
    It also contains multiple sentences.
    """
    
    # Write sample text to file
    with open("sample_book.txt", "w") as f:
        f.write(sample_text)
    
    # Parse the file
    text = parser.parse_file("sample_book.txt")
    logger.info(f"Parsed text: {text[:100]}...")
    
    # Chunk the text
    chunks = parser.chunk_text(text)
    logger.info(f"Created {len(chunks)} chunks")
    
    # Clean up
    os.remove("sample_book.txt")
    
    logger.info("BookParser test completed")

def test_embedding_service():
    """Test the embedding service."""
    logger.info("Testing EmbeddingService...")
    
    embedding_service = EmbeddingService()
    
    # Check if API key is available
    if not embedding_service.api_key:
        logger.warning("No Google API key available. Skipping embedding test.")
        return
    
    # Test with a sample text
    sample_text = "This is a test sentence for embedding generation."
    
    # Generate embedding
    embedding = embedding_service.generate_embedding(sample_text)
    
    if embedding:
        logger.info(f"Generated embedding with {len(embedding)} dimensions")
    else:
        logger.error("Failed to generate embedding")
    
    logger.info("EmbeddingService test completed")

def test_personality_extractor():
    """Test the personality extractor service."""
    logger.info("Testing PersonalityExtractor...")
    
    extractor = PersonalityExtractor()
    
    # Check if API key is available
    if not extractor.api_key:
        logger.warning("No Google API key available. Skipping personality extraction test.")
        return
    
    # Test with a sample text
    sample_text = """
    "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.
    
    However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered the rightful property of some one or other of their daughters.
    
    "My dear Mr. Bennet," said his lady to him one day, "have you heard that Netherfield Park is let at last?"
    
    Mr. Bennet replied that he had not.
    
    "But it is," returned she; "for Mrs. Long has just been here, and she told me all about it."
    
    Mr. Bennet made no answer.
    
    "Do you not want to know who has taken it?" cried his wife impatiently.
    
    "You want to tell me, and I have no objection to hearing it."
    
    This was invitation enough.
    """
    
    # Extract personality
    book_metadata = {
        "title": "Pride and Prejudice",
        "author": "Jane Austen"
    }
    
    personality = extractor.extract_book_personality(sample_text, book_metadata)
    logger.info(f"Extracted personality: {personality}")
    
    # Extract characters
    characters = extractor.extract_characters(sample_text, book_metadata)
    logger.info(f"Extracted {len(characters)} characters")
    
    logger.info("PersonalityExtractor test completed")

def test_vector_store():
    """Test the FAISS vector store."""
    logger.info("Testing FAISSVectorStore...")
    
    vector_store = FAISSVectorStore(dimension=3)  # Use small dimension for testing
    
    # Test adding chunks
    chunks = [
        {"text": "This is the first chunk", "page": 1},
        {"text": "This is the second chunk", "page": 1},
        {"text": "This is the third chunk", "page": 2}
    ]
    
    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ]
    
    vector_store.add_book_chunks("test_book", chunks, embeddings)
    
    # Test searching
    results = vector_store.search([1.0, 0.1, 0.1], ["test_book"], top_k=2)
    logger.info(f"Search results: {results}")
    
    # Test statistics
    stats = vector_store.get_stats()
    logger.info(f"Vector store stats: {stats}")
    
    logger.info("FAISSVectorStore test completed")

def test_rag_service():
    """Test the RAG service."""
    logger.info("Testing RAGService...")
    
    # Initialize services
    vector_store = FAISSVectorStore(dimension=3)  # Use small dimension for testing
    embedding_service = EmbeddingService()
    rag_service = RAGService(vector_store, embedding_service)
    
    # Check if API key is available
    if not rag_service.api_key:
        logger.warning("No Google API key available. Skipping RAG test.")
        return
    
    # Add test data to vector store
    chunks = [
        {"text": "Pride and Prejudice is a novel by Jane Austen.", "page": 1},
        {"text": "Elizabeth Bennet is the protagonist of the novel.", "page": 2},
        {"text": "Mr. Darcy is initially portrayed as proud and disagreeable.", "page": 3}
    ]
    
    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0]
    ]
    
    vector_store.add_book_chunks("test_book", chunks, embeddings)
    
    # Mock the retrieve_chunks method to use our test data
    rag_service.retrieve_chunks = lambda query, book_ids, top_k=5: chunks
    
    # Test chat
    messages = [{"role": "user", "content": "Who is Elizabeth Bennet?"}]
    response = rag_service.chat(messages, ["test_book"])
    
    logger.info(f"RAG response: {response['message']}")
    logger.info(f"Sources: {[source['text'] for source in response['sources']]}")
    
    logger.info("RAGService test completed")

def main():
    """Run all tests."""
    logger.info("Starting BookTalk backend services tests...")
    
    test_book_parser()
    test_embedding_service()
    test_personality_extractor()
    test_vector_store()
    test_rag_service()
    
    logger.info("All tests completed")

if __name__ == "__main__":
    main()
