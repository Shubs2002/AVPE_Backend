# AI Video Production Engine (AVPE)

A powerful AI-powered video generation system that creates professional character videos using Google's Gemini AI (Veo 3.1 for video, Imagen for frames, Gemini for scripts).

## 🎬 Features

### Core Capabilities
- **AI Script Generation** - Gemini creates engaging scripts with visual storytelling
- **Frame Generation** - Imagen (Nano Banana) generates first and last keyframes
- **Video Interpolation** - Veo 3.1 interpolates between keyframes for smooth motion
- **Character Consistency** - Dual reference system maintains character appearance
- **Automatic Thumbnails** - AI-generated thumbnails with first frame reference
- **Multi-Format Support** - Stories, daily character content, memes, music videos

### Advanced Features
- **Frame Chaining** - Last frame of segment N becomes first frame of segment N+1
- **Organized Storage** - File storage manager for clean directory structure
- **Auto-Retry Logic** - Handles API rate limits and transient errors
- **Cloudinary Integration** - Fast, reliable image hosting
- **MongoDB Storage** - Structured character and content data
- **Video Merging** - Automatic segment merging with cleanup

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Poetry (package manager)
- Google AI API key (Gemini, Veo, Imagen)
- OpenAI API key (optional, for scripts)
- Cloudinary account (for image hosting)
- MongoDB (for character storage)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd Backend

# Install dependencies with Poetry
poetry install

# Copy environment template
cp .env.dev .env

# Configure your API keys in .env
```

### Environment Variables

```bash
# Google AI
GOOGLE_API_KEY=your_google_api_key
GOOGLE_PROJECT_ID=your_project_id

# OpenAI (optional)
OPENAI_API_KEY=your_openai_key

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=avpe_db
```

### Run Server

```bash
# Development mode
poetry run dev

# Production mode
poetry run start
```

Server runs on: `http://127.0.0.1:8000`

## 📖 API Documentation

### Generate Daily Character Content

Create engaging character moments with AI-generated scripts.

```bash
POST /api/generate-daily-character
```

**Request:**
```json
{
  "idea": "Floof discovers a mysterious box",
  "character_name": "Floof",
  "creature_language": "Soft and High-Pitched",
  "num_segments": 7,
  "allow_dialogue": false
}
```

**Response:**
```json
{
  "content": {
    "title": "Floof's Mysterious Discovery",
    "segments": [
      {
        "segment": 1,
        "first_frame_description": "Floof standing in room, looking at box...",
        "last_frame_description": "Floof reaching toward box...",
        "scene": "Floof notices mysterious box",
        "action": "Steps closer cautiously",
        "creature_sounds": [...]
      }
    ]
  }
}
```

### Generate Videos from Content

Convert scripts into videos with AI-generated keyframes.

```bash
POST /api/generate-daily-character-videos
```

**Request:**
```json
{
  "content_data": { /* output from generate-daily-character */ },
  "character_keyframe_uri": "https://res.cloudinary.com/.../character.png",
  "resolution": "720p",
  "aspect_ratio": "16:9",
  "download": true,
  "auto_merge": true
}
```

**Response:**
```json
{
  "success_count": 7,
  "total_segments": 7,
  "video_urls": ["https://...", "https://..."],
  "merged_video": {
    "success": true,
    "output_filename": "floofs_mysterious_discovery_complete"
  }
}
```

### Add Character from Image

Upload character image and automatically extract details with AI.

```bash
POST /api/add-character-from-image
Content-Type: multipart/form-data
```

**Form Data:**
- `image`: Character image file
- `character_name`: Name of character

**Response:**
```json
{
  "success": true,
  "character_id": "67890abcdef",
  "cloudinary_url": "https://res.cloudinary.com/.../character.png",
  "character_details": {
    "physical_appearance": {...},
    "personality": "friendly, cute",
    "video_prompt_description": "..."
  }
}
```

## 🎨 How It Works

### 1. Script Generation
```
User Idea → Gemini AI → Structured Script
- Segments with scene descriptions
- First and last frame descriptions
- Creature sounds and timing
- Camera angles and movements
```

### 2. Frame Generation
```
Segment 1:
├── Generate first_frame (Imagen + character image)
├── Generate last_frame (Imagen + character + first frame)
└── Store for next segment

Segment 2:
├── Use last_frame from Segment 1 as first_frame
├── Generate last_frame (Imagen + character + first frame)
└── Store for next segment
```

