# Installation Guide - Character Creation from Image

## 📦 Step-by-Step Installation

### Step 1: Install Python Dependencies

```bash
pip install cloudinary rembg
```

**What gets installed:**
- `cloudinary` - For cloud image hosting and management
- `rembg` - For automatic background removal from images

### Step 2: Configure Cloudinary

1. **Sign up for Cloudinary** (if you don't have an account)
   - Go to: https://cloudinary.com
   - Click "Sign Up" (free tier available)
   - Complete registration

2. **Get your credentials**
   - Log in to Cloudinary Dashboard
   - You'll see your credentials on the main page:
     - Cloud Name
     - API Key
     - API Secret

3. **Add credentials to `.env.dev`**

Open `.env.dev` and add these lines at the end:

```env
# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your_cloud_name_here
CLOUDINARY_API_KEY=your_api_key_here
CLOUDINARY_API_SECRET=your_api_secret_here
```

**Example:**
```env
# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=dxyz123abc
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=abcdefghijklmnopqrstuvwxyz123456
```

### Step 3: Verify MongoDB Connection

Make sure MongoDB is configured in `.env.dev`:

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=avpe_dev
```

### Step 4: Start the Server

```bash
python -m uvicorn src.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Step 5: Test the Installation

#### Option A: Using cURL

```bash
curl -X POST "http://localhost:8000/api/create-character-from-image" \
  -F "image=@path/to/your/character.png" \
  -F "character_name=Test Character"
```

#### Option B: Using Python Test Script

1. Update `test_create_character_from_image.py`:

```python
# Update these lines
image_path = "path/to/your/character.png"  # Your image path
character_name = "Test Character"           # Your character name

# Uncomment this line
test_create_character_from_image(image_path, character_name)
```

2. Run the test:

```bash
python test_create_character_from_image.py
```

#### Option C: Using Postman/Thunder Client

1. Create new POST request
2. URL: `http://localhost:8000/api/create-character-from-image`
3. Body type: `form-data`
4. Add fields:
   - `image` (File) - Select your image
   - `character_name` (Text) - Enter name
5. Send request

### Step 6: Verify Success

If everything works, you should see:

```
✅ Character created successfully!
🆔 Character ID: 507f1f77bcf86cd799439011
📝 Character Name: Test Character
🖼️ Image URL: https://res.cloudinary.com/.../test_character.png
```

## 🔧 Troubleshooting

### Issue: "Module 'cloudinary' not found"

**Solution:**
```bash
pip install cloudinary
```

### Issue: "Module 'rembg' not found"

**Solution:**
```bash
pip install rembg
```

### Issue: "Cloudinary credentials not configured"

**Solution:**
1. Check `.env.dev` has Cloudinary credentials
2. Restart the server after adding credentials
3. Verify credentials are correct (no extra spaces)

### Issue: "Background removal failed"

**Solution:**
- This is normal! The system will continue with the original image
- Background removal requires additional models to download on first use
- Wait for the download to complete (happens automatically)

### Issue: "MongoDB connection failed"

**Solution:**
1. Check `MONGODB_URI` in `.env.dev`
2. Verify MongoDB Atlas is accessible
3. Check network connection
4. Run: `python diagnose_mongodb.py`

### Issue: "Image file too large"

**Solution:**
- Maximum file size is 10MB
- Resize your image before uploading
- Use PNG or JPG format

## 📋 Verification Checklist

- [ ] Dependencies installed (`cloudinary`, `rembg`)
- [ ] Cloudinary credentials in `.env.dev`
- [ ] MongoDB connection working
- [ ] Server starts without errors
- [ ] Test request succeeds
- [ ] Character appears in MongoDB
- [ ] Image URL is accessible

## 🎯 Quick Test Commands

### Test 1: Check Server Health
```bash
curl http://localhost:8000/api/characters/health/check
```

Expected: `{"success": true, ...}`

### Test 2: List Characters
```bash
curl http://localhost:8000/api/characters
```

Expected: List of characters (may be empty initially)

### Test 3: Create Character
```bash
curl -X POST "http://localhost:8000/api/create-character-from-image" \
  -F "image=@character.png" \
  -F "character_name=Test"
```

Expected: Character creation success response

## 📚 Next Steps

After successful installation:

1. **Read the guides:**
   - `CHARACTER_IMAGE_QUICK_START.md` - Quick reference
   - `CHARACTER_IMAGE_CREATION_GUIDE.md` - Complete guide
   - `CHARACTER_IMAGE_VISUAL_FLOW.md` - Visual diagrams

2. **Try the features:**
   - Create characters from images
   - Use characters in story generation
   - Use character images as keyframes

3. **Explore the API:**
   - Visit: http://localhost:8000/docs
   - Try the interactive API documentation

## 🎉 Installation Complete!

You're now ready to create characters from images! 🎭

**What you can do now:**
- ✅ Upload character images
- ✅ Get AI-powered analysis
- ✅ Remove backgrounds automatically
- ✅ Store images in the cloud
- ✅ Save to MongoDB
- ✅ Use in video generation

Happy character creating! 🚀
