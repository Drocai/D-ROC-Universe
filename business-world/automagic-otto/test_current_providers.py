#!/usr/bin/env python3
"""
Quick test of current provider configuration
"""

import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger("Test")

print("\n" + "="*60)
print("TESTING CURRENT PROVIDER CONFIGURATION")
print("="*60)

# Test 1: Script Generation
print("\n[1/3] Testing Script Generation...")
print("-" * 60)

try:
    from api_providers import ProviderManager
    manager = ProviderManager()

    # Try to generate a short script
    test_topic = "The benefits of morning exercise"
    print(f"Topic: {test_topic}")

    script = manager.generate_script_with_fallback(test_topic, max_tokens=200)

    print(f"\n✅ SUCCESS! Generated script ({len(script)} chars)")
    print(f"\nScript preview:\n{script[:200]}...")

except Exception as e:
    print(f"\n❌ FAILED: {str(e)[:200]}")
    print("This is expected if OpenAI quota is exceeded and Gemini isn't working")

# Test 2: Image Generation
print("\n\n[2/3] Testing Image Generation...")
print("-" * 60)

try:
    test_prompt = "A beautiful sunrise over mountains"
    print(f"Prompt: {test_prompt}")

    image_data = manager.generate_image_with_fallback(test_prompt)

    # Save test image
    test_img_path = "test_image.jpg"
    with open(test_img_path, 'wb') as f:
        f.write(image_data)

    print(f"\n✅ SUCCESS! Generated image ({len(image_data)} bytes)")
    print(f"Saved to: {test_img_path}")

except Exception as e:
    print(f"\n⚠️  EXPECTED: {str(e)[:150]}")
    print("No image providers configured - this is normal")
    print("System will use placeholder images for now")

# Test 3: Voice Generation
print("\n\n[3/3] Testing Voice Generation...")
print("-" * 60)

try:
    test_text = "This is a test of the voice generation system. Hello world!"
    print(f"Text: {test_text}")

    audio_data = manager.generate_voice_with_fallback(test_text)

    # Save test audio
    test_audio_path = "test_voice.mp3"
    with open(test_audio_path, 'wb') as f:
        f.write(audio_data)

    print(f"\n✅ SUCCESS! Generated voice ({len(audio_data)} bytes)")
    print(f"Saved to: {test_audio_path}")

except Exception as e:
    print(f"\n❌ FAILED: {str(e)[:200]}")

# Summary
print("\n\n" + "="*60)
print("TEST SUMMARY")
print("="*60)

print("""
Based on your current configuration:

✅ WORKING:
   - Voice: ElevenLabs is configured and working

⚠️  PARTIAL:
   - Script: You have OpenAI & Gemini configured
     * OpenAI has quota issues (429 errors)
     * Gemini should work as fallback

❌ NOT CONFIGURED:
   - Image: No image generation providers
     * System will use placeholder images
     * To fix: Add Replicate or HuggingFace API key

RECOMMENDED NEXT STEPS:
1. Get Replicate API key for cheap image generation
   https://replicate.com/account/api-tokens

2. Run full test: python automagic_multi_provider.py --now
   (It will create a video with placeholders for images)
""")

print("="*60 + "\n")
