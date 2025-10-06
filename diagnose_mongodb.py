"""
Detailed MongoDB Diagnostics

This script provides detailed diagnostics for MongoDB connection issues.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, ServerSelectionTimeoutError
from urllib.parse import quote_plus, urlparse
import sys

# Load environment variables
load_dotenv('.env.dev')

def parse_connection_string(uri):
    """Parse and display connection string details"""
    print("\n" + "=" * 60)
    print("CONNECTION STRING ANALYSIS")
    print("=" * 60)
    
    try:
        parsed = urlparse(uri)
        print(f"Scheme: {parsed.scheme}")
        print(f"Username: {parsed.username}")
        print(f"Password: {'*' * len(parsed.password) if parsed.password else 'None'}")
        print(f"Hostname: {parsed.hostname}")
        print(f"Port: {parsed.port or 'default'}")
        print(f"Path: {parsed.path}")
        print(f"Query: {parsed.query}")
        
        # Check for special characters in password
        if parsed.password:
            special_chars = ['@', ':', '/', '?', '#', '[', ']', '!', '$', '&', "'", '(', ')', '*', '+', ',', ';', '=', '%']
            found_special = [char for char in special_chars if char in parsed.password]
            if found_special:
                print(f"\n⚠️  WARNING: Password contains special characters: {found_special}")
                print("   These should be URL-encoded!")
                encoded_pass = quote_plus(parsed.password)
                print(f"   Encoded password: {encoded_pass}")
        
    except Exception as e:
        print(f"Error parsing URI: {e}")


def test_different_auth_methods():
    """Try different authentication methods"""
    
    username = "Shubhs28"
    password = "Shubham_2002"
    cluster = "cluster0.oqzah3n.mongodb.net"
    
    print("\n" + "=" * 60)
    print("TESTING DIFFERENT CONNECTION METHODS")
    print("=" * 60)
    
    # Method 1: Standard connection
    print("\n1️⃣  Testing standard connection...")
    uri1 = f"mongodb+srv://{username}:{password}@{cluster}/?retryWrites=true&w=majority"
    try:
        client = MongoClient(uri1, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("   ✅ SUCCESS with standard connection!")
        client.close()
        return uri1
    except Exception as e:
        print(f"   ❌ Failed: {type(e).__name__}")
    
    # Method 2: URL-encoded password
    print("\n2️⃣  Testing with URL-encoded password...")
    encoded_password = quote_plus(password)
    uri2 = f"mongodb+srv://{username}:{encoded_password}@{cluster}/?retryWrites=true&w=majority"
    try:
        client = MongoClient(uri2, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("   ✅ SUCCESS with URL-encoded password!")
        client.close()
        return uri2
    except Exception as e:
        print(f"   ❌ Failed: {type(e).__name__}")
    
    # Method 3: Without appName
    print("\n3️⃣  Testing without appName parameter...")
    uri3 = f"mongodb+srv://{username}:{password}@{cluster}/"
    try:
        client = MongoClient(uri3, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("   ✅ SUCCESS without appName!")
        client.close()
        return uri3
    except Exception as e:
        print(f"   ❌ Failed: {type(e).__name__}")
    
    # Method 4: With authSource
    print("\n4️⃣  Testing with authSource=admin...")
    uri4 = f"mongodb+srv://{username}:{password}@{cluster}/?authSource=admin"
    try:
        client = MongoClient(uri4, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("   ✅ SUCCESS with authSource!")
        client.close()
        return uri4
    except Exception as e:
        print(f"   ❌ Failed: {type(e).__name__}")
    
    # Method 5: Direct connection (non-SRV)
    print("\n5️⃣  Testing direct connection (non-SRV)...")
    uri5 = f"mongodb://{username}:{password}@cluster0-shard-00-00.oqzah3n.mongodb.net:27017,cluster0-shard-00-01.oqzah3n.mongodb.net:27017,cluster0-shard-00-02.oqzah3n.mongodb.net:27017/?ssl=true&replicaSet=atlas-123456-shard-0&authSource=admin"
    try:
        client = MongoClient(uri5, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("   ✅ SUCCESS with direct connection!")
        client.close()
        return uri5
    except Exception as e:
        print(f"   ❌ Failed: {type(e).__name__}")
    
    return None


def check_network_connectivity():
    """Check if we can reach MongoDB Atlas"""
    print("\n" + "=" * 60)
    print("NETWORK CONNECTIVITY CHECK")
    print("=" * 60)
    
    import socket
    
    hosts = [
        ("cluster0.oqzah3n.mongodb.net", 27017),
        ("cluster0-shard-00-00.oqzah3n.mongodb.net", 27017),
    ]
    
    for host, port in hosts:
        try:
            print(f"\nTesting connection to {host}:{port}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"   ✅ Can reach {host}:{port}")
            else:
                print(f"   ❌ Cannot reach {host}:{port} (error code: {result})")
        except Exception as e:
            print(f"   ❌ Error: {e}")


def main():
    """Main diagnostic function"""
    
    print("\n" + "=" * 60)
    print("🔍 MONGODB ATLAS DETAILED DIAGNOSTICS")
    print("=" * 60)
    
    # Get URI from environment
    mongodb_uri = os.getenv('MONGODB_URI')
    
    if not mongodb_uri:
        print("❌ ERROR: MONGODB_URI not found in .env.dev")
        return
    
    print(f"\nLoaded URI from .env.dev")
    print(f"URI: {mongodb_uri[:50]}...")
    
    # Parse connection string
    parse_connection_string(mongodb_uri)
    
    # Check network connectivity
    check_network_connectivity()
    
    # Try different authentication methods
    working_uri = test_different_auth_methods()
    
    # Summary
    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    if working_uri:
        print(f"\n✅ FOUND WORKING CONNECTION!")
        print(f"\nWorking URI:")
        print(f"{working_uri}")
        print(f"\n💡 Update your .env.dev with this URI")
    else:
        print("\n❌ ALL CONNECTION METHODS FAILED")
        print("\n🔍 Possible Issues:")
        print("   1. Username or password is incorrect")
        print("   2. User doesn't exist in MongoDB Atlas")
        print("   3. User doesn't have proper database permissions")
        print("   4. IP address is not whitelisted")
        print("   5. MongoDB Atlas cluster is paused or deleted")
        print("\n📋 Next Steps:")
        print("   1. Login to MongoDB Atlas: https://cloud.mongodb.com/")
        print("   2. Go to 'Database Access' and verify user exists")
        print("   3. Go to 'Network Access' and add your IP (or 0.0.0.0/0)")
        print("   4. Check cluster status in 'Database' section")
        print("   5. Try creating a new database user with a simple password")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
