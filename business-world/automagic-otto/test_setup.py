print("Starting test_setup.py")
# test_setup.py - Test your AutoMagic setup
import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

def check_ffmpeg():
    """Check if FFmpeg is installed and accessible."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout.split('\n')[0]
        return False, "FFmpeg command returned non-zero exit code"
    except FileNotFoundError:
        return False, "FFmpeg not found in PATH"
    except Exception as e:
        return False, str(e)

print("🔍 Testing AutoMagic Setup...")
print("-" * 50)

# Check Python version
python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
print(f"🐍 Python version: {python_version}")

# Load environment variables
try:
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv()
        print("✓ .env file loaded successfully")
    else:
        print("❌ .env file not found")
except Exception as e:
    print(f"❌ Error loading .env file: {e}")

# Check API keys
api_keys = {
    "OpenAI": os.getenv("OPENAI_API_KEY"),
    "ElevenLabs": os.getenv("ELEVENLABS_API_KEY"),
    "Google API": os.getenv("GOOGLE_API_KEY"),
    "YouTube Client ID": os.getenv("YOUTUBE_CLIENT_ID"),
    "YouTube Client Secret": os.getenv("YOUTUBE_CLIENT_SECRET"),
    "YouTube Channel ID": os.getenv("YOUTUBE_CHANNEL_ID"),
}

missing_keys = []
print("\nAPI Keys Status:")
print("-" * 30)
for name, key in api_keys.items():
    if key and not key.startswith("YOUR_") and key != "":
        print(f"✓ {name}: Configured")
    else:
        print(f"❌ {name}: Not configured")
        missing_keys.append(name)

# Check directories
print("\nDirectories Status:")
print("-" * 30)
directories = [
    "generated_images",
    "generated_audio", 
    "generated_video_clips",
    "final_videos",
    "logs"
]

for directory in directories:
    if os.path.isdir(directory):
        print(f"✓ {directory}/: Exists")
    else:
        print(f"❌ {directory}/: Missing")

# Check FFmpeg
print("\nFFmpeg Status:")
print("-" * 30)
ffmpeg_installed, ffmpeg_info = check_ffmpeg()
if ffmpeg_installed:
    print(f"✓ FFmpeg is installed: {ffmpeg_info}")
else:
    print(f"❌ FFmpeg not detected: {ffmpeg_info}")
    print("  Please install FFmpeg and add it to your PATH")
    print("  See API_SETUP_GUIDE.txt for instructions")

# Check core Python dependencies
print("\nPython Dependencies:")
print("-" * 30)
dependencies = [
    "openai", "elevenlabs", "ffmpeg", "requests", "PIL", 
    "google.oauth2", "schedule"
]
missing_deps = []

for dep in dependencies:
    try:
        if dep == "PIL":
            # PIL needs special import check
            from PIL import Image
            print(f"✓ Pillow (PIL): Installed")
        elif dep == "google.oauth2":
            # Handle module with dots
            import importlib
            importlib.import_module(dep)
            print(f"✓ {dep}: Installed")
        else:
            # Standard imports
            __import__(dep)
            print(f"✓ {dep}: Installed")
    except ImportError:
        print(f"❌ {dep}: Not installed")
        missing_deps.append(dep)

# Overall status
print("\nOverall Status:")
print("-" * 30)
if missing_keys:
    print(f"⚠️  Missing {len(missing_keys)} API keys: {', '.join(missing_keys)}")
    print("  Please check API_SETUP_GUIDE.txt for instructions")
else:
    print("✅ All required API keys are configured!")

if missing_deps:
    print(f"⚠️  Missing {len(missing_deps)} Python dependencies: {', '.join(missing_deps)}")
    print("  Please run: pip install -r requirements.txt")
else:
    print("✅ All required Python dependencies are installed!")

if not ffmpeg_installed:
    print("⚠️  FFmpeg is not installed or not in PATH")
    print("  Please install FFmpeg and add it to your PATH")
else:
    print("✅ FFmpeg is properly installed!")

# Final summary
print("\n" + "="*50)
if not missing_keys and not missing_deps and ffmpeg_installed:
    print("🎉 All checks passed! You're ready to run AutoMagic!")
    print("   Run 'python automagic.py' to get started.")
else:
    print("⚠️  Some checks failed. Please fix the issues above before running AutoMagic.")
