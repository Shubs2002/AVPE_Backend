"""
Test script for the new retry-by-title endpoint.
This makes it super easy to retry failed sets - just provide the story title!
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def check_story_status(title: str):
    """Check the status of a story to see which sets failed."""
    print(f"📊 Checking status for: {title}")
    
    # URL encode the title for the GET request
    encoded_title = title.replace(" ", "%20")
    response = requests.get(f"{BASE_URL}/story-status/{encoded_title}")
    
    if response.status_code == 200:
        result = response.json()
        
        if result["success"]:
            print(f"✅ Story found!")
            print(f"   Title: {result['title']}")
            print(f"   Total sets: {result.get('total_sets', 'N/A')}")
            print(f"   Successful sets: {result.get('successful_sets', 'N/A')}")
            print(f"   Failed sets: {result.get('failed_count', 0)}")
            
            if result.get('failed_sets'):
                print(f"   Failed set numbers: {result['failed_sets']}")
            else:
                print(f"   🎉 {result.get('message', 'All sets completed!')}")
        else:
            print(f"❌ {result.get('error', 'Unknown error')}")
    else:
        print(f"❌ Request failed with status {response.status_code}")
    
    print()
    return response.json() if response.status_code == 200 else None


def retry_story(title: str, max_retries: int = 3):
    """Retry failed sets for a story by title."""
    print(f"🔄 Retrying failed sets for: {title}")
    print(f"⚙️  Max retries per set: {max_retries}\n")
    
    payload = {
        "title": title,
        "max_retries": max_retries
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/retry-story-by-title",
            json=payload,
            timeout=600  # 10 minute timeout
        )
        response.raise_for_status()
        
        result = response.json()
        
        # Check if all sets were already completed
        if result.get("all_completed"):
            print("✅ All sets already completed!")
            print(f"   {result.get('message', '')}")
            return result
        
        # Check for errors
        if not result.get("success", True):
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            return result
        
        # Display results
        print("✅ Retry Complete!\n")
        
        story_result = result.get('story_result', {})
        gen_summary = story_result.get('generation_summary', {})
        
        print(f"📊 Results:")
        print(f"   Original failed sets: {result.get('original_failed_count', 0)}")
        print(f"   Successfully generated: {gen_summary.get('successful_sets', 0)} sets")
        print(f"   Still failed: {gen_summary.get('failed_sets', 0)} sets")
        print(f"   Total segments: {gen_summary.get('total_segments_generated', 0)}")
        
        if gen_summary.get('failed_set_numbers'):
            print(f"   🔴 Still failing: {gen_summary.get('failed_set_numbers')}")
            print(f"\n💡 Tip: You can run this script again to retry the remaining sets")
        else:
            print(f"\n🎉 All sets completed successfully!")
        
        retry_info = story_result.get('retry_info', {})
        if retry_info:
            print(f"\n🔄 Retry Info:")
            print(f"   Total attempts: {retry_info.get('total_retry_attempts', 0)}")
            print(f"   Successful retries: {retry_info.get('successful_retries', 0)}")
        
        print(f"\n💾 Files saved to: generated_movie_script")
        
        return result
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        if e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"Details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None


if __name__ == "__main__":
    print("🎬 Story Retry Tool - By Title\n")
    print("=" * 50)
    
    # Example 1: Check status first
    print("\n1️⃣  Checking story status...\n")
    status = check_story_status("Midnight Protocol")
    
    # Example 2: Retry if there are failed sets
    if status and status.get("success") and status.get("failed_sets"):
        print("=" * 50)
        print("\n2️⃣  Retrying failed sets...\n")
        retry_story("Midnight Protocol", max_retries=3)
    elif status and status.get("success"):
        print("✅ No failed sets to retry!")
    
    print("\n" + "=" * 50)
    print("\n💡 Usage Examples:")
    print("   # Check status only:")
    print("   check_story_status('Midnight Protocol')")
    print()
    print("   # Retry failed sets:")
    print("   retry_story('Midnight Protocol', max_retries=3)")
