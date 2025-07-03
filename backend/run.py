"""
Entry point for running the FastAPI server.
"""
import uvicorn
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def create_required_directories():
    """Create required directories for the application."""
    # Create data directory for FAISS index
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        logger.info(f"Created data directory: {data_dir}")
    
    # Create uploads directory for temporary files
    uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        logger.info(f"Created uploads directory: {uploads_dir}")

if __name__ == "__main__":
    # Create required directories
    create_required_directories()
    
    # Get config from environment or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    
    # Log configuration
    logger.info(f"Starting server with configuration:")
    logger.info(f"  - Host: {host}")
    logger.info(f"  - Port: {port}")
    logger.info(f"  - Debug: {debug}")
    logger.info(f"  - Google API Key: {'Configured' if os.getenv('GOOGLE_API_KEY') else 'Missing'}")
    logger.info(f"  - Firebase Credentials: {'Configured' if os.getenv('FIREBASE_CREDENTIALS_PATH') else 'Missing'}")
    
    # Run with uvicorn
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug
    )
