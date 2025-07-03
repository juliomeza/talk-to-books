from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Header, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="BookTalk API", description="API for BookTalk - AI-Powered Conversational Book Companion")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    book_ids: List[str]
    messages: List[Message]
    character_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    sources: List[Dict[str, Any]]

class BookMetadata(BaseModel):
    id: str
    title: str
    author: str
    description: str
    cover_image: Optional[str] = None
    is_public: bool = True
    characters: Optional[List[Dict[str, str]]] = None

# --- Routes ---
@app.get("/")
async def root():
    return {"message": "Welcome to BookTalk API"}

@app.get("/books", response_model=List[BookMetadata])
async def list_books(token: Optional[str] = Header(None)):
    """
    List available books.
    If authenticated, includes user's private books.
    """
    # Mock data for now
    return [
        {
            "id": "book1",
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "description": "A classic novel of manners",
            "cover_image": "https://example.com/pride.jpg",
            "is_public": True,
            "characters": [
                {"id": "elizabeth", "name": "Elizabeth Bennet"},
                {"id": "darcy", "name": "Mr. Darcy"}
            ]
        },
        {
            "id": "book2",
            "title": "Dracula",
            "author": "Bram Stoker",
            "description": "The classic vampire tale",
            "cover_image": "https://example.com/dracula.jpg",
            "is_public": True,
            "characters": [
                {"id": "dracula", "name": "Count Dracula"},
                {"id": "harker", "name": "Jonathan Harker"}
            ]
        }
    ]

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, token: Optional[str] = Header(None)):
    """
    Chat with a book or character.
    Uses RAG to generate responses from book content.
    """
    # This would use FAISS to retrieve relevant passages and generate a response
    # For now, return mock data
    return {
        "message": "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.",
        "sources": [
            {
                "text": "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.",
                "book_id": "book1",
                "page": 1,
                "chunk_id": "b1c1"
            }
        ]
    }

@app.post("/books/upload")
async def upload_book(
    file: UploadFile = File(...),
    title: str = Form(...),
    author: str = Form(...),
    description: str = Form(...),
    is_public: bool = Form(False),
    token: Optional[str] = Header(None)
):
    """
    Upload a new book.
    Processes the file and generates embeddings.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Process would include:
    # 1. Save the file
    # 2. Extract text content
    # 3. Generate embeddings
    # 4. Extract personality information
    # 5. Store in Firebase/FAISS
    
    return {"message": "Book uploaded successfully", "book_id": "new_book_id"}

@app.get("/books/{book_id}")
async def get_book(book_id: str, token: Optional[str] = Header(None)):
    """
    Get details about a specific book.
    """
    # This would retrieve book data from Firebase
    # Mock data for now
    if book_id == "book1":
        return {
            "id": "book1",
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "description": "A classic novel of manners",
            "cover_image": "https://example.com/pride.jpg",
            "is_public": True,
            "characters": [
                {"id": "elizabeth", "name": "Elizabeth Bennet"},
                {"id": "darcy", "name": "Mr. Darcy"}
            ]
        }
    else:
        raise HTTPException(status_code=404, detail="Book not found")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
