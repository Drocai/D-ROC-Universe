#!/usr/bin/env python3
"""
API Connection Test Module for AutoMagic O.T.T.O.

This script tests API connections to all services used by AutoMagic.
"""
import os
import sys
import logging
import time
import json
from dotenv import load_dotenv
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("API-Test")

# Mask API key function for secure display
def mask_api_key(key):
    """Mask an API key for secure display."""
    if not key or len(key) < 8:
        return "Not configured"
    return f"{key[:4]}...{key[-4:]}"

def test_openai_connection():
    """Test connection to OpenAI API."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key or api_key.startswith("YOUR_"):
        logger.error("❌ OpenAI API key not configured")
        return False
    
    logger.info(f"Testing OpenAI API connection (key: {mask_api_key(api_key)})")
    
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        models = client.models.list()
        model_names = [model.id for model in models.data]
        logger.info(f"✅ OpenAI API connection successful. Available models: {len(model_names)}")
        return True
    except Exception as e:
        logger.error(f"❌ OpenAI API connection failed: {str(e)}")
        return False

def test_elevenlabs_connection():
    """Test connection to ElevenLabs API."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not api_key or api_key.startswith("YOUR_"):
        logger.error("❌ ElevenLabs API key not configured")
        return False
    
    logger.info(f"Testing ElevenLabs API connection (key: {mask_api_key(api_key)})")
    
    try:
        import elevenlabs
        elevenlabs.set_api_key(api_key)
        voices = elevenlabs.voices()
        voice_names = [voice.name for voice in voices]
        logger.info(f"✅ ElevenLabs API connection successful. Available voices: {len(voice_names)}")
        return True
    except Exception as e:
        logger.error(f"❌ ElevenLabs API connection failed: {str(e)}")
        return False

def test_google_api_connection():
    """Test connection to Google API."""
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key or api_key.startswith("YOUR_"):
        logger.error("❌ Google API key not configured")
        return False
    
    logger.info(f"Testing Google API connection (key: {mask_api_key(api_key)})")
    
    try:
        import requests
        url = f"https://www.googleapis.com/discovery/v1/apis?key={api_key}"
        response = requests.get(url)
        
        if response.status_code == 200:
            apis = response.json().get('items', [])
            logger.info(f"✅ Google API connection successful. Available APIs: {len(apis)}")
            return True
        else:
            logger.error(f"❌ Google API request failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text[:500]}")
            return False
    except Exception as e:
        logger.error(f"❌ Google API connection failed: {str(e)}")
        return False

def test_ffmpeg_installation():
    """Test FFmpeg installation."""
    logger.info("Testing FFmpeg installation")
    
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            logger.info(f"✅ FFmpeg is properly installed: {version_line}")
            return True
        else:
            logger.error(f"❌ FFmpeg command failed with return code {result.returncode}")
            logger.error(f"stderr: {result.stderr}")
            return False
    except FileNotFoundError:
        logger.error("❌ FFmpeg not found in PATH")
        return False
    except Exception as e:
        logger.error(f"❌ Error testing FFmpeg: {str(e)}")
        return False

def test_youtube_credentials():
    """Test YouTube API credentials."""
    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
    
    if not client_id or client_id.startswith("YOUR_") or not client_secret or client_secret.startswith("YOUR_"):
        logger.error("❌ YouTube API credentials not configured")
        return False
    
    logger.info(f"Testing YouTube API credentials (client ID: {mask_api_key(client_id)})")
    
    # Check for credentials file
    credentials_file = os.getenv("GOOGLE_API_CREDENTIALS_FILE", "youtube_credentials.json")
    
    if not os.path.exists(credentials_file):
        logger.error(f"❌ YouTube credentials file not found: {credentials_file}")
        return False
    
    logger.info(f"✅ YouTube credentials file exists: {credentials_file}")
    
    # Check token file
    token_path = os.getenv("YOUTUBE_TOKEN_PATH", "youtube_token.json")
    if os.path.exists(token_path):
        logger.info(f"✅ YouTube token file exists: {token_path}")
        try:
            with open(token_path, 'r') as f:
                token_data = json.load(f)
            if 'refresh_token' in token_data:
                logger.info("✅ YouTube token contains refresh_token")
                return True
            else:
                logger.warning("⚠️ YouTube token file doesn't contain refresh_token")
                return False
        except Exception as e:
            logger.error(f"❌ Error reading YouTube token file: {str(e)}")
            return False
    else:
        logger.warning("⚠️ YouTube token file not found, OAuth flow will be required on first run")
        return False

def main():
    """Main function to test all API connections."""
    load_dotenv()
    
    print("\n" + "="*60)
    print(" 🧪 AutoMagic O.T.T.O. API Connection Tests")
    print("="*60)
    
    # Test OpenAI API
    print("\n📡 Testing OpenAI API...")
    openai_success = test_openai_connection()
    
    # Test ElevenLabs API
    print("\n📡 Testing ElevenLabs API...")
    elevenlabs_success = test_elevenlabs_connection()
    
    # Test Google API
    print("\n📡 Testing Google API...")
    google_success = test_google_api_connection()
    
    # Test FFmpeg
    print("\n🎬 Testing FFmpeg installation...")
    ffmpeg_success = test_ffmpeg_installation()
    
    # Test YouTube credentials
    print("\n📡 Testing YouTube credentials...")
    youtube_success = test_youtube_credentials()
    
    # Overall status
    print("\n" + "="*60)
    print(" 📊 API Connection Test Results")
    print("="*60)
    print(f"OpenAI API:      {'✅ PASSED' if openai_success else '❌ FAILED'}")
    print(f"ElevenLabs API:  {'✅ PASSED' if elevenlabs_success else '❌ FAILED'}")
    print(f"Google API:      {'✅ PASSED' if google_success else '❌ FAILED'}")
    print(f"FFmpeg:          {'✅ PASSED' if ffmpeg_success else '❌ FAILED'}")
    print(f"YouTube Creds:   {'✅ PASSED' if youtube_success else '⚠️ WARNING'}")
    
    all_required_passed = openai_success and elevenlabs_success and ffmpeg_success
    
    print("\n" + "="*60)
    if all_required_passed:
        print("🎉 All critical API connections successful!")
        print("   System is ready for use with AutoMagic.")
    else:
        print("⚠️ Some API connections failed.")
        print("   Please fix the failed connections before using AutoMagic.")
    print("="*60 + "\n")
    
    return 0 if all_required_passed else 1

if __name__ == "__main__":
    sys.exit(main())
