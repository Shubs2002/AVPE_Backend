"""
Test MongoDB Connection Script

This script tests the MongoDB connection with your credentials.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from urllib.parse import quote_plus

# Load environment variables
load_dotenv('.env.dev')

def test_connection():
    """Test MongoDB connection"""
    
    # Get credentials from environment
    mongodb_uri = os.getenv('MONGODB_URI')
    mongodb_database = os.getenv('MONGODB_DATABASE', 'avpe_dev')
    
    print("=" * 60)
    print("MongoDB Connection Test")
    print("=" * 60)
    print(f"Database: {mongodb_database}")
    print(f"URI: {mongodb_uri[:50]}..." if len(mongodb_uri) > 50 else f"URI: {mongodb_uri}")
    print("=" * 60)
    
    try:
        # Test 1: Create client
        print("\n✓ Step 1: Creating MongoDB client...")
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        print("  ✅ Client created successfully")
        
        # Test 2: Ping server
        print("\n✓ Step 2: Pinging MongoDB server...")
        client.admin.command('ping')
        print("  ✅ Server responded to ping")
        
        # Test 3: Get database
        print(f"\n✓ Step 3: Connecting to database '{mongodb_database}'...")
        db = client[mongodb_database]
        print("  ✅ Database connection established")
        
        # Test 4: List collections
        print("\n✓ Step 4: Listing collections...")
        collections = db.list_collection_names()
        print(f"  ✅ Found {len(collections)} collections: {collections}")
        
        # Test 5: Test write operation
        print("\n✓ Step 5: Testing write operation...")
        test_collection = db['test_connection']
        result = test_collection.insert_one({"test": "connection", "timestamp": "2025-10-05"})
        print(f"  ✅ Write successful. Inserted ID: {result.inserted_id}")
        
        # Test 6: Test read operation
        print("\n✓ Step 6: Testing read operation...")
        doc = test_collection.find_one({"_id": result.inserted_id})
        print(f"  ✅ Read successful. Document: {doc}")
        
        # Test 7: Clean up
        print("\n✓ Step 7: Cleaning up test data...")
        test_collection.delete_one({"_id": result.inserted_id})
        print("  ✅ Test data cleaned up")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED! MongoDB is ready to use.")
        print("=" * 60)
        
        return True
        
    except ConnectionFailure as e:
        print(f"\n❌ Connection Error: {e}")
        print("\nPossible solutions:")
        print("1. Check if your IP address is whitelisted in MongoDB Atlas")
        print("2. Verify your internet connection")
        print("3. Check if MongoDB Atlas cluster is running")
        return False
        
    except OperationFailure as e:
        print(f"\n❌ Authentication Error: {e}")
        print("\nPossible solutions:")
        print("1. Verify username and password in .env.dev")
        print("2. Check if user has proper permissions in MongoDB Atlas")
        print("3. Try URL-encoding special characters in password")
        print("\nTo URL-encode password:")
        print("  from urllib.parse import quote_plus")
        print("  encoded_password = quote_plus('your_password')")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False
    
    finally:
        try:
            client.close()
            print("\n✓ MongoDB client closed")
        except:
            pass


def test_with_encoded_password():
    """Test connection with URL-encoded password"""
    
    print("\n" + "=" * 60)
    print("Testing with URL-encoded password...")
    print("=" * 60)
    
    username = "Shubhs28"
    password = "Shubham_2002"
    cluster = "cluster0.oqzah3n.mongodb.net"
    database = "avpe_dev"
    
    # URL encode the password
    encoded_password = quote_plus(password)
    
    # Build connection string
    uri = f"mongodb+srv://{username}:{encoded_password}@{cluster}/?retryWrites=true&w=majority&appName=Cluster0"
    
    print(f"Encoded password: {encoded_password}")
    print(f"Testing connection...")
    
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ Connection successful with encoded password!")
        
        db = client[database]
        collections = db.list_collection_names()
        print(f"✅ Database accessible. Collections: {collections}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Still failed: {e}")
        return False


if __name__ == "__main__":
    print("\n🔍 Starting MongoDB Connection Tests...\n")
    
    # Test 1: Standard connection
    success = test_connection()
    
    # Test 2: If failed, try with encoded password
    if not success:
        print("\n" + "=" * 60)
        print("Trying alternative connection method...")
        print("=" * 60)
        test_with_encoded_password()
    
    print("\n✅ Test script completed.\n")
