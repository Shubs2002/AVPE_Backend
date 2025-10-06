# 🏗️ Connectors Architecture

## Overview

The connectors module provides a centralized, singleton-based approach to managing external API clients for OpenAI/OpenRouter and Google GenAI services.

## Directory Structure

```
src/app/connectors/
├── __init__.py              # Module exports
├── openai_connector.py      # OpenAI/OpenRouter client
└── genai_connector.py       # Google GenAI client
```

## Design Pattern: Singleton

### Why Singleton?

1. **Resource Efficiency**: API clients maintain connection pools and state
2. **Performance**: Avoid repeated initialization overhead
3. **Consistency**: Same configuration across all uses
4. **Memory**: Single instance reduces memory footprint

### Implementation

```python
# Global variable to store the singleton instance
_client = None

def get_client():
    global _client
    if _client is None:
        _client = initialize_client()
    return _client
```

## OpenAI Connector

### File: `openai_connector.py`

```python
from openai import OpenAI
from app.config.settings import settings

_openai_client = None

def get_openai_client() -> OpenAI:
    """Get or create the OpenAI client instance"""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=settings.OPENAI_API_KEY
        )
    return _openai_client
```

### Configuration

- **Base URL**: `settings.OPENROUTER_BASE_URL`
- **API Key**: `settings.OPENAI_API_KEY`
- **Purpose**: LLM operations (story generation, character analysis)

### Used By

- `openai_service.py` - All content generation functions
- Story generation
- Meme generation
- Free content generation
- Character analysis
- Trending ideas generation

## GenAI Connector

### File: `genai_connector.py`

```python
from google import genai
from app.config.settings import settings

_genai_client = None

def get_genai_client() -> genai.Client:
    """Get or create the Google GenAI client instance"""
    global _genai_client
    if _genai_client is None:
        _genai_client = genai.Client(
            api_key=settings.GOOGLE_STUDIO_API_KEY
        )
    return _genai_client
```

### Configuration

- **API Key**: `settings.GOOGLE_STUDIO_API_KEY`
- **Purpose**: Video generation using Vertex AI Veo-3

### Used By

- `genai_service.py` - Video and thumbnail generation
- Video generation from prompts
- Thumbnail image generation

## Usage Flow

### Story Generation Flow

```
User Request
    ↓
screenwriter_controller.build_story()
    ↓
openai_service.generate_story_segments()
    ↓
get_openai_client()  ← Connector
    ↓
OpenAI API (via OpenRouter)
    ↓
Response
```

### Video Generation Flow

```
User Request
    ↓
cinematographer_controller.handle_generate_full_content_videos()
    ↓
genai_service.generate_video_from_payload()
    ↓
get_genai_client()  ← Connector
    ↓
Google GenAI API (Vertex AI Veo-3)
    ↓
Response
```

## API Comparison

### OpenAI/OpenRouter API

**Purpose**: Text generation (LLM)

**Models Used**:
- `grok-2-1212` (default for story/meme/content generation)
- Vision models for character analysis

**Operations**:
- Story segment generation
- Character analysis from images
- Meme content generation
- Free content generation
- Trending ideas generation

**Request Format**:
```python
response = client.chat.completions.create(
    model="grok-2-1212",
    messages=[{"role": "user", "content": "..."}]
)
```

### Google GenAI API

**Purpose**: Video and image generation

**Models Used**:
- `veo-3` (video generation)
- `gemini-2.5-flash-image-preview` (thumbnail generation)

**Operations**:
- Video generation from text prompts
- Thumbnail image generation

**Request Format**:
```python
response = client.models.generate_content(
    model="veo-3",
    contents=["..."]
)
```

## Error Handling

### Connection Errors

```python
def get_openai_client():
    try:
        if _openai_client is None:
            _openai_client = OpenAI(...)
        return _openai_client
    except Exception as e:
        print(f"❌ Failed to initialize OpenAI client: {e}")
        raise
```

### Retry Logic

Currently handled at the service layer. Future enhancement: move to connector layer.

## Configuration Management

### Environment Variables

```env
# OpenAI/OpenRouter
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENAI_API_KEY=sk-...

# Google GenAI
GOOGLE_STUDIO_API_KEY=...
```

### Settings File

```python
# src/app/config/settings.py
class Settings:
    OPENROUTER_BASE_URL: str
    OPENAI_API_KEY: str
    GOOGLE_STUDIO_API_KEY: str
    SCRIPT_MODEL: str = "grok-2-1212"
```

