"""
Simple one-liner to retry Midnight Protocol failed sets.
Run this tomorrow when the rate limit resets!
"""
import requests

print("🎬 Retrying Midnight Protocol...\n")

response = requests.post(
    "http://127.0.0.1:8000/api/retry-story-by-title",
    json={"title": "Midnight Protocol", "max_retries": 3},
    timeout=600
)

result = response.json()

if result.get("all_completed"):
    print("✅ All sets already completed!")
elif result.get("success") and "story_result" in result:
    story = result["story_result"]
    gen = story.get("generation_summary", {})
    print(f"✅ Success! Generated {gen.get('successful_sets', 0)} sets")
    print(f"📊 Total segments: {gen.get('total_segments_generated', 0)}")
    if gen.get('failed_sets', 0) > 0:
        print(f"❌ Still failed: {gen.get('failed_set_numbers', [])}")
    else:
        print("🎉 All failed sets now completed!")
else:
    print(f"❌ Error: {result.get('error', 'Unknown error')}")
