#!/usr/bin/env python3
"""
Simple API test for AutoMagic debugging
"""

import os
import sys
from dotenv import load_dotenv

def test_openai_api():
    """Test different OpenAI API endpoints"""
    print("Testing OpenAI API...")
    load_dotenv()
    
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        print("✓ OpenAI client created")
        
        # Test 1: List models (basic permission)
        try:
            models = client.models.list()
            print("✓ Models list successful")
        except Exception as e:
            print(f"✗ Models list failed: {e}")
        
        # Test 2: Chat completion (should work with most keys)
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say hello"}],
                max_tokens=5
            )
            print("✓ Chat completion successful")
        except Exception as e:
            print(f"✗ Chat completion failed: {e}")
        
        # Test 3: Image generation (requires special permissions)
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt="A simple red circle",
                n=1,
                size="1024x1024"
            )
            print("✓ Image generation successful")
        except Exception as e:
            print(f"✗ Image generation failed: {e}")
            print(f"  Error details: {type(e).__name__}: {str(e)}")
            
    except Exception as e:
        print(f"✗ OpenAI setup failed: {e}")

def test_elevenlabs_api():
    """Test ElevenLabs API"""
    print("\nTesting ElevenLabs API...")
    
    try:
        import elevenlabs
        api_key = os.getenv('ELEVENLABS_API_KEY')
        if not api_key:
            print("✗ No ElevenLabs API key found")
            return
            
        elevenlabs.set_api_key(api_key)
        
        # Test listing voices
        voices = elevenlabs.voices()
        print(f"✓ ElevenLabs API working - found {len(voices)} voices")
        
        if voices:
            print(f"  Sample voice: {voices[0].name}")
            
    except Exception as e:
        print(f"✗ ElevenLabs API failed: {e}")

def test_ffmpeg():
    """Test FFmpeg"""
    print("\nTesting FFmpeg...")
    
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✓ FFmpeg working: {version_line}")
        else:
            print(f"✗ FFmpeg failed with return code: {result.returncode}")
    except FileNotFoundError:
        print("✗ FFmpeg not found in PATH")
    except Exception as e:
        print(f"✗ FFmpeg test failed: {e}")

if __name__ == "__main__":
    print("AutoMagic Simple API Test")
    print("=" * 40)
    
    test_openai_api()
    test_elevenlabs_api()
    test_ffmpeg()
    
    print("\nTest completed!")
