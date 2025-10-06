"""
Connectors module for external API clients

This module provides singleton instances of external API clients:
- OpenAI/OpenRouter client for LLM operations
- Google GenAI client for video generation
- MongoDB client for database operations
"""

from app.connectors.openai_connector import get_openai_client
from app.connectors.genai_connector import get_genai_client
from app.connectors.mongodb_connector import get_mongodb_client, get_mongodb_database, get_collection

__all__ = ['get_openai_client', 'get_genai_client', 'get_mongodb_client', 'get_mongodb_database', 'get_collection']
