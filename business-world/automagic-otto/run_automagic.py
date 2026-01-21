#!/usr/bin/env python3
"""
AutoMagic O.T.T.O. Launcher Script
This script provides a robust entry point to launch the AutoMagic system
with proper error handling and environment validation.
"""
import os
import sys
import subprocess
import platform
import time
import shutil
from pathlib import Path
import logging

# Set up basic logging for the launcher
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("AutoMagic-Launcher")

def check_ffmpeg():
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

def check_python_version():
    """Check if Python version is compatible."""
    min_version = (3, 8)
    current = (sys.version_info.major, sys.version_info.minor)
    if current < min_version:
        return False, f"Python {current[0]}.{current[1]} detected. AutoMagic requires Python {min_version[0]}.{min_version[1]}+"
    return True, f"Python {current[0]}.{current[1]}.{sys.version_info.micro}"

def check_dependencies():
    """Check critical dependencies."""
    missing = []
    dependencies = [
        "dotenv", "openai", "schedule", "PIL", "ffmpeg", "requests", 
        "google.oauth2", "google.auth", "elevenlabs"
    ]
    
    for dep in dependencies:
        try:
            if dep == "PIL":
                from PIL import Image
            elif dep == "dotenv":
                from dotenv import load_dotenv
            elif "." in dep:
                import importlib
                importlib.import_module(dep)
            else:
                __import__(dep)
        except ImportError:
            missing.append(dep)
    
    if missing:
        return False, f"Missing dependencies: {', '.join(missing)}"
    return True, "All critical dependencies found"

def backup_env_file():
    """Create a backup of the .env file if it exists."""
    env_path = Path(".env")
    if env_path.exists():
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        backup_path = f".env.backup-{timestamp}"
        shutil.copy2(env_path, backup_path)
        logger.info(f"Created backup of .env file: {backup_path}")
        return True
    return False

def main():
    """Main launcher function."""
    logger.info("🚀 Starting AutoMagic O.T.T.O. Launch Sequence")
    
    # Check Python version
    py_ok, py_msg = check_python_version()
    if not py_ok:
        logger.error(f"❌ {py_msg}")
        logger.error("Please upgrade your Python installation and try again.")
        return 1
    logger.info(f"✅ {py_msg}")
    
    # Check FFmpeg
    ffmpeg_ok, ffmpeg_msg = check_ffmpeg()
    if not ffmpeg_ok:
        logger.error(f"❌ FFmpeg check failed: {ffmpeg_msg}")
        logger.error("Please install FFmpeg and add it to your PATH. See API_SETUP_GUIDE.txt")
        return 1
    logger.info(f"✅ FFmpeg detected: {ffmpeg_msg}")
    
    # Check critical dependencies
    deps_ok, deps_msg = check_dependencies()
    if not deps_ok:
        logger.error(f"❌ Dependency check failed: {deps_msg}")
        logger.error("Run: pip install -r requirements.txt")
        return 1
    logger.info(f"✅ {deps_msg}")
    
    # Create backup of .env file
    backup_made = backup_env_file()
    if backup_made:
        logger.info("✅ Environment file backup created")
    
    # Check if the .env file exists
    if not Path(".env").exists():
        logger.error("❌ No .env file found! Please run automagic_setup.py first.")
        return 1
    
    # Launch the main application
    logger.info("🚀 Launching AutoMagic O.T.T.O...")
    try:
        # Start the main program through subprocess to isolate potential crashes
        subprocess.run([sys.executable, "automagic.py"], check=True)
        logger.info("✅ AutoMagic completed successfully!")
        return 0
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ AutoMagic process exited with error code: {e.returncode}")
        return e.returncode
    except KeyboardInterrupt:
        logger.info("⏹️ AutoMagic process was interrupted by user.")
        return 0
    except Exception as e:
        logger.error(f"❌ Failed to launch AutoMagic: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
