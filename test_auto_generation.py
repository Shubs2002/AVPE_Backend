#!/usr/bin/env python3
"""
Test script for the new AUTO generation routes.
Each route handles the complete 2-step process internally and returns all segments.
"""

import requests
import json
import time

# API base URL (adjust as needed)
BASE_URL = "http://localhost:8000"

def test_movie_auto():
    """Test the auto movie generation route."""
    print("🎬 Testing Auto Movie Generation")
    print("=" * 50)
    
    payload = {
        "idea": "A thrilling sci-fi adventure about time travelers trying to prevent an apocalypse",
        "total_segments": 20,
        "custom_character_roster": None,
        "no_narration": False,
        "narration_only_first": False,
        "adult_story": False
    }
    
    try:
        print("🚀 Generating complete movie (auto 2-step process)...")
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/generate-movie-auto", json=payload)
        response.raise_for_status()
        
        end_time = time.time()
        result = response.json()
        movie = result["movie"]
        
        print(f"✅ Movie generated successfully in {end_time - start_time:.2f} seconds!")
        print(f"📖 Title: {movie['title']}")
        print(f"👥 Characters: {len(movie.get('characters_roster', []))}")
        print(f"📊 Segments: {movie['generation_info']['total_segments_generated']}/{movie['generation_info']['total_segments_planned']}")
        print(f"🎯 Success rate: {movie['generation_info']['successful_sets']}/{movie['generation_info']['total_sets']} sets")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed: {e}")
        return False

def test_story_auto():
    """Test the auto story generation route."""
    print("\n📖 Testing Auto Story Generation")
    print("=" * 50)
    
    payload = {
        "idea": "A magical adventure in a fantasy world with dragons and wizards",
        "segments": 15,
        "custom_character_roster": None
    }
    
    try:
        print("🚀 Generating complete story (auto 2-step process)...")
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/generate-story-auto", json=payload)
        response.raise_for_status()
        
        end_time = time.time()
        result = response.json()
        story = result["story"]
        
        print(f"✅ Story generated successfully in {end_time - start_time:.2f} seconds!")
        print(f"📖 Title: {story['title']}")
        print(f"👥 Characters: {len(story.get('characters_roster', []))}")
        print(f"📊 Segments: {story['generation_info']['total_segments_generated']}/{story['generation_info']['total_segments_planned']}")
        print(f"🎯 Success rate: {story['generation_info']['successful_batches']}/{story['generation_info']['total_batches']} batches")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed: {e}")
        return False

def test_meme_auto():
    """Test the auto meme generation route."""
    print("\n😂 Testing Auto Meme Generation")
    print("=" * 50)
    
    payload = {
        "idea": "When you're trying to look busy at work but your boss walks by",
        "segments": 7,
        "custom_character_roster": None,
        "no_narration": False,
        "narration_only_first": False
    }
    
    try:
        print("🚀 Generating complete meme (auto 2-step process)...")
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/generate-meme-auto", json=payload)
        response.raise_for_status()
        
        end_time = time.time()
        result = response.json()
        meme = result["meme"]
        
        print(f"✅ Meme generated successfully in {end_time - start_time:.2f} seconds!")
        print(f"📖 Title: {meme['title']}")
        print(f"👥 Characters: {len(meme.get('characters_roster', []))}")
        print(f"📊 Segments: {meme['generation_info']['total_segments_generated']}/{meme['generation_info']['total_segments_planned']}")
        print(f"🎯 Success: {meme['generation_info']['success']}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed: {e}")
        return False

def test_free_content_auto():
    """Test the auto free content generation route."""
    print("\n🎯 Testing Auto Free Content Generation")
    print("=" * 50)
    
    payload = {
        "idea": "5 morning habits that will change your life",
        "segments": 10,
        "custom_character_roster": None,
        "no_narration": False,
        "narration_only_first": False
    }
    
    try:
        print("🚀 Generating complete free content (auto 2-step process)...")
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/generate-free-content-auto", json=payload)
        response.raise_for_status()
        
        end_time = time.time()
        result = response.json()
        content = result["content"]
        
        print(f"✅ Free content generated successfully in {end_time - start_time:.2f} seconds!")
        print(f"📖 Title: {content['title']}")
        print(f"👥 Characters: {len(content.get('characters_roster', []))}")
        print(f"📊 Segments: {content['generation_info']['total_segments_generated']}/{content['generation_info']['total_segments_planned']}")
        print(f"🎯 Success rate: {content['generation_info']['successful_batches']}/{content['generation_info']['total_batches']} batches")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed: {e}")
        return False

def test_random_content():
    """Test auto generation with random ideas (no idea provided)."""
    print("\n🎲 Testing Auto Generation with Random Ideas")
    print("=" * 50)
    
    # Test random meme
    try:
        print("🎲 Generating random meme...")
        response = requests.post(f"{BASE_URL}/generate-meme-auto", json={
            "idea": None,  # Will generate random idea
            "segments": 5
        })
        response.raise_for_status()
        
        result = response.json()
        meme = result["meme"]
        print(f"✅ Random meme: {meme['title']}")
        
    except Exception as e:
        print(f"❌ Random meme failed: {e}")
    
    # Test random free content
    try:
        print("🎲 Generating random free content...")
        response = requests.post(f"{BASE_URL}/generate-free-content-auto", json={
            "idea": None,  # Will generate random idea
            "segments": 5
        })
        response.raise_for_status()
        
        result = response.json()
        content = result["content"]
        print(f"✅ Random content: {content['title']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Random content failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Auto Generation Routes")
    print("Each route handles the complete 2-step process internally")
    print("=" * 70)
    
    # Test all auto routes
    movie_success = test_movie_auto()
    story_success = test_story_auto()
    meme_success = test_meme_auto()
    content_success = test_free_content_auto()
    random_success = test_random_content()
    
    print("\n" + "=" * 70)
    print("📊 Test Results:")
    print(f"🎬 Movie auto: {'✅ Success' if movie_success else '❌ Failed'}")
    print(f"📖 Story auto: {'✅ Success' if story_success else '❌ Failed'}")
    print(f"😂 Meme auto: {'✅ Success' if meme_success else '❌ Failed'}")
    print(f"🎯 Content auto: {'✅ Success' if content_success else '❌ Failed'}")
    print(f"🎲 Random content: {'✅ Success' if random_success else '❌ Failed'}")
    
    total_success = sum([movie_success, story_success, meme_success, content_success, random_success])
    
    if total_success == 5:
        print("\n🎉 All auto routes working perfectly!")
        print("\n💡 Usage:")
        print("- Use /generate-movie-auto for complete movies")
        print("- Use /generate-story-auto for complete stories")
        print("- Use /generate-meme-auto for complete memes")
        print("- Use /generate-free-content-auto for complete content")
        print("- Each route handles the 2-step process internally")
        print("- No more truncation issues!")
        print("- Single API call returns complete results")
    else:
        print(f"\n⚠️ {5 - total_success} routes failed. Check the server logs for details.")
        
    print("\n🔧 Manual 2-step routes are also available for advanced control:")
    print("- /generate-*-metadata + /generate-*-segments-from-metadata")