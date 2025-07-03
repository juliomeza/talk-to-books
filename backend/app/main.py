from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
import time
from dotenv import load_dotenv
from app.api import books, chat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="BookTalk API",
    description="API for BookTalk - AI-Powered Conversational Book Companion",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Process the request
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log request details
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"Status: {response.status_code} "
            f"Time: {process_time:.3f}s"
        )
        
        return response
    except Exception as e:
        # Log exceptions
        process_time = time.time() - start_time
        logger.error(
            f"Request: {request.method} {request.url.path} "
            f"Error: {str(e)} "
            f"Time: {process_time:.3f}s"
        )
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# Include routers
app.include_router(books.router, prefix="/books", tags=["books"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])

@app.get("/")
async def root():
    """
    Root endpoint to check if API is running.
    """
    return {
        "message": "Welcome to BookTalk API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    # Check required services
    services_status = {
        "api": "healthy",
        "google_api": "healthy" if os.getenv("GOOGLE_API_KEY") else "not_configured",
        "firebase": "healthy" if os.getenv("FIREBASE_CREDENTIALS_PATH") else "not_configured"
    }
    
    # Overall status
    overall_status = "healthy" if all(status == "healthy" for status in services_status.values()) else "degraded"
    
    return {
        "status": overall_status,
        "services": services_status,
        "timestamp": time.time()
    }
