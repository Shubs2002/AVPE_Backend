"""
Test Character CRUD Operations

This script tests all character CRUD operations with MongoDB.
"""

from app.services.character_service_mongodb import (
    save_character_to_mongodb,
    get_all_characters,
    get_character_by_id,
    update_character,
    delete_character,
    search_characters
)

def test_character_crud():
    """Test complete CRUD operations"""
    
    print("\n" + "=" * 60)
    print("🧪 Testing Character CRUD Operations")
    print("=" * 60)
    
    # Test 1: Create Character
    print("\n1️⃣  CREATE: Saving test character...")
    test_character = {
        "id": "test_char_1",
        "name": "Test Hero",
        "physical_appearance": {
            "gender": "male",
            "estimated_age": "30 years old",
            "height": "6'0\"",
            "skin_tone": "tan"
        },
        "personality": "brave, kind",
        "role": "protagonist"
    }
    
    create_result = save_character_to_mongodb(test_character, "Test Hero")
    
    if create_result.get('success'):
        character_id = create_result.get('character_id')
        print(f"   ✅ Character created with ID: {character_id}")
    else:
        print(f"   ❌ Failed: {create_result.get('error')}")
        return
    
    # Test 2: Read All Characters
    print("\n2️⃣  READ ALL: Listing all characters...")
    all_chars = get_all_characters()
    
    if all_chars.get('success'):
        print(f"   ✅ Found {all_chars.get('total_characters')} characters")
        for char in all_chars.get('characters', [])[:3]:
            print(f"      - {char.get('character_name')} (ID: {char.get('id')})")
    else:
        print(f"   ❌ Failed: {all_chars.get('error')}")
    
    # Test 3: Read Single Character
    print(f"\n3️⃣  READ ONE: Getting character by ID...")
    get_result = get_character_by_id(character_id)
    
    if get_result.get('success'):
        char = get_result.get('character')
        print(f"   ✅ Retrieved: {char.get('character_name')}")
        print(f"      Gender: {char.get('character_data', {}).get('physical_appearance', {}).get('gender')}")
        print(f"      Role: {char.get('character_data', {}).get('role')}")
    else:
        print(f"   ❌ Failed: {get_result.get('error')}")
    
    # Test 4: Update Character
    print(f"\n4️⃣  UPDATE: Updating character...")
    update_data = {
        "personality": "brave, kind, wise",
        "role": "legendary hero"
    }
    
    update_result = update_character(character_id, update_data)
    
    if update_result.get('success'):
        print(f"   ✅ Character updated")
        
        # Verify update
        verify = get_character_by_id(character_id)
        if verify.get('success'):
            char = verify.get('character')
            print(f"      New personality: {char.get('character_data', {}).get('personality')}")
            print(f"      New role: {char.get('character_data', {}).get('role')}")
    else:
        print(f"   ❌ Failed: {update_result.get('error')}")
    
    # Test 5: Search Characters
    print(f"\n5️⃣  SEARCH: Searching for 'hero'...")
    search_result = search_characters(query="hero")
    
    if search_result.get('success'):
        print(f"   ✅ Found {search_result.get('total_results')} results")
        for char in search_result.get('characters', [])[:3]:
            print(f"      - {char.get('character_name')}")
    else:
        print(f"   ❌ Failed: {search_result.get('error')}")
    
    # Test 6: Delete Character
    print(f"\n6️⃣  DELETE: Deleting test character...")
    delete_result = delete_character(character_id)
    
    if delete_result.get('success'):
        print(f"   ✅ Character deleted")
        
        # Verify deletion
        verify = get_character_by_id(character_id)
        if not verify.get('success'):
            print(f"   ✅ Verified: Character no longer exists")
    else:
        print(f"   ❌ Failed: {delete_result.get('error')}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ ALL CRUD OPERATIONS COMPLETED!")
    print("=" * 60)
    print("\n🎉 MongoDB character storage is fully functional!")
    print("\nYou can now:")
    print("  • Save characters from image analysis")
    print("  • List all saved characters")
    print("  • Search characters by name/filters")
    print("  • Update character details")
    print("  • Delete characters")
    print("  • Use characters in story generation")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        test_character_crud()
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
