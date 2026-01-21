#!/usr/bin/env python3
"""Debug Groq API"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"API Key: {api_key[:20]}...")

# Test 1: List models
print("\n[1] Testing connection - List models...")
try:
    response = requests.get(
        "https://api.groq.com/openai/v1/models",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=10
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        models = response.json()
        print(f"Available models: {len(models.get('data', []))}")
        for model in models.get('data', [])[:5]:
            print(f"  - {model.get('id')}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Simple generation
print("\n[2] Testing generation...")
try:
    payload = {
        "model": "llama-3.1-8b-instant",  # Try a different model
        "messages": [{"role": "user", "content": "Say hello in one sentence"}],
        "max_tokens": 50,
        "temperature": 0.7
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=30
    )

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        message = result['choices'][0]['message']['content']
        print(f"Success! Response: {message}")
    else:
        print(f"Error: {response.text}")

except Exception as e:
    print(f"Error: {e}")