## Testing

### Unit Testing

```python
from app.connectors.openai_connector import get_openai_client, reset_openai_client

def test_openai_connector():
    # Reset before test
    reset_openai_client()
    
    # Get client
    client1 = get_openai_client()
    client2 = get_openai_client()
    
    # Should be the same instance (singleton)
    assert client1 is client2
```

### Integration Testing

```python
def test_story_generation_with_connector():
    from app.services.openai_service import generate_story_segments
    
    result = generate_story_segments("A hero saves the day", 5)
    assert result is not None
    assert 'segments' in result
```

## Performance Considerations

### Initialization Time

- **First Call**: ~100-200ms (client initialization)
- **Subsequent Calls**: ~0.1ms (returns cached instance)

### Memory Usage

- **Without Singleton**: N instances × ~10MB = N × 10MB
- **With Singleton**: 1 instance × ~10MB = 10MB

### Connection Pooling

Both OpenAI and Google GenAI clients maintain internal connection pools:
- Reuses HTTP connections
- Reduces latency
- Improves throughput

## Security Considerations

### API Key Management

✅ **Good Practices**:
- API keys stored in environment variables
- Never hardcoded in source code
- Loaded via settings module
- Not logged or exposed in responses

❌ **Avoid**:
- Committing API keys to version control
- Logging API keys
- Exposing keys in error messages

### Client Isolation

Each connector manages its own client instance:
- No cross-contamination between services
- Independent error handling
- Separate rate limiting

## Monitoring & Logging

### Current Logging

```python
def get_openai_client():
    if _openai_client is None:
        _openai_client = OpenAI(...)
        print("✅ OpenAI/OpenRouter client initialized")
    return _openai_client
```

### Future Enhancements

```python
import logging

logger = logging.getLogger(__name__)

def get_openai_client():
    if _openai_client is None:
        logger.info("Initializing OpenAI client")
        _openai_client = OpenAI(...)
        logger.info("OpenAI client initialized successfully")
    return _openai_client
```

## Extending the Architecture

### Adding a New Connector

1. **Create connector file**: `src/app/connectors/new_api_connector.py`

```python
from some_api import Client
from app.config.settings import settings

_new_api_client = None

def get_new_api_client() -> Client:
    global _new_api_client
    if _new_api_client is None:
        _new_api_client = Client(
            api_key=settings.NEW_API_KEY
        )
        print("✅ New API client initialized")
    return _new_api_client

def reset_new_api_client():
    global _new_api_client
    _new_api_client = None
```

2. **Update `__init__.py`**:

```python
from app.connectors.new_api_connector import get_new_api_client

__all__ = ['get_openai_client', 'get_genai_client', 'get_new_api_client']
```

3. **Use in services**:

```python
from app.connectors.new_api_connector import get_new_api_client

def my_service_function():
    client = get_new_api_client()
    # Use client...
```

## Best Practices

### ✅ Do

1. Always use `get_*_client()` functions
2. Never create client instances directly in services
3. Use reset functions for testing
4. Handle errors at service layer
5. Log client initialization

### ❌ Don't

1. Don't create multiple client instances
2. Don't hardcode API keys
3. Don't bypass connectors
4. Don't modify global client state
5. Don't expose clients in public APIs

## Comparison: Before vs After

### Before (Direct Instantiation)

```python
# In openai_service.py
from openai import OpenAI
from app.config.settings import settings

client = OpenAI(
    base_url=settings.OPENROUTER_BASE_URL,
    api_key=settings.OPENAI_API_KEY
)

def generate_story():
    response = client.chat.completions.create(...)
```

**Issues**:
- ❌ Client created at module import time
- ❌ No control over initialization
- ❌ Hard to test
- ❌ Tight coupling

### After (Connector Pattern)

```python
# In openai_service.py
from app.connectors.openai_connector import get_openai_client

def generate_story():
    client = get_openai_client()
    response = client.chat.completions.create(...)
```

**Benefits**:
- ✅ Lazy initialization
- ✅ Singleton pattern
- ✅ Easy to test
- ✅ Loose coupling
- ✅ Centralized management

## Conclusion

The connectors architecture provides a clean, maintainable, and efficient way to manage external API clients. The singleton pattern ensures resource efficiency while maintaining flexibility for testing and future enhancements.

---

**Architecture Version**: 1.0
**Last Updated**: 2025-10-05
**Status**: ✅ Production Ready
