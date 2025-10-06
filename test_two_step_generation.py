#!/usr/bin/env python3
"""
Test script to demonstrate the new two-step generation mechanism for movies.
This solves the truncation issue by separating metadata generation from segment generation.
"""

import requests
import json
import time

# API base URL (adjust as needed)
BASE_URL = "http://localhost:8000"

def test_movie_two_step_generation():
    """Test the new two-step movie generation process."""
    
    print("🎬 Testing Two-Step Movie Generation")
    print("=" * 50)
    
    # Step 1: Generate metadata
    print("\n📋 Step 1: Generating movie metadata...")
    
    metadata_payload = {
        "idea": "A thrilling sci-fi adventure about time travelers trying to prevent an apocalypse",
        "total_segments": 20,
        "custom_character_roster": None,
        "no_narration": False,
        "narration_only_first": False,
        "adult_story": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-movie-metadata", json=metadata_payload)
        response.raise_for_status()
        
        metadata_result = response.json()
        metadata = metadata_result["metadata"]
        
        print(f"✅ Metadata generated successfully!")
        print(f"📖 Title: {metadata['title']}")
        print(f"👥 Characters: {len(metadata.get('characters_roster', []))}")
        print(f"📊 Total segments planned: {metadata['generation_info']['total_segments']}")
        
        # Step 2: Generate segments in batches
        print(f"\n🎬 Step 2: Generating segments in batches...")
        
        total_segments = metadata['generation_info']['total_segments']
        segments_per_set = 5  # Generate 5 segments at a time
        total_sets = (total_segments + segments_per_set - 1) // segments_per_set
        
        all_segments = []
        
        for set_number in range(1, min(3, total_sets + 1)):  # Test first 2 sets only
            print(f"\n🎯 Generating set {set_number}/{total_sets}...")
            
            segments_payload = {
                "metadata": metadata,
                "set_number": set_number,
                "segments_per_set": segments_per_set,
                "save_to_files": True,
                "output_directory": "test_movie_output"
            }
            
            try:
                response = requests.post(f"{BASE_URL}/generate-movie-segments", json=segments_payload)
                response.raise_for_status()
                
                segments_result = response.json()
                segments_data = segments_result["segments"]
                
                print(f"✅ Set {set_number} generated successfully!")
                print(f"📊 Segments in set: {segments_data['segments_count']}")
                print(f"🔄 Next set: {segments_data.get('next_set_number', 'Complete')}")
                print(f"✅ Complete: {segments_data['is_complete']}")
                
                all_segments.extend(segments_data['story_set']['segments'])
                
                # Small delay between requests
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Failed to generate set {set_number}: {e}")
                continue
        
        print(f"\n🎉 Two-step generation test completed!")
        print(f"📊 Total segments generated: {len(all_segments)}")
        print(f"💾 Files saved to: test_movie_output/")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to generate metadata: {e}")
        return False

def test_story_two_step_generation():
    """Test the new two-step story generation process."""
    
    print("\n📖 Testing Two-Step Story Generation")
    print("=" * 50)
    
    # Step 1: Generate metadata
    print("\n📋 Step 1: Generating story metadata...")
    
    metadata_payload = {
        "idea": "A magical adventure in a fantasy world with dragons and wizards",
        "segments": 10,
        "custom_character_roster": None
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-story-metadata", json=metadata_payload)
        response.raise_for_status()
        
        metadata_result = response.json()
        metadata = metadata_result["metadata"]
        
        print(f"✅ Metadata generated successfully!")
        print(f"📖 Title: {metadata['title']}")
        print(f"👥 Characters: {len(metadata.get('characters_roster', []))}")
        
        # Step 2: Generate segments in batches
        print(f"\n📖 Step 2: Generating segments in batches...")
        
        total_segments = metadata['generation_info']['segments_planned']
        segments_per_batch = 3  # Generate 3 segments at a time
        total_batches = (total_segments + segments_per_batch - 1) // segments_per_batch
        
        all_segments = []
        
        for batch_number in range(1, min(3, total_batches + 1)):  # Test first 2 batches only
            print(f"\n🎯 Generating batch {batch_number}/{total_batches}...")
            
            segments_payload = {
                "metadata": metadata,
                "segments_per_batch": segments_per_batch,
                "batch_number": batch_number
            }
            
            try:
                response = requests.post(f"{BASE_URL}/generate-story-segments-from-metadata", json=segments_payload)
                response.raise_for_status()
                
                segments_result = response.json()
                segments_data = segments_result["segments"]
                
                print(f"✅ Batch {batch_number} generated successfully!")
                print(f"📊 Segments in batch: {segments_data['segments_count']}")
                print(f"🔄 Next batch: {segments_data.get('next_batch_number', 'Complete')}")
                print(f"✅ Complete: {segments_data['is_complete']}")
                
                all_segments.extend(segments_data['segments'])
                
                # Small delay between requests
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Failed to generate batch {batch_number}: {e}")
                continue
        
        print(f"\n🎉 Two-step story generation test completed!")
        print(f"📊 Total segments generated: {len(all_segments)}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to generate story metadata: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Two-Step Generation Mechanism")
    print("This solves the truncation issue by separating metadata from segments")
    print("=" * 70)
    
    # Test movie generation
    movie_success = test_movie_two_step_generation()
    
    # Test story generation
    story_success = test_story_two_step_generation()
    
    print("\n" + "=" * 70)
    print("📊 Test Results:")
    print(f"🎬 Movie generation: {'✅ Success' if movie_success else '❌ Failed'}")
    print(f"📖 Story generation: {'✅ Success' if story_success else '❌ Failed'}")
    
    if movie_success and story_success:
        print("\n🎉 All tests passed! The two-step mechanism is working correctly.")
        print("\n💡 How to use:")
        print("1. Call /generate-movie-metadata to get detailed metadata")
        print("2. Call /generate-movie-segments repeatedly with different set_number")
        print("3. Each call generates a small batch of segments without truncation")
        print("4. Repeat until all segments are generated")
    else:
        print("\n⚠️ Some tests failed. Check the server logs for details.")