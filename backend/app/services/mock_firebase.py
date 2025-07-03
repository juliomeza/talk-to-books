"""
Mock Firebase service for testing.
This module provides a mock implementation of the Firebase service for testing.
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class MockFirebaseService:
    """
    Mock implementation of the Firebase service for testing.
    """
    
    def __init__(self):
        """
        Initialize mock Firebase service.
        """
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.users = {}
        self.books = self._load_books()
    
    def _load_books(self) -> Dict[str, Dict[str, Any]]:
        """Load books from data directory."""
        books = {}
        
        # Try to load books from JSON files
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json") and not filename.startswith("user_"):
                book_id = filename.replace(".json", "")
                try:
                    with open(os.path.join(self.data_dir, filename), "r") as f:
                        book_data = json.load(f)
                        books[book_id] = book_data
                except Exception as e:
                    logger.error(f"Error loading book {book_id}: {e}")
        
        # If no books found, create default mock books
        if not books:
            books = {
                "mock_book_1": {
                    "id": "mock_book_1",
                    "title": "Pride and Prejudice",
                    "author": "Jane Austen",
                    "description": "A classic novel of manners by Jane Austen.",
                    "is_public": True,
                    "characters": [
                        {"id": "elizabeth", "name": "Elizabeth Bennet"},
                        {"id": "darcy", "name": "Mr. Darcy"}
                    ]
                },
                "mock_book_2": {
                    "id": "mock_book_2",
                    "title": "Dracula",
                    "author": "Bram Stoker",
                    "description": "The classic vampire tale.",
                    "is_public": True,
                    "characters": [
                        {"id": "dracula", "name": "Count Dracula"},
                        {"id": "harker", "name": "Jonathan Harker"}
                    ]
                }
            }
            
            # Save mock books
            for book_id, book_data in books.items():
                with open(os.path.join(self.data_dir, f"{book_id}.json"), "w") as f:
                    json.dump(book_data, f, indent=2)
        
        return books
    
    def verify_token(self, token: str) -> Optional[str]:
        """
        Verify Firebase ID token and return user ID.
        
        Args:
            token: Firebase ID token
            
        Returns:
            User ID or None if invalid
        """
        # For testing, accept any token
        if token and token != "invalid_token":
            return "test_user_id"
        return None
    
    def list_books(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available books (public books + user's private books).
        
        Args:
            user_id: Optional user ID for including private books
            
        Returns:
            List of book metadata
        """
        books = []
        
        # Add public books
        for book_id, book_data in self.books.items():
            if book_data.get("is_public", True):
                books.append(book_data)
        
        # Add private books belonging to the user
        if user_id:
            for book_id, book_data in self.books.items():
                if not book_data.get("is_public", True) and book_data.get("owner_id") == user_id:
                    if not any(book["id"] == book_id for book in books):
                        books.append(book_data)
        
        return books
    
    def get_book(self, book_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get book metadata.
        
        Args:
            book_id: Book ID
            user_id: Optional user ID for access control
            
        Returns:
            Book metadata or None if not found or no access
        """
        book_data = self.books.get(book_id)
        
        if not book_data:
            return None
        
        # Check access
        if not book_data.get("is_public", True) and book_data.get("owner_id") != user_id:
            return None
        
        return book_data
    
    def add_book(self, book_data: Dict[str, Any], user_id: str) -> str:
        """
        Add a new book.
        
        Args:
            book_data: Book metadata
            user_id: User ID (owner)
            
        Returns:
            Book ID
        """
        # Generate a new ID
        book_id = f"book_{len(self.books) + 1}"
        
        # Add owner ID
        book_data["owner_id"] = user_id
        book_data["id"] = book_id
        
        # Add to books dictionary
        self.books[book_id] = book_data
        
        # Save to file
        with open(os.path.join(self.data_dir, f"{book_id}.json"), "w") as f:
            json.dump(book_data, f, indent=2)
        
        return book_id
    
    def update_book(self, book_id: str, book_data: Dict[str, Any]) -> bool:
        """
        Update book metadata.
        
        Args:
            book_id: Book ID
            book_data: Updated book data
            
        Returns:
            True if successful, False otherwise
        """
        if book_id not in self.books:
            return False
        
        # Update book data
        self.books[book_id].update(book_data)
        
        # Save to file
        with open(os.path.join(self.data_dir, f"{book_id}.json"), "w") as f:
            json.dump(self.books[book_id], f, indent=2)
        
        return True
