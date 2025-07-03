import os
import json
import logging
from typing import List, Dict, Any, Optional
import firebase_admin
from firebase_admin import credentials, firestore, storage, auth
from google.cloud.firestore_v1.base_query import FieldFilter
from dotenv import load_dotenv

# Import mock service for testing
from .mock_firebase import MockFirebaseService

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class FirebaseService:
    """
    Service for interacting with Firebase (Auth, Firestore, Storage).
    """
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Firebase service.
        
        Args:
            credentials_path: Path to Firebase credentials JSON file
        """
        # Get credentials path from environment if not provided
        credentials_path = credentials_path or os.getenv("FIREBASE_CREDENTIALS_PATH")
        
        # Check if we should use mock implementation
        use_mock = os.getenv("USE_MOCK_FIREBASE", "False").lower() in ("true", "1", "t")
        
        if use_mock or not credentials_path or not os.path.exists(credentials_path):
            logger.warning("Using mock Firebase implementation for testing")
            self.mock_service = MockFirebaseService()
            self.using_mock = True
            return
        
        # Use real Firebase implementation
        self.using_mock = False
        
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred)
            except Exception as e:
                logger.error(f"Error initializing Firebase: {e}")
                logger.warning("Falling back to mock Firebase implementation")
                self.mock_service = MockFirebaseService()
                self.using_mock = True
                return
        
        self.db = firestore.client()
        self.bucket = storage.bucket()
    
    # --- User Management ---
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user data from Firebase Auth.
        
        Args:
            user_id: Firebase user ID
            
        Returns:
            User data or None if not found
        """
        if self.using_mock:
            # Use mock implementation
            return {"uid": user_id, "email": f"{user_id}@example.com", "display_name": f"Test User {user_id}"}
        
        try:
            user = auth.get_user(user_id)
            return {
                "uid": user.uid,
                "email": user.email,
                "display_name": user.display_name
            }
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    def verify_token(self, token: str) -> Optional[str]:
        """
        Verify Firebase ID token and return user ID.
        
        Args:
            token: Firebase ID token
            
        Returns:
            User ID or None if invalid
        """
        if self.using_mock:
            # Use mock implementation
            return self.mock_service.verify_token(token)
        
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token.get("uid")
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
    
    # --- Book Management ---
    
    def list_books(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available books (public books + user's private books).
        
        Args:
            user_id: Optional user ID for including private books
            
        Returns:
            List of book metadata
        """
        if self.using_mock:
            # Use mock implementation
            return self.mock_service.list_books(user_id)
        
        books = []
        
        # Get public books
        query = self.db.collection("books").where(filter=FieldFilter("is_public", "==", True))
        for doc in query.stream():
            books.append({**doc.to_dict(), "id": doc.id})
        
        # If user_id provided, get their private books
        if user_id:
            query = self.db.collection("books").where(filter=FieldFilter("owner_id", "==", user_id))
            for doc in query.stream():
                # Only add if not already in list (to avoid duplicates)
                if not any(book["id"] == doc.id for book in books):
                    books.append({**doc.to_dict(), "id": doc.id})
        
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
        if self.using_mock:
            # Use mock implementation
            return self.mock_service.get_book(book_id, user_id)
        
        doc_ref = self.db.collection("books").document(book_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
        
        book_data = {**doc.to_dict(), "id": doc.id}
        
        # Check access
        if not book_data.get("is_public", False) and book_data.get("owner_id") != user_id:
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
        if self.using_mock:
            # Use mock implementation
            return self.mock_service.add_book(book_data, user_id)
        
        # Add owner ID and timestamp
        book_data["owner_id"] = user_id
        book_data["created_at"] = firestore.SERVER_TIMESTAMP
        
        # Add to Firestore
        doc_ref = self.db.collection("books").document()
        doc_ref.set(book_data)
        
        return doc_ref.id
    
    def update_book(self, book_id: str, book_data: Dict[str, Any]) -> bool:
        """
        Update book metadata.
        
        Args:
            book_id: Book ID
            book_data: Updated book data
            
        Returns:
            True if successful, False otherwise
        """
        if self.using_mock:
            # Use mock implementation
            return self.mock_service.update_book(book_id, book_data)
        
        try:
            doc_ref = self.db.collection("books").document(book_id)
            doc_ref.update(book_data)
            return True
        except Exception as e:
            logger.error(f"Error updating book {book_id}: {e}")
            return False

    # --- File Storage ---
    
    def upload_file(self, file_path: str, destination_path: str) -> str:
        """
        Upload a file to Firebase Storage.
        
        Args:
            file_path: Local file path
            destination_path: Storage destination path
            
        Returns:
            Public URL of the uploaded file
        """
        blob = self.bucket.blob(destination_path)
        blob.upload_from_filename(file_path)
        
        # Make public and return URL
        blob.make_public()
        return blob.public_url
    
    def download_file(self, storage_path: str, destination_path: str) -> bool:
        """
        Download a file from Firebase Storage.
        
        Args:
            storage_path: Storage path
            destination_path: Local destination path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            blob = self.bucket.blob(storage_path)
            blob.download_to_filename(destination_path)
            return True
        except Exception as e:
            logger.error(f"Error downloading file {storage_path}: {e}")
            return False
