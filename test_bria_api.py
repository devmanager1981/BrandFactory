"""Quick test to verify Bria API token and find correct endpoints"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("BRIA_API_TOKEN")
BASE_URL = "https://engine.prod.bria-api.com/v1"

headers = {
    "api_token": API_TOKEN,
    "Content-Type": "application/json"
}

print(f"Testing with token: {API_TOKEN[:10]}...")
print(f"Base URL: {BASE_URL}")

# Try different endpoint formats
endpoints_to_try = [
    "/text_to_image/base",
    "/image/generate",
    "/structured_prompt/generate",
    "/text-to-image/base",
    "/generate",
]

for endpoint in endpoints_to_try:
    url = f"{BASE_URL}{endpoint}"
    print(f"\nTrying: {url}")
    
    payload = {
        "prompt": "A simple test",
        "num_results": 1
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"  Status: {response.status_code}")
        if response.status_code != 404:
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")
