# Utils Package

This package contains reusable utility functions and helpers for the application.

## Modules

### id_generator.py

Centralized ID generation utility using UUID4 for guaranteed uniqueness.

#### Functions

##### `generate_character_id()`
Generate a unique ID for a character.

**Returns:** `str` - Format: `char_{12_hex_chars}`

**Example:**
```python
from app.utils.id_generator import generate_character_id

char_id = generate_character_id()
# Output: 'char_a1b2c3d4e5f6'
```

---

##### `generate_user_id()`
Generate a unique ID for a user (future use).

**Returns:** `str` - Format: `user_{16_hex_chars}`

**Example:**
```python
from app.utils.id_generator import generate_user_id

user_id = generate_user_id()
# Output: 'user_a1b2c3d4e5f6g7h8'
```

**Note:** Uses 16 characters for extra uniqueness for potentially larger user base.

---

##### `generate_custom_id(prefix, length=12)`
Generate a unique ID with a custom prefix.

**Parameters:**
- `prefix` (str): Prefix for the ID (e.g., 'char', 'user', 'story')
- `length` (int): Length of the UUID hex portion (default: 12)

**Returns:** `str` - Format: `{prefix}_{uuid_hex}`

**Example:**
```python
from app.utils.id_generator import generate_custom_id

# Custom entity ID
entity_id = generate_custom_id('entity', 10)
# Output: 'entity_a1b2c3d4e5'

# Project ID
project_id = generate_custom_id('proj', 8)
# Output: 'proj_a1b2c3d4'
```

---

##### Additional Helper Functions

- `generate_story_id()` - Format: `story_{12_hex}`
- `generate_segment_id()` - Format: `seg_{10_hex}`
- `generate_session_id()` - Format: `sess_{16_hex}`

---

## ID Format Standards

### Character IDs
- **Format:** `char_{12_hex}`
- **Length:** 17 chars total (5 prefix + 12 hex)
- **Uniqueness:** 2^48 combinations (~281 trillion)
- **Example:** `char_a1b2c3d4e5f6`
- **Used for:** Character roster entries

### User IDs
- **Format:** `user_{16_hex}`
- **Length:** 21 chars total (5 prefix + 16 hex)
- **Uniqueness:** 2^64 combinations (~18 quintillion)
- **Example:** `user_a1b2c3d4e5f6g7h8`
- **Used for:** User accounts (future)

### Story IDs
- **Format:** `story_{12_hex}`
- **Length:** 18 chars total (6 prefix + 12 hex)
- **Uniqueness:** 2^48 combinations
- **Example:** `story_a1b2c3d4e5f6`
- **Used for:** Story/content entries

### Segment IDs
- **Format:** `seg_{10_hex}`
- **Length:** 14 chars total (4 prefix + 10 hex)
- **Uniqueness:** 2^40 combinations (~1 trillion)
- **Example:** `seg_a1b2c3d4e5`
- **Used for:** Story segments

### Session IDs
- **Format:** `sess_{16_hex}`
- **Length:** 21 chars total (5 prefix + 16 hex)
- **Uniqueness:** 2^64 combinations
- **Example:** `sess_a1b2c3d4e5f6g7h8`
- **Used for:** User sessions (future)

---

## Usage Examples

### In Character Analysis

```python
from app.utils.id_generator import generate_character_id

# After AI returns character data
character_data = json.loads(ai_response)

for character in character_data['characters_roster']:
    character['id'] = generate_character_id()
    print(f"Generated ID: {character['id']}")
```

### In Story Generation

```python
from app.utils.id_generator import generate_character_id

def ensure_character_ids(roster):
    """Ensure all characters have IDs"""
    for character in roster:
        if not character.get('id') or character.get('id') == 'unknown':
            character['id'] = generate_character_id()
    return roster

# Use in story generation
custom_roster = ensure_character_ids(custom_character_roster)
```

### Future: User Management

```python
from app.utils.id_generator import generate_user_id

def create_user(username, email):
    user_id = generate_user_id()
    user = {
        'id': user_id,
        'username': username,
        'email': email,
        'created_at': datetime.utcnow()
    }
    # Save to database
    return user
```

---

## Extending the Utility

### Adding New ID Types

To add a new ID type, create a new function in `id_generator.py`:

```python
def generate_project_id() -> str:
    """
    Generate a unique ID for a project.
    
    Returns:
        str: Unique project ID in format 'proj_{12_hex_chars}'
    """
    return generate_custom_id('proj', 12)
```

Then export it in `__init__.py`:

```python
from .id_generator import (
    generate_character_id,
    generate_user_id,
    generate_project_id,  # Add new function
    generate_custom_id
)

__all__ = [
    'generate_character_id',
    'generate_user_id',
    'generate_project_id',  # Add to exports
    'generate_custom_id'
]
```

### Recommended Lengths

- **Short-lived entities** (segments, temp data): 8-10 chars
- **Standard entities** (characters, stories): 12 chars
- **Critical entities** (users, sessions): 16 chars

---

## Benefits

1. **Centralized** - Single source of truth for ID generation
2. **Consistent** - Same format across the application
3. **Unique** - UUID4 guarantees uniqueness
4. **Expandable** - Easy to add new ID types
5. **Testable** - Simple functions, easy to test
6. **Type-Safe** - Clear prefixes identify entity types

---

## Testing

```python
# Test character ID generation
from app.utils.id_generator import generate_character_id

char_id = generate_character_id()
assert char_id.startswith('char_')
assert len(char_id) == 17
print(f"✅ Character ID: {char_id}")

# Test user ID generation
from app.utils.id_generator import generate_user_id

user_id = generate_user_id()
assert user_id.startswith('user_')
assert len(user_id) == 21
print(f"✅ User ID: {user_id}")

# Test custom ID generation
from app.utils.id_generator import generate_custom_id

custom_id = generate_custom_id('test', 8)
assert custom_id.startswith('test_')
assert len(custom_id) == 13  # 5 (prefix) + 8 (hex)
print(f"✅ Custom ID: {custom_id}")
```

---

## Migration from Old Code

### Before (inline UUID generation)
```python
import uuid

# Scattered throughout codebase
character['id'] = f"char_{uuid.uuid4().hex[:12]}"
user['id'] = f"user_{uuid.uuid4().hex[:16]}"
```

### After (centralized utility)
```python
from app.utils.id_generator import generate_character_id, generate_user_id

# Consistent and maintainable
character['id'] = generate_character_id()
user['id'] = generate_user_id()
```

---

## Future Enhancements

Potential additions to the utils package:

1. **Validation utilities** - Validate ID formats
2. **Date/time helpers** - Consistent datetime handling
3. **String utilities** - Common string operations
4. **File utilities** - File handling helpers
5. **Encryption utilities** - Password hashing, token generation

---

**Created:** 2025-10-05  
**Status:** ✅ Production Ready
