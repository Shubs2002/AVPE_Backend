"""
Quick test to verify the endpoint structure is correct.
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

print("🧪 Testing story-status endpoint...\n")

# Test 1: Check status
try:
    response = requests.get(f"{BASE_URL}/story-status/Midnight Protocol")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Status endpoint works!")
        print(json.dumps(result, indent=2))
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "="*50 + "\n")
print("🧪 Testing retry-story-by-title endpoint structure...\n")

# Test 2: Check what the endpoint would receive
payload = {
    "title": "Midnight Protocol",
    "max_retries": 3,
    "base_dir": "generated_movie_script"
}

print("Request payload:")
print(json.dumps(payload, indent=2))
print("\nNote: Not actually calling retry to avoid rate limits.")
print("Run retry_midnight_protocol_simple.py when ready to retry.")
