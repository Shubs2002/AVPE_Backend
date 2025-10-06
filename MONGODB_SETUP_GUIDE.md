# 🚀 MongoDB Setup Guide

## Quick Setup

### 1. Install MongoDB Python Driver

```bash
pip install pymongo
```

### 2. Configure Environment Variables

Add to your `.env` file:

```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=avpe_database
```

### 3. Start MongoDB

**Option A: Local MongoDB**
```bash
mongod
```

**Option B: MongoDB Atlas (Cloud)**
- Sign up at https://www.mongodb.com/cloud/atlas
- Create a cluster
- Get connection string
- Update `MONGODB_URI` in `.env`

### 4. Test Connection

```bash
curl -X GET "http://localhost:8000/characters/health/check"
```

## Installation Options

### Option 1: MongoDB Atlas (Recommended for Production)

1. **Sign Up**: https://www.mongodb.com/cloud/atlas
2. **Create Cluster**: Free tier available
3. **Get Connection String**:
   ```
   mongodb+srv://username:password@cluster.mongodb.net/
   ```
4. **Update `.env`**:
   ```env
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
   MONGODB_DATABASE=avpe_database
   ```

### Option 2: Local MongoDB

**Windows:**
```bash
# Download installer
https://www.mongodb.com/try/download/community

# Or use Chocolatey
choco install mongodb

# Start MongoDB
mongod
```

**Mac:**
```bash
# Install via Homebrew
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB
brew services start mongodb-community
```

**Linux (Ubuntu/Debian):**
```bash
# Import MongoDB public key
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Install MongoDB
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
```

### Option 3: Docker

```bash
# Pull MongoDB image
docker pull mongo

# Run MongoDB container
docker run -d -p 27017:27017 --name mongodb mongo

# Update .env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=avpe_database
```

## Configuration Examples

### Development (.env.dev)
```env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=avpe_dev
```

### Production (.env.prod)
```env
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DATABASE=avpe_prod
```

### With Authentication
```env
MONGODB_URI=mongodb://username:password@localhost:27017/
MONGODB_DATABASE=avpe_database
```

## Verify Setup

### 1. Check MongoDB is Running

```bash
# Local MongoDB
mongo --eval "db.version()"

# Or check process
ps aux | grep mongod
```

### 2. Test API Connection

```bash
curl -X GET "http://localhost:8000/characters/health/check"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "MongoDB connection successful",
  "database": "avpe_database",
  "collections": []
}
```

### 3. Create First Character

```bash
curl -X POST "http://localhost:8000/analyze-character-image-file" \
  -F "image=@test.jpg" \
  -F "character_name=Test" \
  -F "save_character=true"
```

### 4. List Characters

```bash
curl -X GET "http://localhost:8000/characters"
```

## Troubleshooting

### Error: Connection Refused

**Problem:** MongoDB not running

**Solution:**
```bash
# Start MongoDB
mongod

# Or with systemd
sudo systemctl start mongod
```

### Error: Authentication Failed

**Problem:** Wrong credentials

**Solution:**
- Check username/password in `MONGODB_URI`
- Verify user has correct permissions

### Error: Database Not Found

**Problem:** Database doesn't exist

**Solution:**
- MongoDB creates database automatically on first write
- Just start using the API

### Error: Module 'pymongo' Not Found

**Problem:** Python driver not installed

**Solution:**
```bash
pip install pymongo
```

## MongoDB Tools

### MongoDB Compass (GUI)

Download: https://www.mongodb.com/products/compass

- Visual database browser
- Query builder
- Index management
- Performance monitoring

### MongoDB Shell

```bash
# Connect to local MongoDB
mongo

# Connect to specific database
mongo avpe_database

# List databases
show dbs

# List collections
show collections

# Query characters
db.characters.find().pretty()
```

## Security Best Practices

### 1. Use Authentication

```env
MONGODB_URI=mongodb://username:password@localhost:27017/
```

### 2. Use SSL/TLS (Production)

```env
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/?ssl=true
```

### 3. Restrict Network Access

- Use firewall rules
- Whitelist IP addresses
- Use VPN for remote access

### 4. Regular Backups

```bash
# Backup database
mongodump --db avpe_database --out /backup/

# Restore database
mongorestore --db avpe_database /backup/avpe_database/
```

## Performance Tips

### 1. Indexes

Indexes are created automatically by the application:
- `character_name`
- `character_data.name`
- `created_at`
- Text index for search

### 2. Connection Pooling

The connector uses singleton pattern for efficient connection reuse.

### 3. Pagination

Always use pagination for large result sets:
```bash
curl "http://localhost:8000/characters?skip=0&limit=20"
```

## Monitoring

### Check Database Stats

```javascript
// In MongoDB shell
use avpe_database
db.stats()
```

### Check Collection Stats

```javascript
db.characters.stats()
```

### Monitor Queries

```javascript
db.setProfilingLevel(2)  // Log all queries
db.system.profile.find().pretty()
```

## Migration from Files

### Migrate Existing Characters

```python
import json
import os
import requests

# Read from saved_characters folder
for filename in os.listdir('saved_characters'):
    if filename.endswith('.json'):
        with open(f'saved_characters/{filename}', 'r') as f:
            data = json.load(f)
        
        character_data = data.get('character_data', {})
        character_name = data.get('metadata', {}).get('character_name', 'Unknown')
        
        # Save to MongoDB via API
        response = requests.post(
            'http://localhost:8000/analyze-character-image-file',
            files={'image': open('placeholder.jpg', 'rb')},
            data={
                'character_name': character_name,
                'save_character': True
            }
        )
        
        print(f"Migrated: {character_name}")
```

## Quick Commands

```bash
# Install driver
pip install pymongo

# Start MongoDB (local)
mongod

# Test connection
curl http://localhost:8000/characters/health/check

# List characters
curl http://localhost:8000/characters

# Search characters
curl -X POST http://localhost:8000/characters/search \
  -H "Content-Type: application/json" \
  -d '{"query": "hero"}'
```

## Support

### MongoDB Documentation
- https://docs.mongodb.com/

### MongoDB University (Free Courses)
- https://university.mongodb.com/

### Community
- https://community.mongodb.com/

---

**Setup Guide Version:** 1.0  
**Last Updated:** 2025-10-05  
**Status:** ✅ Ready to Use
