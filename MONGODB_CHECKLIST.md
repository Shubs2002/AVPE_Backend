# ✅ MongoDB Atlas Connection Checklist

## Current Status: ❌ Authentication Failed

All connection attempts are failing. Here's what to check:

## 🔍 Checklist

### 1. Verify MongoDB Atlas User

- [ ] Login to https://cloud.mongodb.com/
- [ ] Click on your project
- [ ] Go to **"Database Access"** (left sidebar)
- [ ] Check if user **"Shubhs28"** exists
- [ ] If exists, verify it has permissions (should be "Atlas Admin" or "Read and write to any database")
- [ ] If doesn't exist, **CREATE NEW USER**

### 2. Check Network Access (IP Whitelist)

- [ ] In MongoDB Atlas, go to **"Network Access"** (left sidebar)
- [ ] Check if your IP is whitelisted
- [ ] **Recommended**: Add `0.0.0.0/0` (Allow from anywhere) for testing
- [ ] Click "Add IP Address" → "Allow Access from Anywhere" → "Confirm"

### 3. Verify Cluster Status

- [ ] Go to **"Database"** (left sidebar)
- [ ] Check if **Cluster0** is running (should show green "Active")
- [ ] If paused, click "Resume"
- [ ] If deleted, you'll need to create a new cluster

### 4. Test with MongoDB Compass (GUI Tool)

Download MongoDB Compass: https://www.mongodb.com/products/compass

- [ ] Install MongoDB Compass
- [ ] Open Compass
- [ ] Paste your connection string:
  ```
  mongodb+srv://Shubhs28:Shubham_2002@cluster0.oqzah3n.mongodb.net/
  ```
- [ ] Click "Connect"
- [ ] If it works in Compass, the issue is with Python code
- [ ] If it fails in Compass, the credentials are wrong

### 5. Create New Test User (Recommended)

To isolate the issue, create a fresh user:

1. In MongoDB Atlas → **Database Access**
2. Click **"Add New Database User"**
3. Fill in:
   - **Username**: `avpe_test`
   - **Password**: `TestPass123` (simple, no special chars)
   - **Authentication Method**: Password
   - **Database User Privileges**: Atlas Admin
4. Click **"Add User"**
5. Update `.env.dev`:
   ```env
   MONGODB_URI=mongodb+srv://avpe_test:TestPass123@cluster0.oqzah3n.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
   ```
6. Test: `poetry run python test_mongodb_connection.py`

## 🔧 Alternative: Use Local MongoDB

If MongoDB Atlas continues to fail, use local MongoDB for development:

### Windows:
```bash
# Install
choco install mongodb

# Start
mongod

# Update .env.dev
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=avpe_dev

# Test
poetry run python test_mongodb_connection.py
```

### Mac:
```bash
# Install
brew install mongodb-community

# Start
brew services start mongodb-community

# Update .env.dev
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=avpe_dev

# Test
poetry run python test_mongodb_connection.py
```

## 📞 Get Help from MongoDB Atlas

If nothing works:

1. **Check MongoDB Atlas Status**: https://status.mongodb.com/
2. **Contact Support**: In Atlas, click "?" → "Contact Support"
3. **Community Forums**: https://community.mongodb.com/

## 🎯 Most Likely Issues

Based on the diagnostics:

### Issue #1: Wrong Credentials (90% likely)
- **Symptom**: `bad auth : authentication failed`
- **Solution**: Verify username/password in MongoDB Atlas
- **Action**: Create new user with simple password

### Issue #2: IP Not Whitelisted (5% likely)
- **Symptom**: Connection timeout or network errors
- **Solution**: Add IP to Network Access
- **Action**: Add 0.0.0.0/0 in Network Access

### Issue #3: Cluster Paused/Deleted (5% likely)
- **Symptom**: Cannot connect at all
- **Solution**: Resume or recreate cluster
- **Action**: Check cluster status in Database section

## ✅ Success Criteria

When everything works, you should see:

```bash
poetry run python test_mongodb_connection.py
```

Output:
```
✅ ALL TESTS PASSED! MongoDB is ready to use.
```

## 🚀 Once Working

After successful connection:

1. Start your FastAPI app
2. Test character endpoints:
   ```bash
   curl http://localhost:8000/characters/health/check
   ```
3. Create a character:
   ```bash
   curl -X POST http://localhost:8000/analyze-character-image-file \
     -F "image=@test.jpg" \
     -F "character_name=Test" \
     -F "save_character=true"
   ```

---

**Current Issue**: Authentication failing  
**Most Likely Cause**: Wrong username/password  
**Recommended Action**: Create new user in MongoDB Atlas with simple password  
**Alternative**: Use local MongoDB for development
