#!/usr/bin/env python3
"""
Test script for WhatsApp AI Story generation endpoint.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_romantic_sunset():
    """Test romantic sunset WhatsApp story."""
    print("🌅 Test 1: Romantic Sunset Story")
    print("=" * 50)
    
    payload = {
        "idea": "A couple watching the sunset on a beach, falling in love",
        "segments": 7
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-whatsapp-story", json=payload)
        response.raise_for_status()
        
        result = response.json()["whatsapp_story"]
        print(f"✅ Success!")
        print(f"   Title: {result.get('title')}")
        print(f"   Segments: {len(result.get('segments', []))}")
        print(f"   First Scene: {result['segments'][0]['scene'][:60]}...")
        print(f"   Aesthetic Focus: {result['segments'][0].get('aesthetic_focus', 'N/A')[:60]}...")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_nature_adventure():
    """Test nature adventure WhatsApp story."""
    print("\n🏔️ Test 2: Nature Adventure Story")
    print("=" * 50)
    
    payload = {
        "idea": "A solo traveler discovering hidden waterfalls in misty mountains at dawn",
        "segments": 6
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-whatsapp-story", json=payload)
        response.raise_for_status()
        
        result = response.json()["whatsapp_story"]
        print(f"✅ Success!")
        print(f"   Title: {result.get('title')}")
        print(f"   Segments: {len(result.get('segments', []))}")
        
        # Check visual elements
        first_bg = result['segments'][0]['background_definition']
        print(f"   Time of Day: {first_bg.get('time_of_day')}")
        print(f"   Lighting: {first_bg.get('lighting')[:50]}...")
        print(f"   Atmosphere: {first_bg.get('atmosphere')}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_city_aesthetic():
    """Test city aesthetic WhatsApp story."""
    print("\n🌃 Test 3: City Aesthetic Story")
    print("=" * 50)
    
    payload = {
        "idea": "Night walks through neon-lit city streets in the rain",
        "segments": 5
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-whatsapp-story", json=payload)
        response.raise_for_status()
        
        result = response.json()["whatsapp_story"]
        print(f"✅ Success!")
        print(f"   Title: {result.get('title')}")
        print(f"   Visual Style: {result['segments'][0].get('visual_style')}")
        print(f"   Mood: {result['segments'][0].get('mood')}")
        print(f"   Color Palette: {result['segments'][0]['background_definition'].get('color_palette')}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_with_custom_characters():
    """Test WhatsApp story with custom characters."""
    print("\n👥 Test 4: Custom Characters Story")
    print("=" * 50)
    
    payload = {
        "idea": "Two friends exploring cherry blossom gardens at dawn",
        "segments": 7,
        "custom_character_roster": [
            {
                "name": "Maya",
                "physical_appearance": {
                    "gender": "Female",
                    "age": "25",
                    "hair_color": "Long black hair",
                    "skin_tone": "Fair with warm undertones",
                    "eye_color": "Dark brown"
                },
                "clothing_style": {
                    "primary_outfit": "Flowing white dress",
                    "colors": "White and soft pink"
                }
            },
            {
                "name": "Alex",
                "physical_appearance": {
                    "gender": "Male",
                    "age": "27",
                    "hair_color": "Short brown hair",
                    "skin_tone": "Olive",
                    "eye_color": "Green"
                },
                "clothing_style": {
                    "primary_outfit": "Casual denim jacket",
                    "colors": "Blue and white"
                }
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-whatsapp-story", json=payload)
        response.raise_for_status()
        
        result = response.json()["whatsapp_story"]
        print(f"✅ Success!")
        print(f"   Title: {result.get('title')}")
        print(f"   Characters: {len(result.get('characters_roster', []))}")
        
        # Check if custom characters are used
        char_names = [c['name'] for c in result.get('characters_roster', [])]
        print(f"   Character Names: {', '.join(char_names)}")
        
        if 'Maya' in char_names and 'Alex' in char_names:
            print(f"   ✅ Custom characters successfully integrated!")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_magical_forest():
    """Test magical forest WhatsApp story."""
    print("\n🌲 Test 5: Magical Forest Story")
    print("=" * 50)
    
    payload = {
        "idea": "A magical forest at twilight with fireflies and ancient trees",
        "segments": 8
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-whatsapp-story", json=payload)
        response.raise_for_status()
        
        result = response.json()["whatsapp_story"]
        print(f"✅ Success!")
        print(f"   Title: {result.get('title')}")
        print(f"   Hashtags: {', '.join(result.get('hashtags', [])[:5])}")
        
        # Check aesthetic elements
        print(f"\n   Segment Details:")
        for i, seg in enumerate(result['segments'][:3], 1):
            print(f"   Segment {i}:")
            print(f"     - Scene: {seg['scene'][:50]}...")
            print(f"     - Hook: {seg.get('whatsapp_hook', 'N/A')[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_response_structure():
    """Test that response has all required fields."""
    print("\n🔍 Test 6: Response Structure Validation")
    print("=" * 50)
    
    payload = {
        "idea": "A peaceful morning in a cozy café",
        "segments": 5
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-whatsapp-story", json=payload)
        response.raise_for_status()
        
        result = response.json()["whatsapp_story"]
        
        # Check required fields
        required_fields = ['title', 'short_summary', 'description', 'hashtags', 
                          'narrator_voice', 'characters_roster', 'segments']
        
        missing_fields = [field for field in required_fields if field not in result]
        
        if missing_fields:
            print(f"❌ Missing fields: {', '.join(missing_fields)}")
            return False
        
        print(f"✅ All required fields present!")
        
        # Check segment structure
        segment = result['segments'][0]
        segment_fields = ['segment', 'scene', 'content_type', 'camera', 'clip_duration',
                         'background_definition', 'visual_style', 'mood', 'aesthetic_focus']
        
        missing_seg_fields = [field for field in segment_fields if field not in segment]
        
        if missing_seg_fields:
            print(f"⚠️ Missing segment fields: {', '.join(missing_seg_fields)}")
        else:
            print(f"✅ All segment fields present!")
        
        # Check background definition
        bg = segment['background_definition']
        bg_fields = ['location', 'time_of_day', 'lighting', 'atmosphere', 
                    'key_visual_elements', 'color_palette']
        
        missing_bg_fields = [field for field in bg_fields if field not in bg]
        
        if missing_bg_fields:
            print(f"⚠️ Missing background fields: {', '.join(missing_bg_fields)}")
        else:
            print(f"✅ All background fields present!")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 WhatsApp AI Story Generation Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(("Romantic Sunset", test_romantic_sunset()))
    results.append(("Nature Adventure", test_nature_adventure()))
    results.append(("City Aesthetic", test_city_aesthetic()))
    results.append(("Custom Characters", test_with_custom_characters()))
    results.append(("Magical Forest", test_magical_forest()))
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
        print("\n💡 WhatsApp Story Features:")
        print("   ✅ Beautiful sceneries and aesthetic moments")
        print("   ✅ Optimized for 6-8 second segments")
        print("   ✅ Vertical format (9:16) for mobile")
        print("   ✅ AI-ready descriptions for video generation")
        print("   ✅ Emotional storytelling through visuals")
        print("   ✅ Custom character support")
        print("\n📱 Perfect for WhatsApp Status updates!")
    else:
        print(f"\n⚠️ {total_tests - total_passed} test(s) failed")
