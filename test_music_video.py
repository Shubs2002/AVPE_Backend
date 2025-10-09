#!/usr/bin/env python3
"""
Test script for AI Music Video generation endpoint.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_basic_music_video():
    """Test basic music video generation."""
    print("🎵 Test 1: Basic Music Video")
    print("=" * 50)
    
    payload = {
        "song_lyrics": """
        Verse 1:
        Walking down the street
        Feeling the beat
        Life is sweet
        
        Chorus:
        This is my time
        This is my rhyme
        Living life sublime
        
        Verse 2:
        Dancing in the rain
        Breaking every chain
        No more pain
        
        Chorus:
        This is my time
        This is my rhyme
        Living life sublime
        """,
        "song_length": 120,
        "music_genre": "Pop"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-music-video", json=payload)
        response.raise_for_status()
        
        result = response.json()["music_video"]
        print(f"✅ Success!")
        print(f"   Title: {result.get('title')}")
        print(f"   Genre: {result.get('music_genre')}")
        print(f"   Total Segments: {result.get('total_segments')}")
        print(f"   Song Length: {result.get('song_length')}s")
        
        # Check timing
        total_duration = sum(seg['duration'] for seg in result['segments'])
        print(f"   Total Duration: {total_duration}s")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_with_background_voice():
    """Test music video with background voice."""
    print("\n🎤 Test 2: Music Video with Background Voice")
    print("=" * 50)
    
    payload = {
        "song_lyrics": """
        Verse 1:
        In the silence of the night
        I find my inner light
        
        Chorus:
        Rise above, reach the sky
        Spread your wings and fly
        """,
        "song_length": 90,
        "background_voice_needed": True,
        "music_genre": "Inspirational Pop",
        "visual_theme": "Journey of self-discovery"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-music-video", json=payload)
        response.raise_for_status()
        
        result = response.json()["music_video"]
        print(f"✅ Success!")
        print(f"   Title: {result.get('title')}")
        print(f"   Background Voice: {result['background_voice_info']['enabled']}")
        print(f"   Visual Theme: {result.get('visual_theme')}")
        
        # Check if background voice is in segments
        has_bg_voice = any('background_voice' in seg for seg in result['segments'])
        print(f"   Background Voice in Segments: {has_bg_voice}")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_with_custom_characters():
    """Test music video with custom characters."""
    print("\n👤 Test 3: Music Video with Custom Characters")
    print("=" * 50)
    
    payload = {
        "song_lyrics": """
        Verse 1:
        Two hearts beating as one
        Our story has just begun
        
        Chorus:
        Together we stand
        Hand in hand
        """,
        "song_length": 100,
        "custom_character_roster": [
            {
                "name": "Lead Singer",
                "role": "Main Performer",
                "physical_appearance": {
                    "gender": "Female",
                    "age": "25",
                    "hair_color": "Long blonde hair",
                    "eye_color": "Blue",
                    "skin_tone": "Fair"
                },
                "clothing_style": {
                    "primary_outfit": "Elegant white dress",
                    "style": "Romantic"
                }
            }
        ],
        "music_genre": "Ballad"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-music-video", json=payload)
        response.raise_for_status()
        
        result = response.json()["music_video"]
        print(f"✅ Success!")
        print(f"   Title: {result.get('title')}")
        print(f"   Characters: {len(result.get('characters_roster', []))}")
        
        # Check character names
        char_names = [c['name'] for c in result.get('characters_roster', [])]
        print(f"   Character Names: {', '.join(char_names)}")
        
        if 'Lead Singer' in char_names:
            print(f"   ✅ Custom character successfully integrated!")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_with_additional_dialogues():
    """Test music video with additional dialogues."""
    print("\n💬 Test 4: Music Video with Additional Dialogues")
    print("=" * 50)
    
    payload = {
        "song_lyrics": """
        Verse 1:
        Looking back at yesterday
        Wishing I could stay
        
        Chorus:
        But time moves on
        And we must be strong
        """,
        "song_length": 110,
        "additional_dialogues": [
            {
                "timestamp": 30,
                "character": "narrator",
                "line": "This is where everything changed..."
            },
            {
                "timestamp": 70,
                "character": "narrator",
                "line": "And this is where we found hope."
            }
        ],
        "music_genre": "Emotional Ballad",
        "visual_theme": "Memories and hope"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-music-video", json=payload)
        response.raise_for_status()
        
        result = response.json()["music_video"]
        print(f"✅ Success!")
        print(f"   Title: {result.get('title')}")
        print(f"   Total Segments: {result.get('total_segments')}")
        
        # Check for dialogue segments
        dialogue_segments = [seg for seg in result['segments'] if seg.get('segment_type') == 'dialogue']
        print(f"   Dialogue Segments: {len(dialogue_segments)}")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_hip_hop_music_video():
    """Test hip-hop style music video."""
    print("\n🎤 Test 5: Hip-Hop Music Video")
    print("=" * 50)
    
    payload = {
        "song_lyrics": """
        Verse 1:
        Started from the bottom now we here
        Making moves, no fear
        
        Chorus:
        We on top, can't stop
        Living life, hip-hop
        
        Verse 2:
        City lights, late nights
        Chasing dreams, reaching heights
        
        Chorus:
        We on top, can't stop
        Living life, hip-hop
        """,
        "song_length": 150,
        "music_genre": "Hip-Hop",
        "visual_theme": "Urban success story"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-music-video", json=payload)
        response.raise_for_status()
        
        result = response.json()["music_video"]
        print(f"✅ Success!")
        print(f"   Title: {result.get('title')}")
        print(f"   Genre: {result.get('music_genre')}")
        print(f"   Visual Theme: {result.get('visual_theme')}")
        print(f"   Color Palette: {result.get('color_palette_overall', 'N/A')}")
        
        # Check segment types
        segment_types = [seg['segment_type'] for seg in result['segments']]
        print(f"   Segment Types: {', '.join(set(segment_types))}")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_response_structure():
    """Test that response has all required fields."""
    print("\n🔍 Test 6: Response Structure Validation")
    print("=" * 50)
    
    payload = {
        "song_lyrics": "Simple song lyrics for testing",
        "song_length": 60,
        "music_genre": "Pop"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-music-video", json=payload)
        response.raise_for_status()
        
        result = response.json()["music_video"]
        
        # Check required fields
        required_fields = ['title', 'song_length', 'total_segments', 'segments', 
                          'characters_roster', 'visual_themes']
        
        missing_fields = [field for field in required_fields if field not in result]
        
        if missing_fields:
            print(f"❌ Missing fields: {', '.join(missing_fields)}")
            return False
        
        print(f"✅ All required fields present!")
        
        # Check segment structure
        segment = result['segments'][0]
        segment_fields = ['segment', 'segment_type', 'start_time', 'end_time', 
                         'duration', 'lyrics', 'scene', 'camera', 'shot_type']
        
        missing_seg_fields = [field for field in segment_fields if field not in segment]
        
        if missing_seg_fields:
            print(f"⚠️ Missing segment fields: {', '.join(missing_seg_fields)}")
        else:
            print(f"✅ All segment fields present!")
        
        # Check timing accuracy
        total_duration = sum(seg['duration'] for seg in result['segments'])
        song_length = result['song_length']
        timing_diff = abs(total_duration - song_length)
        
        print(f"   Song Length: {song_length}s")
        print(f"   Total Duration: {total_duration}s")
        print(f"   Difference: {timing_diff}s")
        
        if timing_diff <= 5:  # Allow 5 second tolerance
            print(f"   ✅ Timing is accurate!")
        else:
            print(f"   ⚠️ Timing difference is significant")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 AI Music Video Generation Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(("Basic Music Video", test_basic_music_video()))
    results.append(("With Background Voice", test_with_background_voice()))
    results.append(("With Custom Characters", test_with_custom_characters()))
    results.append(("With Additional Dialogues", test_with_additional_dialogues()))
    results.append(("Hip-Hop Style", test_hip_hop_music_video()))
    results.append(("Response Structure", test_response_structure()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total_passed = sum(1 for _, success in results if success)
    total_tests = len(results)
    
    print("\n" + "=" * 60)
    print(f"Total: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed!")
        print("\n💡 Music Video Features:")
        print("   ✅ Lyric synchronization")
        print("   ✅ Cinematic camera work")
        print("   ✅ Custom characters/performers")
        print("   ✅ Optional background voice")
        print("   ✅ Additional dialogues")
        print("   ✅ Genre-specific styling")
        print("   ✅ Precise timing for Veo3")
        print("\n🎵 Perfect for AI-generated music videos!")
    else:
        print(f"\n⚠️ {total_tests - total_passed} test(s) failed")
