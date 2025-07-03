from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Message(BaseModel):
    role: str  # 'user' or 'assistant'
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

class Character(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    personality_traits: Optional[List[str]] = None

class SourceChunk(BaseModel):
    text: str
    book_id: str
    page: Optional[int] = None
    chunk_id: str

class BookUploadResponse(BaseModel):
    message: str
    book_id: str
