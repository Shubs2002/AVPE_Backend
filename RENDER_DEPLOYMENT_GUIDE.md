# Render Deployment Guide

## 🚀 **Deploying Your Video Generation Backend to Render**

### 📋 **Recommended Architecture for Cloud Deployment**

Instead of using FFmpeg on Render (which has limitations), we've implemented a **cloud-adaptive approach**:

#### 🏠 **Local Development**
- ✅ Uses FFmpeg for video merging
- ✅ Full server-side video processing
- ✅ Immediate results

#### ☁️ **Production (Render)**
- ✅ Client-side video merging using Web APIs
- ✅ No server-side video processing overhead
- ✅ Better scalability and performance
- ✅ Lower server costs

## 🛠️ **Render Setup Steps**

### 1. **Environment Configuration**

Create these environment variables in Render:

```bash
ENV=prod
GOOGLE_STUDIO_API_KEY=your_google_studio_api_key
OPENAI_API_KEY=your_openai_api_key
# ... other environment variables
```

### 2. **Build Configuration**

Create a `render.yaml` file in your project root:

```yaml
services:
  - type: web
    name: video-generation-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: ENV
        value: prod
      - key: GOOGLE_STUDIO_API_KEY
        fromSecret: google_studio_api_key
      - key: OPENAI_API_KEY
        fromSecret: openai_api_key
```

### 3. **Dependencies**

Update your `requirements.txt` (no FFmpeg needed):

```txt
fastapi
uvicorn
pydantic
python-dotenv
requests
pillow
google-genai
# ... other dependencies
```

### 4. **Dockerfile** (Alternative to requirements.txt)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🎯 **How Video Merging Works in Production**

### **Backend Response** (Render)
```json
{
  "success": true,
  "merge_method": "client_side",
  "video_urls": [
    "https://video1.url",
    "https://video2.url",
    "https://video3.url"
  ],
  "instructions": {
    "method": "Use Web APIs for client-side merging",
    "steps": [
      "Download video segments",
      "Use Canvas/WebCodecs to merge",
      "Generate final video blob"
    ]
  },
  "web_merge_config": {
    "format": "mp4",
    "codec": "h264",
    "quality": "high"
  }
}
```

### **Frontend Implementation** (Client-side merging)

```javascript
// Example client-side video merging
async function mergeVideos(videoUrls) {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  const mediaRecorder = new MediaRecorder(canvas.captureStream());
  
  // Download and merge video segments
  for (const url of videoUrls) {
    const video = document.createElement('video');
    video.src = url;
    await video.play();
    
    // Draw video frames to canvas
    ctx.drawImage(video, 0, 0);
  }
  
  // Generate final merged video
  const chunks = [];
  mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
  mediaRecorder.onstop = () => {
    const blob = new Blob(chunks, { type: 'video/mp4' });
    // Download or upload merged video
  };
  
  mediaRecorder.start();
  // ... merging logic
  mediaRecorder.stop();
}
```

## 🔄 **API Endpoints Behavior**

### **Development (Local)**
```bash
POST /merge-content-videos
# Returns: Actual merged video file path
{
  "success": true,
  "output_file": "downloads/merged_video.mp4",
  "thumbnail_result": {...}
}
```

### **Production (Render)**
```bash
POST /merge-content-videos  
# Returns: Instructions for client-side merging
{
  "success": true,
  "merge_method": "client_side",
  "video_urls": [...],
  "instructions": {...}
}
```

## 🎨 **Thumbnail Generation**

Thumbnails work the same in both environments:
- ✅ Generated using Google AI Studio API
- ✅ Saved to cloud storage or returned as base64
- ✅ No FFmpeg dependency

## 📊 **Performance Benefits**

### **Render Deployment Advantages:**
- 🚀 **Faster Response Times** - No server-side video processing
- 💰 **Lower Costs** - Reduced CPU/memory usage
- 📈 **Better Scalability** - Handles more concurrent users
- 🔄 **No Timeouts** - Video processing happens on client
- 💾 **Less Storage** - No temporary video files on server

### **Client-Side Merging Advantages:**
- 🎯 **User Control** - Users see progress and can cancel
- 📱 **Device Utilization** - Uses client's processing power
- 🔒 **Privacy** - Videos processed locally
- 🌐 **Offline Capable** - Can work without constant server connection

## 🚀 **Deployment Commands**

### **Option 1: Connect GitHub Repository**
1. Connect your GitHub repo to Render
2. Set environment variables
3. Deploy automatically on push

### **Option 2: Manual Deployment**
```bash
# Build and deploy
git add .
git commit -m "Deploy to Render"
git push origin main
```

## 🔧 **Environment Variables for Render**

```bash
ENV=prod
GOOGLE_STUDIO_API_KEY=AIzaSyC65HE20pJaKw4MDirCb5sOXE_Xx1JlStk
OPENAI_API_KEY=your_openai_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
GCP_PROJECT_ID=your_project_id
# ... other variables from your .env files
```

## 🎯 **Testing Your Deployment**

### **Health Check Endpoint**
```bash
GET https://your-app.onrender.com/api/check-ffmpeg
# Should return: {"ffmpeg_available": false, "merge_method": "client_side"}
```

### **Video Generation Test**
```bash
POST https://your-app.onrender.com/api/generate-full-content-videos
# Should work normally and return client-side merge instructions
```

## 📋 **Migration Checklist**

- [ ] Set ENV=prod in Render environment variables
- [ ] Add all required API keys to Render secrets
- [ ] Update frontend to handle client-side video merging
- [ ] Test thumbnail generation in production
- [ ] Verify all API endpoints work correctly
- [ ] Set up monitoring and logging

## 🎉 **Result**

Your backend will:
- ✅ Generate content (stories, memes, educational)
- ✅ Create individual video segments
- ✅ Generate thumbnails automatically
- ✅ Provide merge instructions for frontend
- ✅ Scale efficiently on Render
- ✅ Keep costs low

The frontend handles video merging using modern Web APIs, giving you the best of both worlds: powerful backend content generation and efficient client-side video processing!