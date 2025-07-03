from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File, Form, BackgroundTasks
from typing import List, Optional
import logging
import os
import tempfile
import shutil
from app.models.schemas import BookMetadata, BookUploadResponse
from app.services.firebase_service import FirebaseService
from app.services.book_parser import BookParser
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import FAISSVectorStore
from app.services.personality_extractor import PersonalityExtractor

router = APIRouter()
logger = logging.getLogger(__name__)

# Dependency to get services
def get_firebase_service():
    return FirebaseService()

def get_book_parser():
    return BookParser()

def get_embedding_service():
    return EmbeddingService()

def get_vector_store():
    return FAISSVectorStore()

def get_personality_extractor():
    return PersonalityExtractor()

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

@router.get("/", response_model=List[BookMetadata])
async def list_books(
    user_id: Optional[str] = Depends(get_user_id),
    firebase_service: FirebaseService = Depends(get_firebase_service)
):
    """
    List all available books (public + user's private books).
    """
    books = firebase_service.list_books(user_id)
    return books

@router.get("/{book_id}", response_model=BookMetadata)
async def get_book(
    book_id: str,
    user_id: Optional[str] = Depends(get_user_id),
    firebase_service: FirebaseService = Depends(get_firebase_service)
):
    """
    Get details about a specific book.
    """
    book = firebase_service.get_book(book_id, user_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found or access denied")
    
    return book

async def process_book_background(
    temp_file_path: str,
    book_id: str,
    book_data: dict,
    user_id: str,
    firebase_service: FirebaseService,
    book_parser: BookParser,
    embedding_service: EmbeddingService,
    vector_store: FAISSVectorStore,
    personality_extractor: PersonalityExtractor
):
    """
    Background task to process an uploaded book.
    """
    try:
        # 1. Parse the book file
        logger.info(f"Parsing book file: {temp_file_path}")
        text_content = book_parser.parse_file(temp_file_path)
        if not text_content:
            logger.error(f"Failed to parse book file: {temp_file_path}")
            return
        
        # 2. Chunk the text
        chunks = book_parser.chunk_text(text_content)
        logger.info(f"Created {len(chunks)} chunks for book {book_id}")
        
        # 3. Extract personalities and characters
        book_personality = personality_extractor.extract_book_personality(
            text_content[:50000],  # Use first ~50k characters
            book_data
        )
        
        characters = personality_extractor.extract_characters(
            text_content[:50000],
            book_data
        )
        
        # 4. Generate embeddings for chunks
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = embedding_service.generate_embeddings_batch(chunk_texts)
        
        # Filter out any None embeddings
        valid_chunks = []
        valid_embeddings = []
        for chunk, embedding in zip(chunks, embeddings):
            if embedding is not None:
                valid_chunks.append(chunk)
                valid_embeddings.append(embedding)
        
        # 5. Add to vector store
        if valid_chunks and valid_embeddings:
            vector_store.add_book_chunks(book_id, valid_chunks, valid_embeddings)
        
        # 6. Update book metadata with personalities and characters
        book_data.update({
            "personality": book_personality,
            "characters": characters
        })
        
        # 7. Save to Firebase
        firebase_service.update_book(book_id, book_data)
        
        logger.info(f"Successfully processed book {book_id}")
    
    except Exception as e:
        logger.error(f"Error processing book {book_id}: {e}")
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@router.post("/upload", response_model=BookUploadResponse)
async def upload_book(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    author: str = Form(...),
    description: str = Form(...),
    is_public: bool = Form(False),
    user_id: str = Depends(get_user_id),
    firebase_service: FirebaseService = Depends(get_firebase_service),
    book_parser: BookParser = Depends(get_book_parser),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    vector_store: FAISSVectorStore = Depends(get_vector_store),
    personality_extractor: PersonalityExtractor = Depends(get_personality_extractor)
):
    """
    Upload a new book and process it.
    """
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # 1. Create book entry with basic metadata
    book_data = {
        "title": title,
        "author": author,
        "description": description,
        "is_public": is_public,
        "owner_id": user_id,
        "processing_status": "processing"
    }
    
    # 2. Add book to Firebase
    book_id = firebase_service.add_book(book_data, user_id)
    
    # 3. Save uploaded file to temporary location
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, file.filename)
    
    try:
        with open(temp_file_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
    finally:
        file.file.close()
    
    # 4. Process book in background
    background_tasks.add_task(
        process_book_background,
        temp_file_path,
        book_id,
        book_data,
        user_id,
        firebase_service,
        book_parser,
        embedding_service,
        vector_store,
        personality_extractor
    )
    
    return {"message": "Book upload started. Processing in background.", "book_id": book_id}
