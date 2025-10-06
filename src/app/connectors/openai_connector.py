"""
OpenAI/OpenRouter API Connector

This module provides a singleton instance of the OpenAI client configured
to work with OpenRouter API for LLM operations (story generation, character analysis, etc.)
"""

from openai import OpenAI
from app.config.settings import settings

# Singleton instance
_openai_client = None


def get_openai_client() -> OpenAI:
    """
    Get or create the OpenAI client instance (singleton pattern)
    
    Returns:
        OpenAI: Configured OpenAI client instance for OpenRouter API
    """
    global _openai_client
    
    if _openai_client is None:
        _openai_client = OpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=settings.OPENAI_API_KEY
        )
        print("✅ OpenAI/OpenRouter client initialized")
    
    return _openai_client


def reset_openai_client():
    """
    Reset the OpenAI client instance (useful for testing or reconfiguration)
    """
    global _openai_client
    _openai_client = None
    print("🔄 OpenAI client reset")
