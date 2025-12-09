"""
Gemini 3 Service

This module provides content generation using Gemini 3 Pro with thinking mode.
Uses the v1alpha API for advanced features like extended thinking.
"""

import json
from typing import Optional
from google import genai
from google.genai import types

from app.config.settings import settings
from app.data.prompts.generate_daily_character_prompt import get_daily_character_prompt


def get_gemini_client_with_thinking() -> genai.Client:
    """
    Get Gemini client configured for v1alpha API with thinking mode support
    
    Returns:
        genai.Client: Configured client for advanced features
    """
    return genai.Client(
        api_key=settings.GOOGLE_STUDIO_API_KEY,
        http_options={'api_version': 'v1alpha'}
    )


def generate_daily_character_content_v2(
    idea: str,
    character_name: str,
    creature_language: str = "Soft and High-Pitched",
    num_segments: int = 7,
    allow_dialogue: bool = False,
    num_characters: int = 1
) -> dict:
    """
    Generate daily character content using Gemini 3 Pro with extended thinking.
    
    This is the v2 version that uses Gemini 3 Pro's thinking mode for better
    reasoning and more creative content generation.
    
    Args:
        idea: The daily life moment/situation
        character_name: Name of the character(s) - comma-separated for multiple
        creature_language: Voice type description(s) - comma-separated for multiple
        num_segments: Number of segments to generate
        allow_dialogue: Allow human dialogue/narration (default: False)
        num_characters: Number of characters (1-5, default: 1)
    
    Returns:
        dict: Generated content with segments
    """
    try:
        print(f"\n🧠 Generating daily character content with Gemini 3 Pro (Thinking Mode)...")
        print(f"💡 Idea: {idea}")
        print(f"🎭 Character(s): {character_name}")
        print(f"👥 Number of characters: {num_characters}")
        print(f"🔢 Segments: {num_segments}")
        
        # Get the prompt
        prompt = get_daily_character_prompt(
            idea=idea,
            character_name=character_name,
            creature_language=creature_language,
            num_segments=num_segments,
            allow_dialogue=allow_dialogue,
            num_characters=num_characters
        )
        
        # Get Gemini client with v1alpha API
        client = get_gemini_client_with_thinking()
        
        print(f"🤔 Gemini 3 Pro is thinking deeply about your content...")
        
        # Generate content with Gemini 3 Pro and thinking mode
        # thinking_budget is in tokens - higher values = more thinking
        # Recommended: 8192 for high thinking, 4096 for medium, 2048 for low
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_budget=8192  # High thinking budget (8K tokens)
                ),
                response_modalities=["TEXT"],
                temperature=0.9,  # Higher creativity for character content
            )
        )
        
        # Extract the response text
        if not response or not response.text:
            raise ValueError("Gemini returned empty response. This might be due to safety filters or API issues.")
        
        response_text = response.text.strip()
        
        print(f"✅ Gemini 3 Pro completed thinking")
        
        # Clean up response (remove markdown code blocks if present)
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse JSON
        content_data = json.loads(response_text)
        
        print(f"✅ Content generated successfully!")
        print(f"📊 Generated {len(content_data.get('segments', []))} segments")
        
        return content_data
    
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse Gemini response as JSON: {str(e)}"
        print(f"❌ {error_msg}")
        if 'response_text' in locals():
            print(f"Response preview: {response_text[:500]}")
        raise ValueError(error_msg)
    
    except Exception as e:
        error_msg = f"Failed to generate content with Gemini 3 Pro: {str(e)}"
        print(f"❌ {error_msg}")
        raise ValueError(error_msg)


def generate_daily_character_content_in_sets_v2(
    idea: str,
    character_name: str,
    creature_language: str,
    total_segments: int,
    allow_dialogue: bool,
    num_characters: int = 1
) -> dict:
    """
    Generate daily character content in sets using Gemini 3 Pro with thinking mode.
    
    For large segment counts, this splits generation into sets of 10 segments each.
    
    Args:
        idea: The daily life moment/situation
        character_name: Name of the character(s) - comma-separated for multiple
        creature_language: Voice type description(s) - comma-separated for multiple
        total_segments: Total number of segments needed
        allow_dialogue: Allow human dialogue/narration
        num_characters: Number of characters (1-5, default: 1)
    
    Returns:
        dict: Complete content with all segments
    """
    import time
    from datetime import datetime
    
    print(f"\n🧠 Generating {total_segments} segments with Gemini 3 Pro (Thinking Mode)...")
    
    segments_per_set = 10
    total_sets = (total_segments + segments_per_set - 1) // segments_per_set
    
    print(f"📦 Will generate {total_sets} sets of up to {segments_per_set} segments each")
    
    all_segments = []
    metadata = None
    
    for set_num in range(1, total_sets + 1):
        start_segment = (set_num - 1) * segments_per_set + 1
        end_segment = min(set_num * segments_per_set, total_segments)
        segments_in_set = end_segment - start_segment + 1
        
        print(f"\n🎬 Generating Set {set_num}/{total_sets} (segments {start_segment}-{end_segment})...")
        
        try:
            # Generate this set
            set_data = generate_daily_character_content_v2(
                idea=idea,
                character_name=character_name,
                creature_language=creature_language,
                num_segments=segments_in_set,
                allow_dialogue=allow_dialogue,
                num_characters=num_characters
            )
            
            # Store metadata from first set
            if set_num == 1:
                metadata = {
                    "title": set_data.get("title", ""),
                    "short_summary": set_data.get("short_summary", ""),
                    "description": set_data.get("description", ""),
                    "hashtags": set_data.get("hashtags", []),
                    "character_name": character_name,
                    "creature_language": creature_language,
                    "allow_dialogue": allow_dialogue,
                    "total_segments": total_segments,
                    "generated_at": datetime.now().isoformat(),
                    "generation_method": "gemini-3-pro-thinking-v2"
                }
            
            # Add segments with correct numbering
            segments = set_data.get("segments", [])
            for seg in segments:
                seg["segment"] = start_segment + segments.index(seg)
                all_segments.append(seg)
            
            print(f"✅ Set {set_num} complete: {len(segments)} segments generated")
            
            # Small delay between sets
            if set_num < total_sets:
                print("⏳ Waiting 2 seconds before next set...")
                time.sleep(2)
        
        except Exception as e:
            print(f"❌ Failed to generate set {set_num}: {str(e)}")
            raise
    
    # Combine everything
    result = metadata.copy() if metadata else {}
    result["segments"] = all_segments
    result["total_segments_generated"] = len(all_segments)
    
    print(f"\n✅ All sets complete! Generated {len(all_segments)}/{total_segments} segments")
    
    return result
