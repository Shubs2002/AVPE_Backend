"""
Test script for Daily Character Life Content Generation.
Perfect for Instagram character pages!
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def test_basic_generation():
    """Test basic daily character content generation"""
    print_section("1️⃣  Basic Generation - Mirror Scare")
    
    payload = {
        "idea": "Character sees his own reflection in the mirror and gets scared thinking it's someone else",
        "num_segments": 7
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    print("\n🎬 Generating content...")
    
    # Uncomment to test:
    # response = requests.post(f"{BASE_URL}/generate-daily-character", json=payload)
    # result = response.json()
    # print(f"\n✅ Generated: {result['content']['title']}")
    # print(f"🎭 Character: {result['content']['character']['name']}")
    # print(f"📊 Segments: {len(result['content']['segments'])}")

def test_with_character_info():
    """Test with custom character information"""
    print_section("2️⃣  With Character Info - Cooking Disaster")
    
    payload = {
        "idea": "Character tries to make breakfast but burns everything and sets off smoke alarm",
        "num_segments": 8,
        "character_info": {
            "name": "Alex",
            "personality": "Clumsy but optimistic, never gives up",
            "appearance": "Messy brown hair, casual hoodie, tired eyes, always has a coffee mug",
            "age": "mid-20s",
            "signature_trait": "Always looks half-asleep",
            "mannerisms": ["Rubs eyes when confused", "Yawns frequently", "Stumbles over things"]
        }
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    print("\n🍳 Generating cooking disaster...")

def test_funny_reaction():
    """Test funny reaction content"""
    print_section("3️⃣  Funny Reaction - Hearing Noise")
    
    payload = {
        "idea": "Character hears a small noise and investigates it like a detective, turns out it's just the fridge",
        "num_segments": 6,
        "character_info": {
            "name": "Sam",
            "personality": "Paranoid but brave, watches too many detective shows",
            "appearance": "Casual clothes, always alert expression"
        }
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    print("\n🔍 Generating detective moment...")

def test_relatable_struggle():
    """Test relatable struggle content"""
    print_section("4️⃣  Relatable Struggle - Waking Up")
    
    payload = {
        "idea": "Character's alarm goes off but they keep hitting snooze and having weird mini-dreams between alarms",
        "num_segments": 7,
        "character_info": {
            "name": "Jordan",
            "personality": "Definitely not a morning person, loves sleep more than anything",
            "appearance": "Messy hair, pajamas, sleepy eyes, pillow marks on face"
        }
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    print("\n😴 Generating morning struggle...")

def test_character_quirk():
    """Test character quirk content"""
    print_section("5️⃣  Character Quirk - Talking to Plants")
    
    payload = {
        "idea": "Character has full conversations with their houseplants and gets offended when they don't respond",
        "num_segments": 5,
        "character_info": {
            "name": "Taylor",
            "personality": "Lonely but creative, treats plants like friends",
            "appearance": "Comfortable clothes, gentle smile, always has dirt on hands"
        }
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    print("\n🌱 Generating plant conversation...")

def test_everyday_adventure():
    """Test everyday adventure content"""
    print_section("6️⃣  Everyday Adventure - Grocery Shopping")
    
    payload = {
        "idea": "Character goes to buy one thing at the store but gets distracted and buys everything except what they came for",
        "num_segments": 8,
        "character_info": {
            "name": "Casey",
            "personality": "Easily distracted, impulsive shopper",
            "appearance": "Casual style, shopping bag always full"
        }
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    print("\n🛒 Generating shopping adventure...")

def test_maximum_segments():
    """Test with maximum segments"""
    print_section("7️⃣  Maximum Segments - Epic Fail")
    
    payload = {
        "idea": "Character tries to do a simple task but everything that can go wrong does go wrong",
        "num_segments": 10,  # Maximum allowed
        "character_info": {
            "name": "Morgan",
            "personality": "Unlucky but persistent",
            "appearance": "Casual clothes, band-aids everywhere"
        }
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    print("\n💥 Generating epic fail sequence...")

def show_content_ideas():
    """Display content idea categories"""
    print_section("💡 Content Idea Categories")
    
    categories = {
        "Funny Reactions": [
            "Seeing reflection and getting scared",
            "Hearing noise and investigating",
            "Finding something unexpected",
            "Trying new food with funny reaction"
        ],
        "Relatable Struggles": [
            "Can't wake up despite alarms",
            "Cooking disaster",
            "Losing keys",
            "Technology confusion"
        ],
        "Character Quirks": [
            "Weird morning routine",
            "Talking to themselves",
            "Dancing when alone",
            "Making faces while thinking"
        ],
        "Everyday Adventures": [
            "Grocery shopping distraction",
            "Parallel parking fail",
            "Waiting for delivery",
            "Social awkwardness"
        ]
    }
    
    for category, ideas in categories.items():
        print(f"📺 {category}:")
        for idea in ideas:
            print(f"   • {idea}")
        print()

def show_instagram_tips():
    """Show Instagram optimization tips"""
    print_section("📱 Instagram Optimization Tips")
    
    print("🎯 Content Structure:")
    print("   Segments 1-2: HOOK (grab attention)")
    print("   Segments 3-6: BUILD (develop moment)")
    print("   Segments 7-10: PAYOFF (punchline)")
    
    print("\n✨ Visual Storytelling:")
    print("   • Show, don't tell")
    print("   • Facial expressions are key")
    print("   • Physical comedy works")
    print("   • Minimal dialogue")
    
    print("\n💬 Engagement Tactics:")
    print("   • Hook in first 2 seconds")
    print("   • Relatable situations")
    print("   • 'Tag someone who...'")
    print("   • Trending audio")
    
    print("\n#️⃣ Hashtag Strategy:")
    print("   #CharacterContent #DailyLife #Relatable")
    print("   #Funny #Viral #InstagramReels #Shorts")

if __name__ == "__main__":
    print("🎬 Daily Character Life Content - Test Suite")
    print("="*70)
    print("Perfect for Instagram character pages!")
    
    show_content_ideas()
    show_instagram_tips()
    
    print("\n" + "="*70)
    print("  Test Examples (Uncomment API calls to run)")
    print("="*70)
    
    test_basic_generation()
    test_with_character_info()
    test_funny_reaction()
    test_relatable_struggle()
    test_character_quirk()
    test_everyday_adventure()
    test_maximum_segments()
    
    print("\n" + "="*70)
    print("🎉 Test Suite Complete!")
    print("="*70)
    
    print("\n📚 Features:")
    print("   ✅ Simple - Just idea + segments")
    print("   ✅ Quick - Max 10 segments (~1 min)")
    print("   ✅ Viral - Instagram optimized")
    print("   ✅ Visual - Show, don't tell")
    print("   ✅ Relatable - Everyday moments")
    print("   ✅ Character - Personality driven")
    
    print("\n🚀 Perfect For:")
    print("   • Instagram character pages")
    print("   • Daily content posting")
    print("   • Building character audience")
    print("   • Relatable comedy content")
    print("   • 1-minute viral videos")
    
    print("\n💡 Next Steps:")
    print("   1. Choose a daily life moment")
    print("   2. Decide on segment count (7-10)")
    print("   3. Optionally define your character")
    print("   4. Uncomment API calls to test")
    print("   5. Generate videos from segments")
    print("   6. Post to Instagram!")
    
    print("\n📖 Documentation: See DAILY_CHARACTER_GUIDE.md")
