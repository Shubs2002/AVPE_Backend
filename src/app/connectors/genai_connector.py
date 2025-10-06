"""
Google GenAI API Connector

This module provides a singleton instance of the Google GenAI client
for video generation using Vertex AI Veo-3 model
"""

from google import genai
from app.config.settings import settings

# Singleton instance
_genai_client = None


def get_genai_client() -> genai.Client:
    """
    Get or create the Google GenAI client instance (singleton pattern)
    
    Returns:
        genai.Client: Configured Google GenAI client instance for Vertex AI
    """
    global _genai_client
    
    if _genai_client is None:
        _genai_client = genai.Client(
            api_key=settings.GOOGLE_STUDIO_API_KEY
        )
        print("✅ Google GenAI client initialized")
    
    return _genai_client


def reset_genai_client():
    """
    Reset the Google GenAI client instance (useful for testing or reconfiguration)
    """
    global _genai_client
    _genai_client = None
    print("🔄 Google GenAI client reset")
