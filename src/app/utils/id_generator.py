"""
ID Generator Utility

This module provides functions for generating unique identifiers across the application.
Uses UUID4 for guaranteed uniqueness with customizable prefixes for different entity types.

Functions:
- generate_character_id(): Generate unique ID for characters
- generate_user_id(): Generate unique ID for users (future use)
- generate_custom_id(): Generate ID with custom prefix
"""

import uuid
from typing import Optional


def generate_custom_id(prefix: str, length: int = 12) -> str:
    """
    Generate a unique ID with a custom prefix.
    
    Args:
        prefix: Prefix for the ID (e.g., 'char', 'user', 'story')
        length: Length of the UUID hex portion (default: 12)
    
    Returns:
        str: Unique ID in format '{prefix}_{uuid_hex}'
    
    Examples:
        >>> generate_custom_id('char', 12)
        'char_a1b2c3d4e5f6'
        >>> generate_custom_id('user', 16)
        'user_a1b2c3d4e5f6g7h8'
    """
    uuid_hex = uuid.uuid4().hex[:length]
    return f"{prefix}_{uuid_hex}"


def generate_character_id() -> str:
    """
    Generate a unique ID for a character.
    
    Returns:
        str: Unique character ID in format 'char_{12_hex_chars}'
    
    Examples:
        >>> generate_character_id()
        'char_a1b2c3d4e5f6'
    """
    return generate_custom_id('char', 12)


def generate_user_id() -> str:
    """
    Generate a unique ID for a user.
    
    Returns:
        str: Unique user ID in format 'user_{16_hex_chars}'
    
    Examples:
        >>> generate_user_id()
        'user_a1b2c3d4e5f6g7h8'
    
    Note:
        Uses 16 characters for user IDs to provide extra uniqueness
        for potentially larger user base.
    """
    return generate_custom_id('user', 16)


def generate_story_id() -> str:
    """
    Generate a unique ID for a story.
    
    Returns:
        str: Unique story ID in format 'story_{12_hex_chars}'
    
    Examples:
        >>> generate_story_id()
        'story_a1b2c3d4e5f6'
    """
    return generate_custom_id('story', 12)


def generate_segment_id() -> str:
    """
    Generate a unique ID for a story segment.
    
    Returns:
        str: Unique segment ID in format 'seg_{10_hex_chars}'
    
    Examples:
        >>> generate_segment_id()
        'seg_a1b2c3d4e5'
    """
    return generate_custom_id('seg', 10)


def generate_session_id() -> str:
    """
    Generate a unique ID for a session.
    
    Returns:
        str: Unique session ID in format 'sess_{16_hex_chars}'
    
    Examples:
        >>> generate_session_id()
        'sess_a1b2c3d4e5f6g7h8'
    """
    return generate_custom_id('sess', 16)


# ID Format Documentation
"""
ID Format Standards:

1. Character IDs: char_{12_hex}
   - Used for: Character roster entries
   - Length: 17 chars total (5 prefix + 12 hex)
   - Uniqueness: 2^48 combinations (~281 trillion)
   - Example: char_a1b2c3d4e5f6

2. User IDs: user_{16_hex}
   - Used for: User accounts (future)
   - Length: 21 chars total (5 prefix + 16 hex)
   - Uniqueness: 2^64 combinations (~18 quintillion)
   - Example: user_a1b2c3d4e5f6g7h8

3. Story IDs: story_{12_hex}
   - Used for: Story/content entries
   - Length: 18 chars total (6 prefix + 12 hex)
   - Uniqueness: 2^48 combinations
   - Example: story_a1b2c3d4e5f6

4. Segment IDs: seg_{10_hex}
   - Used for: Story segments
   - Length: 14 chars total (4 prefix + 10 hex)
   - Uniqueness: 2^40 combinations (~1 trillion)
   - Example: seg_a1b2c3d4e5

5. Session IDs: sess_{16_hex}
   - Used for: User sessions (future)
   - Length: 21 chars total (5 prefix + 16 hex)
   - Uniqueness: 2^64 combinations
   - Example: sess_a1b2c3d4e5f6g7h8

Custom IDs:
- Use generate_custom_id(prefix, length) for new entity types
- Recommended lengths:
  - Short-lived entities (segments, temp data): 8-10 chars
  - Standard entities (characters, stories): 12 chars
  - Critical entities (users, sessions): 16 chars
"""
