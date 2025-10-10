"""
Test script for the File Storage Manager.
Demonstrates all features of the storage management system.
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_get_content_types():
    """Test getting all supported content types"""
    print_section("1. Get Supported Content Types")
    
    response = requests.get(f"{BASE_URL}/storage/content-types")
    result = response.json()
    
    print("Supported Content Types:")
    for content_type in result["content_types"]:
        desc = result["descriptions"].get(content_type, "")
        print(f"  • {content_type}: {desc}")

def test_list_content(content_type="movies"):
    """Test listing content of a specific type"""
    print_section(f"2. List All {content_type.title()}")
    
    response = requests.get(f"{BASE_URL}/storage/list/{content_type}")
    result = response.json()
    
    if result["success"]:
        print(f"Found {result['count']} items:")
        for item in result["items"]:
            print(f"  • {item}")
    else:
        print(f"Error: {result.get('error')}")

def test_get_content_info(content_type="movies", title="Midnight Protocol"):
    """Test getting detailed info about a content item"""
    print_section(f"3. Get Info for '{title}'")
    
    # URL encode the title
    encoded_title = title.replace(" ", "%20")
    response = requests.get(f"{BASE_URL}/storage/info/{content_type}/{encoded_title}")
    result = response.json()
    
    if result.get("exists"):
        print(f"✅ Content exists!")
        print(f"   Directory: {result.get('directory')}")
        print(f"   Has metadata: {result.get('has_metadata')}")
        print(f"   Has sets: {result.get('has_sets')}")
        print(f"   Set count: {result.get('set_count')}")
        print(f"   Existing sets: {result.get('existing_sets')}")
        
        if result.get('total_sets_expected'):
            print(f"   Total expected: {result.get('total_sets_expected')}")
            print(f"   Missing sets: {result.get('missing_sets')}")
            print(f"   Is complete: {result.get('is_complete')}")
    else:
        print(f"❌ Content not found")

def test_storage_stats():
    """Test getting overall storage statistics"""
    print_section("4. Storage Statistics")
    
    response = requests.get(f"{BASE_URL}/storage/stats")
    result = response.json()
    
    if result["success"]:
        print(f"Total items across all types: {result['total_items']}\n")
        
        for content_type, stats in result["by_type"].items():
            print(f"{content_type}:")
            print(f"  Count: {stats['count']}")
            if stats['items']:
                print(f"  Items: {', '.join(stats['items'][:5])}")
                if len(stats['items']) > 5:
                    print(f"         ... and {len(stats['items']) - 5} more")
            print()

def test_migrate_content():
    """Test migrating content from old structure"""
    print_section("5. Migrate Content (Example)")
    
    print("To migrate content from old structure:")
    print()
    print("POST /api/storage/migrate")
    print(json.dumps({
        "old_directory": "generated_movie_script",
        "content_type": "movies"
    }, indent=2))
    print()
    print("This will:")
    print("  1. Find all metadata files in old directory")
    print("  2. Create new organized folder structure")
    print("  3. Copy files to new locations")
    print("  4. Preserve all data")
    print()
    print("⚠️  Not running automatically to avoid duplicates")

def test_direct_storage_manager():
    """Test using the storage manager directly (Python)"""
    print_section("6. Direct Python Usage")
    
    print("You can also use the storage manager directly in Python:")
    print()
    print("```python")
    print("from app.utils import storage_manager, ContentType")
    print()
    print("# Save metadata")
    print("storage_manager.save_metadata(")
    print("    ContentType.MOVIE,")
    print("    'My Movie Title',")
    print("    metadata_dict")
    print(")")
    print()
    print("# Save a set")
    print("storage_manager.save_set(")
    print("    ContentType.MOVIE,")
    print("    'My Movie Title',")
    print("    set_number=1,")
    print("    set_data=set_dict")
    print(")")
    print()
    print("# Get content info")
    print("info = storage_manager.get_content_info(")
    print("    ContentType.MOVIE,")
    print("    'My Movie Title'")
    print(")")
    print("```")

if __name__ == "__main__":
    print("🗂️  File Storage Manager Test Suite")
    print("="*60)
    
    try:
        # Run all tests
        test_get_content_types()
        test_list_content("movies")
        test_get_content_info("movies", "Midnight Protocol")
        test_storage_stats()
        test_migrate_content()
        test_direct_storage_manager()
        
        print_section("✅ Test Suite Complete")
        print("All storage management features demonstrated!")
        print()
        print("💡 Next Steps:")
        print("  1. Integrate storage manager into your generation endpoints")
        print("  2. Migrate existing content using /storage/migrate")
        print("  3. Use new organized structure for all new content")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server")
        print("Make sure the server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")
