from fastapi import APIRouter, Depends, HTTPException, Header
from typing import List, Optional
import logging
from app.models.schemas import ChatRequest, ChatResponse, Message
from app.services.firebase_service import FirebaseService
from app.services.rag_service import RAGService
from app.services.vector_store import FAISSVectorStore
from app.services.embedding_service import EmbeddingService

router = APIRouter()
logger = logging.getLogger(__name__)

# Dependencies
def get_firebase_service():
    return FirebaseService()

def get_rag_service():
    vector_store = FAISSVectorStore()
    embedding_service = EmbeddingService()
    return RAGService(vector_store, embedding_service)

# Dependency to verify token and get user ID
def get_user_id(
    token: Optional[str] = Header(None),
    firebase_service: FirebaseService = Depends(get_firebase_service)
):
    if not token:
        return None
    
    user_id = firebase_service.verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user_id

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: Optional[str] = Depends(get_user_id),
    firebase_service: FirebaseService = Depends(get_firebase_service),
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Chat with books using RAG.
    """
    # Validate access to books and get book personalities
    book_personalities = []
    for book_id in request.book_ids:
        book = firebase_service.get_book(book_id, user_id)
        if not book:
            raise HTTPException(
                status_code=404,
                detail=f"Book not found or access denied: {book_id}"
            )
        book_personalities.append(book)
    
    # Convert messages to dict format
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    # Process chat
    response = rag_service.chat(
        messages=messages,
        book_ids=request.book_ids,
        character_id=request.character_id,
        book_personalities=book_personalities
    )
    
    return response
