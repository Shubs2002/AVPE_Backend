"""
MongoDB Connector

This module provides a singleton instance of the MongoDB client
for database operations (character storage, etc.)
"""

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from app.config.settings import settings

# Singleton instance
_mongodb_client = None
_mongodb_database = None


def get_mongodb_client() -> MongoClient:
    """
    Get or create the MongoDB client instance (singleton pattern)
    
    Returns:
        MongoClient: Configured MongoDB client instance
    """
    global _mongodb_client
    
    if _mongodb_client is None:
        mongodb_uri = settings.MONGODB_URI
        
        if not mongodb_uri:
            raise ValueError("MONGODB_URI not configured in settings")
        
        _mongodb_client = MongoClient(mongodb_uri)
        print("✅ MongoDB client initialized")
    
    return _mongodb_client


def get_mongodb_database(database_name: str = None) -> Database:
    """
    Get the MongoDB database instance
    
    Args:
        database_name: Optional database name (defaults to settings.MONGODB_DATABASE)
    
    Returns:
        Database: MongoDB database instance
    """
    global _mongodb_database
    
    if _mongodb_database is None:
        client = get_mongodb_client()
        db_name = database_name or settings.MONGODB_DATABASE
        
        if not db_name:
            raise ValueError("MONGODB_DATABASE not configured in settings")
        
        _mongodb_database = client[db_name]
        print(f"✅ MongoDB database '{db_name}' connected")
    
    return _mongodb_database


def get_collection(collection_name: str) -> Collection:
    """
    Get a MongoDB collection
    
    Args:
        collection_name: Name of the collection
    
    Returns:
        Collection: MongoDB collection instance
    """
    database = get_mongodb_database()
    return database[collection_name]


def reset_mongodb_client():
    """
    Reset the MongoDB client instance (useful for testing or reconfiguration)
    """
    global _mongodb_client, _mongodb_database
    
    if _mongodb_client:
        _mongodb_client.close()
    
    _mongodb_client = None
    _mongodb_database = None
    print("🔄 MongoDB client reset")


def test_mongodb_connection() -> dict:
    """
    Test MongoDB connection
    
    Returns:
        dict: Connection test result
    """
    try:
        client = get_mongodb_client()
        # Ping the database
        client.admin.command('ping')
        
        database = get_mongodb_database()
        
        return {
            "success": True,
            "message": "MongoDB connection successful",
            "database": database.name,
            "collections": database.list_collection_names()
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"MongoDB connection failed: {str(e)}"
        }
