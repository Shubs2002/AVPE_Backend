"""
Test script for Japanese Anime Generation.
Demonstrates how to generate anime content in different styles.
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def test_shonen_anime():
    """Test Shonen (action) anime generation"""
    print_section("1️⃣  Shonen Anime - Action & Adventure")
    
    payload = {
        "idea": "A teenage martial artist discovers he has the power to control fire and must protect his city from evil spirits",
        "anime_style": "shonen",
        "total_segments": 30,
        "cliffhanger_interval": 10,
        "content_rating": "U/A"
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    print("\n🎌 Generating Shonen Anime...")
    
    # Uncomment to test:
    # response = requests.post(f"{BASE_URL}/generate-anime-auto", json=payload)
    # result = response.json()
    # print(f"\n✅ Generated: {result['result']['anime_title']}")
    # print(f"📊 Segments: {result['result']['generation_summary']['total_segments_generated']}")

def test_shojo_anime():
    """Test Shojo (romance) anime generation"""
    print_section("2️⃣  Shojo Anime - Romance & Emotions")
    
    payload = {
        "idea": "A shy bookworm and a popular athlete are paired for a school project and slowly fall in love",
        "anime_style": "shojo",
        "total_segments": 20,
        "narration_only_first": True,
        "content_rating": "U"
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    print("\n💕 Generating Shojo Anime...")

def test_isekai_anime():
    """Test Isekai (fantasy world) anime generation"""
    print_section("3️⃣  Isekai Anime - Fantasy Adventure")
    
    payload = {
        "idea": "A gamer is transported to a fantasy RPG world where he's overpowered and must defeat the demon king",
        "anime_style": "isekai",
        "total_segments": 35,
        "cliffhanger_interval": 10,
        "content_rating": "U/A"
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    print("\n🗡️ Generating Isekai Anime...")

def test_slice_of_life_anime():
    """Test Slice of Life anime generation"""
    print_section("4️⃣  Slice of Life Anime - Daily Moments")
    
    payload = {
        "idea": "Four friends run a small café and experience the joys and challenges of daily life",
        "anime_style": "slice_of_life",
        "total_segments": 15,
        "no_narration": True,
        "content_rating": "U"
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    print("\n☕ Generating Slice of Life Anime...")

def test_mecha_anime():
    """Test Mecha (giant robots) anime generation"""
    print_section("5️⃣  Mecha Anime - Giant Robots")
    
    payload = {
        "idea": "Teenagers pilot giant robots to defend Earth from an alien invasion",
        "anime_style": "mecha",
        "total_segments": 30,
        "cliffhanger_interval": 10,
        "content_rating": "U/A"
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    print("\n🤖 Generating Mecha Anime...")

def test_seinen_anime():
    """Test Seinen (mature) anime generation"""
    print_section("6️⃣  Seinen Anime - Mature Themes")
    
    payload = {
        "idea": "A detective hunts a serial killer in a corrupt city while dealing with his own dark past",
        "anime_style": "seinen",
        "total_segments": 25,
        "narration_only_first": True,
        "content_rating": "A"
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    print("\n🔍 Generating Seinen Anime...")

def test_custom_characters():
    """Test anime generation with custom characters"""
    print_section("7️⃣  Custom Anime Characters")
    
    payload = {
        "idea": "A high school student with time manipulation powers must prevent a catastrophe",
        "anime_style": "shonen",
        "total_segments": 20,
        "custom_character_roster": [
            {
                "name": "Akira Tanaka",
                "anime_archetype": "protagonist",
                "physical_appearance": {
                    "anime_style_notes": "Classic shonen protagonist design",
                    "gender": "male",
                    "estimated_age": "16",
                    "anime_face": {
                        "eyes": {
                            "size": "LARGE anime eyes",
                            "color": "bright blue with silver flecks",
                            "expression": "determined and intense"
                        }
                    },
                    "anime_hair": {
                        "style": "spiky gravity-defying",
                        "color": "jet black with blue highlights",
                        "special_features": "one ahoge on top"
                    }
                },
                "signature_moves": ["Time Stop", "Temporal Rewind"],
                "catchphrase": "I'll change the future!"
            }
        ]
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    print("\n⏰ Generating Anime with Custom Character...")

def show_anime_styles():
    """Display all available anime styles"""
    print_section("🎨 Available Anime Styles")
    
    styles = {
        "shonen": {
            "target": "Young male (13-18)",
            "features": "Action, battles, friendship, growth",
            "example": "Naruto, One Piece, My Hero Academia"
        },
        "shojo": {
            "target": "Young female (13-18)",
            "features": "Romance, emotions, beautiful aesthetics",
            "example": "Sailor Moon, Fruits Basket, Ouran High School"
        },
        "seinen": {
            "target": "Adult male (18-40)",
            "features": "Mature themes, complex characters",
            "example": "Berserk, Monster, Vinland Saga"
        },
        "slice_of_life": {
            "target": "All ages",
            "features": "Daily life, warmth, gentle humor",
            "example": "K-On!, Barakamon, Non Non Biyori"
        },
        "mecha": {
            "target": "Teens and adults",
            "features": "Giant robots, sci-fi, large battles",
            "example": "Gundam, Evangelion, Code Geass"
        },
        "isekai": {
            "target": "Teens and young adults",
            "features": "Fantasy world, magic, adventure",
            "example": "Re:Zero, Sword Art Online, Overlord"
        }
    }
    
    for style, info in styles.items():
        print(f"📺 {style.upper()}")
        print(f"   Target: {info['target']}")
        print(f"   Features: {info['features']}")
        print(f"   Examples: {info['example']}")
        print()

def show_usage_examples():
    """Show practical usage examples"""
    print_section("💡 Usage Examples")
    
    print("1. Basic Anime Generation:")
    print("""
    curl -X POST "http://127.0.0.1:8000/api/generate-anime-auto" \\
      -H "Content-Type: application/json" \\
      -d '{
        "idea": "Your anime concept here",
        "anime_style": "shonen",
        "total_segments": 30
      }'
    """)
    
    print("\n2. Python Usage:")
    print("""
    import requests
    
    response = requests.post(
        "http://127.0.0.1:8000/api/generate-anime-auto",
        json={
            "idea": "Your anime concept",
            "anime_style": "shojo",
            "total_segments": 20,
            "cliffhanger_interval": 10
        }
    )
    
    result = response.json()
    print(f"Anime: {result['result']['anime_title']}")
    """)
    
    print("\n3. With Custom Characters:")
    print("""
    response = requests.post(
        "http://127.0.0.1:8000/api/generate-anime-auto",
        json={
            "idea": "Your anime concept",
            "anime_style": "shonen",
            "custom_character_roster": [
                {
                    "name": "Hero Name",
                    "anime_archetype": "protagonist",
                    "signature_moves": ["Special Attack"],
                    "catchphrase": "Never give up!"
                }
            ]
        }
    )
    """)

if __name__ == "__main__":
    print("🎌 Japanese Anime Generation Test Suite")
    print("="*70)
    
    show_anime_styles()
    
    print("\n" + "="*70)
    print("  Test Examples (Uncomment API calls to run)")
    print("="*70)
    
    test_shonen_anime()
    test_shojo_anime()
    test_isekai_anime()
    test_slice_of_life_anime()
    test_mecha_anime()
    test_seinen_anime()
    test_custom_characters()
    
    show_usage_examples()
    
    print("\n" + "="*70)
    print("🎉 Anime Generation Test Suite Complete!")
    print("="*70)
    
    print("\n📚 Features:")
    print("   ✅ 6 Anime Styles (Shonen, Shojo, Seinen, Slice of Life, Mecha, Isekai)")
    print("   ✅ Authentic Japanese anime aesthetics")
    print("   ✅ English language dialogue and narration")
    print("   ✅ Large expressive anime eyes")
    print("   ✅ Anime storytelling conventions")
    print("   ✅ Custom character support")
    print("   ✅ Cliffhanger support")
    print("   ✅ Multiple content ratings")
    
    print("\n🚀 Next Steps:")
    print("   1. Choose your anime style")
    print("   2. Create your anime concept")
    print("   3. Uncomment API calls in this script to test")
    print("   4. Check generated_anime/ folder for output")
    print("   5. Generate videos from anime segments")
    
    print("\n📖 Documentation: See ANIME_GENERATION_GUIDE.md")
