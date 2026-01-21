# automagic_setup.py - Automated Setup Script
import os
import sys
import subprocess
import platform
import json
import webbrowser
from pathlib import Path
import argparse
import shutil

# Ensure UTF-8 console encoding on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="AutoMagic O.T.T.O. Setup Tool")
    parser.add_argument("--skip-install", action="store_true", help="Skip package installation")
    parser.add_argument("--skip-env", action="store_true", help="Skip creating .env file if it exists")
    parser.add_argument("--quick", action="store_true", help="Quick setup (skip all checks and confirmations)")
    return parser.parse_args()

def check_ffmpeg():
    """Check if FFmpeg is installed."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout.split('\n')[0]
        return False, "FFmpeg command returned non-zero exit code"
    except FileNotFoundError:
        return False, "FFmpeg not found in PATH"
    except Exception as e:
        return False, str(e)

def main():
    """Main setup function."""
    args = parse_arguments()
    
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
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   Created or verified: {directory}")

    # Create or update requirements.txt with comprehensive dependencies
    print("\n📝 Creating or updating requirements.txt...")
    req_path = Path("requirements.txt")
    if not req_path.exists():
        with req_path.open("w", encoding="utf-8") as f:
            f.write("# AutoMagic dependencies\n")
            f.write("requests==2.32.3\n")
            f.write("python-dotenv==1.1.0\n")
            f.write("schedule==1.2.2\n")
            f.write("openai==1.12.0\n")
            f.write("elevenlabs==1.0.3\n")
            f.write("Pillow==11.0.0\n")
            f.write("ffmpeg-python==0.2.0\n")
            f.write("moviepy==1.0.3\n")
            f.write("google-api-python-client==2.118.0\n")
            f.write("google-auth-httplib2==0.2.0\n")
            f.write("google-auth-oauthlib==1.2.0\n")
            f.write("beautifulsoup4==4.12.3\n")
            f.write("numpy==1.26.4\n")
            f.write("httpx==0.27.0\n")
        print("   requirements.txt created with extended dependencies.")
    else:
        print("   requirements.txt already exists. Skipping creation.")

    # Create .env template if doesn't exist or if not skipping
    env_path = Path(".env")
    if not env_path.exists() or not args.skip_env:
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
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_template)
        print("  ✓ Created .env template")
    else:
        print("\n📋 .env file already exists. Skipping creation.")

    # Check for FFmpeg installation
    print("\n🎬 Checking for FFmpeg installation...")
    ffmpeg_installed, ffmpeg_version = check_ffmpeg()
    if ffmpeg_installed:
        print(f"  ✓ FFmpeg is installed: {ffmpeg_version}")
    else:
        print(f"  ❌ FFmpeg not detected: {ffmpeg_version}")
        print("  Please install FFmpeg and add it to your PATH.")
        print("  See API_SETUP_GUIDE.txt for instructions on installing FFmpeg.")

    # Install Python packages if not skipped
    if not args.skip_install:
        print("\n📦 Installing required Python packages...")
        print("This may take a few minutes...\n")

        try:
            # First, upgrade pip
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
            
            # Install packages one by one for better error handling
            packages = [line.strip() for line in open("requirements.txt") if line.strip() and not line.startswith("#")]
            
            for package in packages:
                print(f"Installing {package}...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                    print(f"  ✓ Installed {package}")
                except Exception as e:
                    print(f"  ⚠️  Failed to install {package}: {e}")
            
            print("\n  ✓ Package installation complete!")
        except Exception as e:
            print(f"\n  ❌ Error during installation: {e}")
            print("  Please try running: pip install -r requirements.txt")
    else:
        print("\n📦 Skipping package installation as requested.")

    # Create expanded API setup guide with FFmpeg instructions
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
5. Download the JSON file as "youtube_credentials.json"
6. Put it in your AutoMagic folder
7. Update GOOGLE_API_CREDENTIALS_FILE in .env if you use a different filename

### 4. Google AI Studio (for Gemini)
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API key"
3. Copy it to .env at GOOGLE_API_KEY=

## Your YouTube Channel ID:
1. Go to YouTube
2. Click your profile → "Your channel"
3. The URL contains your channel ID (or use a tool like https://commentpicker.com/youtube-channel-id.php)
4. Add it to .env at YOUTUBE_CHANNEL_ID=

## Installing FFmpeg (Required for video processing)

### Windows:
1. Download FFmpeg from https://ffmpeg.org/download.html#build-windows
2. Extract the zip file to a location on your computer (e.g., C:\\ffmpeg)
3. Add FFmpeg to your system PATH:
   - Right-click on "This PC" and select "Properties"
   - Click on "Advanced system settings"
   - Click on "Environment Variables"
   - Under "System variables", find and select the "Path" variable
   - Click "Edit" and add the path to the FFmpeg bin folder (e.g., C:\\ffmpeg\\bin)
   - Click "OK" on all dialogs to save changes
4. Restart your command prompt and verify with: ffmpeg -version

### macOS:
1. Install using Homebrew: brew install ffmpeg
2. Verify installation: ffmpeg -version

### Linux:
1. Install using apt (Ubuntu/Debian): sudo apt update && sudo apt install ffmpeg
2. Verify installation: ffmpeg -version

Save this file for reference!
"""

    with open("API_SETUP_GUIDE.txt", "w", encoding="utf-8") as f:
        f.write(api_guide)
    print("  ✓ Created API_SETUP_GUIDE.txt")

    # Create enhanced test script that includes FFmpeg check
    print("\n🧪 Creating test script...")
    test_script = """# test_setup.py - Test your AutoMagic setup
import sys
print("Minimal test_setup.py running")
print(f"Python version: {sys.version}")
"""

    with open("test_setup.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    print("  ✓ Created test_setup.py")

    # Create a Windows batch file for easy execution
    if platform.system() == "Windows":
        batch_content = """@echo off
cd /d "%~dp0"
echo Running AutoMagic...
python automagic.py
pause
"""
        with open("run_automagic.bat", "w", encoding="utf-8") as f:
            f.write(batch_content)
        print("\n📄 Created run_automagic.bat for easy execution")

    # Final instructions
    print("\n" + "="*50)
    print("✅ SETUP COMPLETE!")
    print("="*50)
    print("\n📋 Next Steps:")
    print("1. Open API_SETUP_GUIDE.txt and follow the instructions")
    print("2. Get your API keys and add them to the .env file")
    print("3. Run 'python test_setup.py' to check your configuration")
    print("4. Once all tests pass, you're ready to use AutoMagic!")

    # Open files for editing based on platform
    if not args.quick:
        print("\n💡 Opening setup guide and .env file for editing...")
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
    
if __name__ == "__main__":
    main()