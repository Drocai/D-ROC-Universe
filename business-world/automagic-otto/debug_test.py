#!/usr/bin/env python3
"""
Debug test script for AutoMagic
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test environment setup"""
    print("=== Environment Test ===")
    load_dotenv()
    
    # Check API keys
    openai_key = os.getenv('OPENAI_API_KEY')
    elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    
    print(f"OpenAI API Key: {'✓' if openai_key else '✗'} ({len(openai_key) if openai_key else 0} chars)")
    print(f"ElevenLabs API Key: {'✓' if elevenlabs_key else '✗'} ({len(elevenlabs_key) if elevenlabs_key else 0} chars)")
    print(f"Google API Key: {'✓' if google_key else '✗'} ({len(google_key) if google_key else 0} chars)")
    
    return openai_key, elevenlabs_key, google_key

def test_openai():
    """Test OpenAI connection"""
    print("\n=== OpenAI Test ===")
    try:
        import openai
        client = openai.OpenAI()
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'API test successful'"}],
            max_tokens=10
        )
        print(f"✓ OpenAI API test successful: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"✗ OpenAI API test failed: {e}")
        return False

def test_elevenlabs():
    """Test ElevenLabs connection"""
    print("\n=== ElevenLabs Test ===")
    try:
        import elevenlabs
        elevenlabs.set_api_key(os.getenv('ELEVENLABS_API_KEY'))
        
        # Test by listing voices
        voices = elevenlabs.voices()
        print(f"✓ ElevenLabs API test successful: Found {len(voices)} voices")
        return True
    except Exception as e:
        print(f"✗ ElevenLabs API test failed: {e}")
        return False

def test_ffmpeg():
    """Test FFmpeg availability"""
    print("\n=== FFmpeg Test ===")
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✓ FFmpeg available: {version_line}")
            return True
        else:
            print(f"✗ FFmpeg test failed: Return code {result.returncode}")
            return False
    except Exception as e:
        print(f"✗ FFmpeg test failed: {e}")
        return False

def test_directories():
    """Test required directories"""
    print("\n=== Directory Test ===")
    dirs = [
        'generated_images',
        'generated_audio', 
        'final_videos',
        'logs'
    ]
    
    all_good = True
    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"✓ {dir_name}/ exists")
        else:
            print(f"✗ {dir_name}/ missing")
            all_good = False
    
    return all_good

def main():
    """Run all tests"""
    print("AutoMagic Debug Test")
    print("=" * 50)
    
    # Test environment
    openai_key, elevenlabs_key, google_key = test_environment()
    
    # Test APIs
    openai_ok = test_openai() if openai_key else False
    elevenlabs_ok = test_elevenlabs() if elevenlabs_key else False
    
    # Test system components
    ffmpeg_ok = test_ffmpeg()
    dirs_ok = test_directories()
    
    # Summary
    print("\n=== Summary ===")
    print(f"Environment: {'✓' if openai_key and elevenlabs_key else '✗'}")
    print(f"OpenAI API: {'✓' if openai_ok else '✗'}")
    print(f"ElevenLabs API: {'✓' if elevenlabs_ok else '✗'}")
    print(f"FFmpeg: {'✓' if ffmpeg_ok else '✗'}")
    print(f"Directories: {'✓' if dirs_ok else '✗'}")
    
    if all([openai_ok, elevenlabs_ok, ffmpeg_ok, dirs_ok]):
        print("\n🎉 All tests passed! AutoMagic should work correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
