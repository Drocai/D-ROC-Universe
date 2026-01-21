#!/usr/bin/env python3
"""
AutoMagic O.T.T.O. System Verification Tool

This script performs comprehensive verification of the AutoMagic system,
including file integrity, API configurations, and environment setup.
"""
import os
import sys
import json
import logging
import subprocess
import platform
from pathlib import Path
import hashlib
import importlib
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("AutoMagic-Verifier")

# Define critical files
CRITICAL_FILES = [
    "automagic.py",
    "automation_script.py",
    "automagic_setup.py",
    "requirements.txt",
    ".env"
]

# Define important directories
IMPORTANT_DIRS = [
    "generated_images",
    "generated_audio",
    "generated_video_clips",
    "final_videos",
    "logs"
]

def verify_files() -> Tuple[bool, List[str]]:
    """Verify critical files exist."""
    missing = []
    for filename in CRITICAL_FILES:
        if not Path(filename).exists():
            missing.append(filename)
    return len(missing) == 0, missing

def verify_directories() -> Tuple[bool, List[str]]:
    """Verify important directories exist."""
    missing = []
    for dirname in IMPORTANT_DIRS:
        if not Path(dirname).exists() or not Path(dirname).is_dir():
            missing.append(dirname)
    return len(missing) == 0, missing

def verify_dependencies() -> Tuple[bool, List[str]]:
    """Verify Python dependencies."""
    missing = []
    try:
        with open("requirements.txt", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    pkg = line.split("==")[0].strip()
                    try:
                        importlib.import_module(pkg.replace("-", "_"))
                    except ImportError:
                        missing.append(pkg)
    except Exception as e:
        logger.error(f"Error checking dependencies: {e}")
        missing.append("requirements.txt (error reading file)")
    
    return len(missing) == 0, missing

def verify_ffmpeg() -> Tuple[bool, str]:
    """Verify FFmpeg installation."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout.split('\n')[0]
        return False, "FFmpeg command returned non-zero exit code"
    except FileNotFoundError:
        return False, "FFmpeg not found in PATH"
    except Exception as e:
        return False, str(e)

def verify_env_file() -> Tuple[bool, List[str]]:
    """Verify .env file has needed variables."""
    required_vars = [
        "OPENAI_API_KEY",
        "ELEVENLABS_API_KEY",
        "GOOGLE_API_KEY",
        "IMAGE_SAVE_PATH",
        "AUDIO_SAVE_PATH",
        "VIDEO_CLIP_SAVE_PATH",
        "FINAL_VIDEO_SAVE_PATH"
    ]
    
    missing = []
    try:
        from dotenv import dotenv_values
        env_values = dotenv_values(".env")
        
        for var in required_vars:
            if var not in env_values or not env_values[var] or env_values[var].startswith("YOUR_"):
                missing.append(var)
    
    except Exception as e:
        logger.error(f"Error reading .env file: {e}")
        return False, [".env file could not be read"]
    
    return len(missing) == 0, missing

def verify_api_keys() -> Dict[str, bool]:
    """Check if API keys are configured and valid."""
    from dotenv import load_dotenv
    load_dotenv()
    
    results = {}
    
    # Check OpenAI
    try:
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")
        models = openai.models.list()
        results["OpenAI"] = True
    except Exception:
        results["OpenAI"] = False
    
    # Check ElevenLabs
    try:
        import requests
        elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
        elevenlabs_url = "https://api.elevenlabs.io/v1/voices"
        response = requests.get(elevenlabs_url, headers={"xi-api-key": elevenlabs_key})
        results["ElevenLabs"] = response.status_code == 200
    except Exception:
        results["ElevenLabs"] = False
    
    # Check Google API
    try:
        import requests
        google_key = os.getenv("GOOGLE_API_KEY")
        google_url = f"https://www.googleapis.com/discovery/v1/apis?key={google_key}"
        response = requests.get(google_url)
        results["Google"] = response.status_code == 200
    except Exception:
        results["Google"] = False
    
    return results

def main():
    """Main verification function."""
    logger.info("🔍 Running AutoMagic System Verification")
    print("\n" + "="*60)
    print(" 🚀 AutoMagic O.T.T.O. System Verification")
    print("="*60)
    
    # Check Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"\n🐍 Python Version: {py_version}")
    if sys.version_info < (3, 8):
        print("⚠️  WARNING: Python 3.8+ recommended")
    
    # Check critical files
    files_ok, missing_files = verify_files()
    print(f"\n📄 Critical Files: {'✅ All present' if files_ok else '❌ Some missing'}")
    if not files_ok:
        print(f"   Missing files: {', '.join(missing_files)}")
    
    # Check directories
    dirs_ok, missing_dirs = verify_directories()
    print(f"\n📁 Important Directories: {'✅ All present' if dirs_ok else '❌ Some missing'}")
    if not dirs_ok:
        for dirname in missing_dirs:
            print(f"   Creating missing directory: {dirname}")
            Path(dirname).mkdir(exist_ok=True)
        print("   ✅ Created missing directories")
    
    # Check dependencies
    deps_ok, missing_deps = verify_dependencies()
    print(f"\n📦 Python Dependencies: {'✅ All installed' if deps_ok else '❌ Some missing'}")
    if not deps_ok:
        print(f"   Missing packages: {', '.join(missing_deps)}")
        install = input("   Would you like to install missing packages now? (y/n): ")
        if install.lower() == 'y':
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
                print("   ✅ Dependencies installed")
            except Exception as e:
                print(f"   ❌ Error installing dependencies: {e}")
    
    # Check FFmpeg
    ffmpeg_ok, ffmpeg_msg = verify_ffmpeg()
    print(f"\n🎬 FFmpeg: {'✅ Installed' if ffmpeg_ok else '❌ Not found'}")
    if ffmpeg_ok:
        print(f"   {ffmpeg_msg}")
    else:
        print(f"   Error: {ffmpeg_msg}")
        print("   Please install FFmpeg and add it to your PATH")
        print("   See API_SETUP_GUIDE.txt for instructions")
    
    # Check .env file
    env_ok, missing_vars = verify_env_file()
    print(f"\n⚙️  Environment Configuration: {'✅ Complete' if env_ok else '❌ Incomplete'}")
    if not env_ok:
        print(f"   Missing or invalid variables: {', '.join(missing_vars)}")
        print("   Please update your .env file with these values")
    
    # Verify API keys if requested
    test_apis = input("\nWould you like to test API connections? (y/n): ")
    if test_apis.lower() == 'y':
        print("\n🔑 Testing API Connections...")
        
        api_results = verify_api_keys()
        for api, status in api_results.items():
            print(f"   {'✅' if status else '❌'} {api} API: {'Connected' if status else 'Failed'}")
    
    # Summary
    success = files_ok and dirs_ok and (deps_ok or install.lower() == 'y') and ffmpeg_ok and env_ok
    
    print("\n" + "="*60)
    if success:
        print("🎉 Verification Complete: System is ready to run!")
        print("   Run 'python automagic.py' to start or 'python run_automagic.py' for monitored execution")
    else:
        print("⚠️  Verification Complete: Some issues need attention")
        print("   Please fix the issues above before running AutoMagic")
    print("="*60 + "\n")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
