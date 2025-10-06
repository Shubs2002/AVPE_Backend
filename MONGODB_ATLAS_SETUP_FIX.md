# 🔧 MongoDB Atlas Authentication Fix

## Problem

Authentication is failing with error: `bad auth : authentication failed`

## Solutions

### Option 1: Verify/Update MongoDB Atlas Credentials

1. **Go to MongoDB Atlas**: https://cloud.mongodb.com/
2. **Login** to your account
3. **Select your cluster** (Cluster0)
4. **Click "Database Access"** in the left sidebar
5. **Check if user exists**:
   - Look for user: `Shubhs28`
   - If not found, create a new user

### Option 2: Create New Database User

1. **In MongoDB Atlas**, go to **Database Access**
2. **Click "Add New Database User"**
3. **Fill in details**:
   - Username: `avpe_user` (or any name you prefer)
   - Password: Create a strong password (avoid special characters for now)
   - Authentication Method: Password
4. **Set Permissions**:
   - Built-in Role: **Atlas Admin** (or **Read and write to any database**)
5. **Click "Add User"**
6. **Update your `.env.dev` file** with new credentials

### Option 3: Reset Existing User Password

1. **In MongoDB Atlas**, go to **Database Access**
2. **Find user** `Shubhs28`
3. **Click "Edit"**
4. **Click "Edit Password"**
5. **Set new password** (avoid special characters like `_` for now)
6. **Click "Update User"**
7. **Update `.env.dev`** with new password

### Option 4: Check IP Whitelist

1. **In MongoDB Atlas**, go to **Network Access**
2. **Check if your IP is whitelisted**
3. **Add your current IP** or use `0.0.0.0/0` (allow from anywhere - for development only!)
4. **Click "Confirm"**

### Option 5: Use Simple Password (Testing)

For testing, use a simple password without special characters:

1. **Create new user** with simple password like: `password123`
2. **Update `.env.dev`**:
   ```env
   MONGODB_URI=mongodb+srv://testuser:password123@cluster0.oqzah3n.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
   MONGODB_DATABASE=avpe_dev
   ```
3. **Test connection**:
   ```bash
   poetry run python test_mongodb_connection.py
   ```

## Recommended Setup

### Step-by-Step Guide

#### 1. Create New Database User

```
Username: avpe_backend
Password: AvpeBackend2025!
Role: Atlas Admin
```

#### 2. Whitelist IP Address

- Go to **Network Access**
- Click **Add IP Address**
- Choose **Allow Access from Anywhere** (0.0.0.0/0)
- Or add your specific IP

#### 3. Update .env.dev

```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://avpe_backend:AvpeBackend2025!@cluster0.oqzah3n.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
MONGODB_DATABASE=avpe_dev
```

#### 4. If Password Has Special Characters

URL-encode the password:

```python
from urllib.parse import quote_plus
password = "AvpeBackend2025!"
encoded = quote_plus(password)
print(encoded)  # AvpeBackend2025%21
```

Then use in URI:
```env
MONGODB_URI=mongodb+srv://avpe_backend:AvpeBackend2025%21@cluster0.oqzah3n.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
```

#### 5. Test Connection

```bash
poetry run python test_mongodb_connection.py
```

## Alternative: Use Local MongoDB (For Development)

If MongoDB Atlas continues to have issues, use local MongoDB:

### Install MongoDB Locally

**Windows:**
```bash
choco install mongodb
mongod
```

**Mac:**
```bash
brew install mongodb-community
brew services start mongodb-community
```

### Update .env.dev for Local MongoDB

```env
# MongoDB Configuration (Local)
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=avpe_dev
```

### Test Local Connection

```bash
poetry run python test_mongodb_connection.py
```

## Quick Test Commands

### Test with your current credentials:
```bash
poetry run python test_mongodb_connection.py
```

### Test with custom URI:
```bash
poetry run python -c "from pymongo import MongoClient; client = MongoClient('YOUR_URI_HERE'); client.admin.command('ping'); print('Success!')"
```

## Common Issues

### Issue 1: "bad auth"
- **Cause**: Wrong username/password
- **Fix**: Verify credentials in MongoDB Atlas

### Issue 2: "connection timeout"
- **Cause**: IP not whitelisted
- **Fix**: Add IP to Network Access in Atlas

### Issue 3: "SSL/TLS error"
- **Cause**: Network/firewall blocking
- **Fix**: Check firewall settings, try different network

## Next Steps

1. ✅ Fix MongoDB Atlas credentials
2. ✅ Test connection with `test_mongodb_connection.py`
3. ✅ Once successful, start your FastAPI app
4. ✅ Test character CRUD endpoints

## Need Help?

If you continue to have issues:

1. **Check MongoDB Atlas Status**: https://status.mongodb.com/
2. **Review MongoDB Atlas Docs**: https://docs.atlas.mongodb.com/
3. **Try Local MongoDB** as alternative for development

---

**Once you fix the credentials, run:**
```bash
poetry run python test_mongodb_connection.py
```

**Expected output:**
```
✅ ALL TESTS PASSED! MongoDB is ready to use.
```
