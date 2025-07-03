import os
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class PersonalityExtractor:
    """
    Service for extracting book and character personalities using Google's generative AI.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize personality extractor.
        
        Args:
            api_key: Google API key (defaults to environment variable GOOGLE_API_KEY)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("No Google API key provided. Personality extraction will be limited.")
            return
        
        # Configure Google Generative AI API
        genai.configure(api_key=self.api_key)
        
        # Use Gemini Pro model
        self.model = genai.GenerativeModel('gemini-pro')
    
    def extract_book_personality(self, text_sample: str, book_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract book personality from text.
        
        Args:
            text_sample: Sample of book text (first few chapters)
            book_metadata: Book metadata (title, author, etc.)
            
        Returns:
            Dictionary of personality traits and tone
        """
        if not self.api_key:
            logger.error("Cannot extract personality: No API key")
            return {"tone": "neutral", "personality_traits": []}
        
        try:
            # Create prompt for LLM
            prompt = f"""
            Book Title: {book_metadata.get('title', 'Unknown')}
            Author: {book_metadata.get('author', 'Unknown')}
            
            Analyze the following book text and extract the book's overall personality, tone, and writing style.
            Focus on consistent patterns and unique characteristics that define this book's voice.
            
            Text sample:
            {text_sample[:10000]}  # Limit sample size
            
            Output a JSON object with the following structure:
            {{
                "tone": "Primary tone of the book",
                "writing_style": "Brief description of writing style",
                "personality_traits": ["trait1", "trait2", "trait3", "trait4", "trait5"],
                "voice_characteristics": "How the book would 'speak' if it had a voice"
            }}
            """
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Parse response (assuming it returns valid JSON-like text)
            # In a real implementation, we'd need more robust parsing
            response_text = response.text
            
            # For now, return a simplified response
            if "personality_traits" in response_text:
                # Extract JSON from the response text
                import json
                import re
                
                # Find JSON pattern in response
                json_match = re.search(r'({[\s\S]*})', response_text)
                if json_match:
                    try:
                        personality_data = json.loads(json_match.group(1))
                        return personality_data
                    except json.JSONDecodeError:
                        logger.error("Failed to parse personality JSON")
            
            # Default response if parsing fails
            return {
                "tone": "neutral",
                "writing_style": "standard",
                "personality_traits": ["informative"],
                "voice_characteristics": "neutral and informative"
            }
            
        except Exception as e:
            logger.error(f"Error extracting book personality: {e}")
            return {
                "tone": "neutral",
                "personality_traits": []
            }
    
    def extract_characters(self, text_sample: str, book_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract main characters and their personalities from text.
        
        Args:
            text_sample: Sample of book text (first few chapters)
            book_metadata: Book metadata (title, author, etc.)
            
        Returns:
            List of character objects with personality traits
        """
        if not self.api_key:
            logger.error("Cannot extract characters: No API key")
            return []
        
        try:
            # Create prompt for LLM
            prompt = f"""
            Book Title: {book_metadata.get('title', 'Unknown')}
            Author: {book_metadata.get('author', 'Unknown')}
            
            Analyze the following book text and identify the main characters.
            For each character, extract their personality traits, speech patterns, and defining characteristics.
            
            Text sample:
            {text_sample[:15000]}  # Limit sample size
            
            Output a JSON array with the following structure for each character:
            [
                {{
                    "name": "Character Name",
                    "description": "Brief description",
                    "personality_traits": ["trait1", "trait2", "trait3"],
                    "speech_pattern": "How this character typically speaks"
                }},
                ... (up to 5 main characters)
            ]
            """
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Parse response
            response_text = response.text
            
            # Extract JSON from the response text
            import json
            import re
            
            # Find JSON pattern in response
            json_match = re.search(r'(\[[\s\S]*\])', response_text)
            if json_match:
                try:
                    characters_data = json.loads(json_match.group(1))
                    
                    # Add IDs to characters
                    for i, character in enumerate(characters_data):
                        character["id"] = f"char_{i}"
                    
                    return characters_data
                except json.JSONDecodeError:
                    logger.error("Failed to parse characters JSON")
            
            # Default empty list if parsing fails
            return []
            
        except Exception as e:
            logger.error(f"Error extracting characters: {e}")
            return []
