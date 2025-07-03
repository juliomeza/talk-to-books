import os
import logging
import json
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from app.services.vector_store import FAISSVectorStore
from app.services.embedding_service import EmbeddingService
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class RAGService:
    """
    Service for implementing the Retrieval-Augmented Generation (RAG) pipeline.
    """
    
    def __init__(
        self,
        vector_store: FAISSVectorStore,
        embedding_service: EmbeddingService,
        api_key: Optional[str] = None
    ):
        """
        Initialize RAG service.
        
        Args:
            vector_store: Vector store for retrieving book chunks
            embedding_service: Service for generating embeddings
            api_key: Google API key (defaults to environment variable GOOGLE_API_KEY)
        """
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            logger.warning("No Google API key provided. RAG functionality will be limited.")
            return
        
        # Configure Google Generative AI API
        genai.configure(api_key=self.api_key)
        
        # Use Gemini Pro model
        self.model = genai.GenerativeModel('gemini-pro')
    
    def retrieve_chunks(
        self,
        query: str,
        book_ids: List[str],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks from books.
        
        Args:
            query: User query
            book_ids: List of book IDs to search in
            top_k: Number of chunks to retrieve
            
        Returns:
            List of relevant chunks with metadata
        """
        # Generate embedding for query
        query_embedding = self.embedding_service.generate_embedding(query)
        if not query_embedding:
            logger.error("Failed to generate embedding for query")
            return []
        
        # Search for relevant chunks
        chunks = self.vector_store.search(
            query_embedding=query_embedding,
            book_ids=book_ids,
            top_k=top_k
        )
        
        return chunks
    
    def generate_response(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        character_id: Optional[str] = None,
        book_personalities: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate response based on retrieved chunks.
        
        Args:
            query: User query
            chunks: Retrieved chunks
            character_id: Optional character ID for personality
            book_personalities: Optional list of book personality data
            
        Returns:
            Response with message and source chunks
        """
        if not self.api_key:
            logger.error("Cannot generate response: No API key")
            return {
                "message": "I don't have enough information to answer that question based on the selected books.",
                "sources": []
            }
        
        if not chunks:
            return {
                "message": "I don't have enough information to answer that question based on the selected books.",
                "sources": []
            }
        
        try:
            # Prepare context from chunks
            context = "\n\n".join([f"Source {i+1}:\n{chunk['text']}" for i, chunk in enumerate(chunks)])
            
            # Prepare personality information
            personality_info = ""
            if character_id and book_personalities:
                # Find character in any of the book personalities
                for book in book_personalities:
                    characters = book.get("characters", [])
                    for character in characters:
                        if character.get("id") == character_id:
                            personality_info = f"""
                            You are responding as the character: {character.get('name')}
                            Character description: {character.get('description', '')}
                            Personality traits: {', '.join(character.get('personality_traits', []))}
                            Speech pattern: {character.get('speech_pattern', '')}
                            """
                            break
            elif book_personalities:
                # Use the first book's personality
                book = book_personalities[0]
                personality = book.get("personality", {})
                personality_info = f"""
                You are responding with the tone and style of the book.
                Tone: {personality.get('tone', 'neutral')}
                Writing style: {personality.get('writing_style', 'standard')}
                Personality traits: {', '.join(personality.get('personality_traits', []))}
                Voice characteristics: {personality.get('voice_characteristics', '')}
                """
            
            # Create prompt for LLM
            prompt = f"""
            {personality_info}
            
            You are an AI assistant that answers questions based strictly on the following text sources from books.
            You must only use information from these sources to answer the question.
            If the sources don't contain relevant information, say you don't have enough information to answer.
            
            SOURCES:
            {context}
            
            USER QUESTION: {query}
            
            Answer the question based only on the provided sources. Be accurate, informative, and maintain the appropriate tone.
            """
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            return {
                "message": response.text,
                "sources": chunks
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "message": "I encountered an error while trying to answer your question. Please try again.",
                "sources": chunks
            }
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        book_ids: List[str],
        character_id: Optional[str] = None,
        book_personalities: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Chat with books using RAG.
        
        Args:
            messages: List of messages (role and content)
            book_ids: List of book IDs to search in
            character_id: Optional character ID for personality
            book_personalities: Optional list of book personality data
            
        Returns:
            Response with message and source chunks
        """
        # Get the last user message as the query
        user_messages = [msg for msg in messages if msg["role"] == "user"]
        if not user_messages:
            return {
                "message": "No user message found",
                "sources": []
            }
        
        query = user_messages[-1]["content"]
        
        # Retrieve relevant chunks
        chunks = self.retrieve_chunks(query, book_ids)
        
        # Generate response
        return self.generate_response(query, chunks, character_id, book_personalities)
