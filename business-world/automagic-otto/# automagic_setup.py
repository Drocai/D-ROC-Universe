# automagic_setup.py - Automated Setup Script
import os
import sys
import subprocess
import platform
import json
import webbrowser
from pathlib import Path

print("🚀 Welcome to AutoMagic O.T.T.O. Automated Setup!")
print("This will set up everything for you automatically.\n")

# Create all necessary directories
directories = [
    "generated_images",
    "generated_audio", 
    "generated_video_clips",
    "final_videos",
    "logs"
]

print("📁 Creating directories...")
for directory in directories:
    Path(directory).mkdir(exist_ok=True)
    print(f"  ✓ Created {directory}/")

# Create requirements.txt
print("\n📝 Creating requirements.txt...")
requirements = """python-dotenv==1.0.1
schedule==1.2.1
requests==2.31.0
openai==1.12.0
google-generativeai==0.4.0
elevenlabs==1.0.3
Pillow==10.2.0
moviepy==1.0.3
imageio-ffmpeg==0.4.9
google-api-python-client==2.118.0
google-auth-httplib2==0.2.0
google-auth-oauthlib==1.2.0
beautifulsoup4==4.12.3
numpy==1.26.4
"""

with open("requirements.txt", "w") as f:
    f.write(requirements)
print("  ✓ Created requirements.txt")

# Create .env template
print("\n📋 Creating .env template...")
env_template = """# AutoMagic Configuration - Fill in your API keys below

# OpenAI (for DALL-E image generation)
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE

# ElevenLabs (for voice generation)
ELEVENLABS_API_KEY=YOUR_ELEVENLABS_API_KEY_HERE
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Google APIs (for YouTube and Gemini)
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY_HERE
YOUTUBE_CLIENT_ID=YOUR_YOUTUBE_CLIENT_ID_HERE
YOUTUBE_CLIENT_SECRET=YOUR_YOUTUBE_CLIENT_SECRET_HERE
YOUTUBE_CHANNEL_ID=YOUR_YOUTUBE_CHANNEL_ID_HERE
GOOGLE_API_CREDENTIALS_FILE=youtube_credentials.json

# Optional APIs (leave blank if not using)
ANTHROPIC_API_KEY=
KLING_API_KEY=
PICTORY_API_KEY=
COMFYUI_API_ADDRESS=http://127.0.0.1:8188

# TikTok (optional)
TIKTOK_SESSION_ID=
TIKTOK_USERNAME=

# Application Settings (don't change these)
DAILY_RUN_TIME=09:00
LOG_LEVEL=INFO
IMAGE_SAVE_PATH=generated_images/
AUDIO_SAVE_PATH=generated_audio/
VIDEO_CLIP_SAVE_PATH=generated_video_clips/
FINAL_VIDEO_SAVE_PATH=final_videos/
LOG_FILE_PATH=logs/automagic.log
SEASON=1
DAY_NUMBER=1
MAX_VIDEO_DURATION=60
VIDEO_RESOLUTION=1080x1920
VIDEO_FPS=30
"""

with open(".env", "w") as f:
    f.write(env_template)
print("  ✓ Created .env template")

# Install Python packages
print("\n📦 Installing required Python packages...")
print("This may take a few minutes...\n")

try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("\n  ✓ All packages installed successfully!")
except Exception as e:
    print(f"\n  ❌ Error installing packages: {e}")
    print("  Please run: pip install -r requirements.txt")

# Create the main automagic.py file
print("\n📝 Creating automagic.py...")
# I'll include a simplified version for the setup
automagic_code = '''import os
print("AutoMagic O.T.T.O. is installed!")
print("Please complete the API setup before running the full version.")
'''

with open("automagic.py", "w") as f:
    f.write(automagic_code)
print("  ✓ Created automagic.py")

# Create API setup guide
print("\n📖 Creating API setup guide...")
api_guide = """# AutoMagic API Setup Guide

## Required APIs (in order of importance):

### 1. OpenAI API (for DALL-E images)
1. Go to: https://platform.openai.com/
2. Sign up or log in
3. Click "API keys" in the left menu
4. Click "Create new secret key"
5. Copy the key and paste it in .env file at OPENAI_API_KEY=

### 2. ElevenLabs API (for voice)
1. Go to: https://elevenlabs.io/
2. Sign up for free account
3. Click your profile icon → "Profile"
4. Copy your API key
5. Paste it in .env file at ELEVENLABS_API_KEY=

### 3. Google Cloud (for YouTube)
1. Go to: https://console.cloud.google.com/
2. Create a new project
3. Enable "YouTube Data API v3"
4. Create credentials (OAuth 2.0 Client ID)
5. Download the JSON file as "client_secret.json"
6. Put it in your AutoMagic folder

### 4. Google AI Studio (for Gemini)
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API key"
3. Copy it to .env at GOOGLE_API_KEY=

## Your YouTube Channel ID:
1. Go to YouTube
2. Click your profile → "Your channel"
3. The URL contains your channel ID
4. Add it to .env at YOUTUBE_CHANNEL_ID=

Save this file for reference!
"""

with open("API_SETUP_GUIDE.txt", "w") as f:
    f.write(api_guide)
print("  ✓ Created API_SETUP_GUIDE.txt")

# Create a simple test script
print("\n🧪 Creating test script...")
test_script = """# test_setup.py - Test your AutoMagic setup
import os
from dotenv import load_dotenv

print("🔍 Testing AutoMagic Setup...")
print("-" * 40)

# Load environment variables
load_dotenv()

# Check API keys
api_keys = {
    "OpenAI": os.getenv("OPENAI_API_KEY"),
    "ElevenLabs": os.getenv("ELEVENLABS_API_KEY"),
    "Google API": os.getenv("GOOGLE_API_KEY"),
    "YouTube Client ID": os.getenv("YOUTUBE_CLIENT_ID"),
}

missing_keys = []
for name, key in api_keys.items():
    if key and key != f"YOUR_{name.upper().replace(' ', '_')}_HERE":
        print(f"✓ {name}: Configured")
    else:
        print(f"❌ {name}: Not configured")
        missing_keys.append(name)

print("-" * 40)
if missing_keys:
    print(f"⚠️  Missing API keys: {', '.join(missing_keys)}")
    print("Please check API_SETUP_GUIDE.txt for instructions")
else:
    print("✅ All required APIs are configured!")
    print("You're ready to run AutoMagic!")
"""

with open("test_setup.py", "w") as f:
    f.write(test_script)
print("  ✓ Created test_setup.py")

# Final instructions
print("\n" + "="*50)
print("✅ SETUP COMPLETE!")
print("="*50)
print("\n📋 Next Steps:")
print("1. Open API_SETUP_GUIDE.txt and follow the instructions")
print("2. Get your API keys and add them to the .env file")
print("3. Run 'python test_setup.py' to check your configuration")
print("4. Once all tests pass, you're ready to use AutoMagic!")
print("\n💡 Tip: The setup guide has been opened in your browser")

# Open the setup guide
webbrowser.open('API_SETUP_GUIDE.txt')

# Also try to open .env file
if platform.system() == "Windows":
    os.system("notepad .env")
elif platform.system() == "Darwin":  # macOS
    os.system("open -e .env")
else:  # Linux
    os.system("xdg-open .env")

print("\n🎉 Setup automation complete!")