### 3. Video Generation
```
For each segment:
├── IMAGE parameter: first_frame
├── CONFIG.last_frame: last_frame
└── Veo 3.1 interpolates between them
```

### 4. Post-Processing
```
├── Download all videos
├── Generate thumbnail (with first frame reference)
├── Merge segments (optional)
└── Cleanup temporary frames
```

## 📁 Project Structure

```
Backend/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py              # API endpoints
│   │   ├── controllers/
│   │   │   ├── screenwriter_controller.py
│   │   │   └── cinematographer_controller.py
│   │   ├── services/
│   │   │   ├── genai_service.py       # Veo 3.1 video generation
│   │   │   ├── imagen_service.py      # Imagen frame generation
│   │   │   ├── openai_service.py      # Script generation
│   │   │   ├── content_to_video_service.py
│   │   │   ├── video_merger_service.py
│   │   │   └── file_storage_manager.py
│   │   ├── data/
│   │   │   └── prompts/               # AI prompts
│   │   └── connectors/
│   │       └── genai_connector.py     # Google AI client
│   └── main.py                        # FastAPI app
├── generated_content/                 # Output directory
│   └── daily_character/
│       └── {Title}/
│           ├── videos/                # Generated videos
│           ├── frames/                # Temporary frames
│           └── {title}_thumbnail.png
├── pyproject.toml                     # Dependencies
└── README.md
```

## 🎯 Use Cases

### Daily Character Content
Create viral Instagram/TikTok character moments:
- Funny reactions
- Relatable struggles
- Character quirks
- Everyday adventures

### Story Videos
Generate narrative content:
- Short stories
- Adventures
- Educational content
- Character development

### Meme Videos
Create trending meme content:
- Reaction videos
- Comedy sketches
- Viral formats

## 🔧 Configuration

### Video Settings
```python
{
  "resolution": "720p",      # 720p, 1080p
  "aspect_ratio": "16:9",    # 16:9, 9:16, 1:1, 4:5
  "duration": 8,             # seconds per segment
  "download": true,          # download to local
  "auto_merge": true         # merge segments automatically
}
```

### Character Settings
```python
{
  "character_name": "Floof",
  "creature_language": "Soft and High-Pitched",
  "allow_dialogue": false    # creature sounds only
}
```

## 📊 Storage Structure

```
generated_content/
└── daily_character/
    └── Floofs_Adventure/
        ├── videos/
        │   ├── floof_segment_1.mp4
        │   ├── floof_segment_2.mp4
        │   └── floof_segment_3.mp4
        ├── frames/                    # Deleted after success
        │   ├── first_frame_*.png
        │   └── last_frame_*.png
        └── Floofs_Adventure_complete_thumbnail.png
```

## 🚨 Error Handling

### Automatic Retry
- **Rate Limits**: Exponential backoff (5s, 10s, 20s)
- **Overloaded**: Automatic retry up to 3 times
- **Transient Errors**: Smart detection and retry

### Fallback Mechanisms
- **Frame Generation Fails**: Use character image
- **Video Generation Fails**: Continue with other segments
- **Merge Fails**: Return individual video URLs

## 🎨 Advanced Features

### Dual Reference System
Imagen uses TWO references for last frame generation:
1. **Character Image** - Maintains character appearance
2. **First Frame** - Maintains environment/lighting

### Frame Chaining
Perfect continuity between segments:
```
Segment 1 last frame → Segment 2 first frame
Segment 2 last frame → Segment 3 first frame
```

### Organized Storage
File storage manager creates clean directory structure:
- Content type folders
- Title-based organization
- Automatic cleanup

## 📝 API Rate Limits

### Google AI (Free Tier)
- **Requests**: 15 per minute, 1,500 per day
- **Tokens**: Limited per minute

### Solutions
1. Wait for quota reset
2. Upgrade to paid tier
3. Use multiple API keys
4. Implement request throttling

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

## 📄 License

[Your License Here]

## 🆘 Support

For issues or questions:
- Check documentation
- Review error logs
- Contact support

## 🎉 Credits

Built with:
- **Google Gemini AI** - Veo 3.1, Imagen, Gemini
- **FastAPI** - Web framework
- **Poetry** - Dependency management
- **Cloudinary** - Image hosting
- **MongoDB** - Data storage

---

**Made with ❤️ for AI video creators**
