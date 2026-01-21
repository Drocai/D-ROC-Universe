#!/usr/bin/env python3
"""
Provider Setup and Testing Script
Helps configure and test the new multi-provider system
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s"
)
logger = logging.getLogger("Setup")


def install_dependencies():
    """Install required dependencies"""
    print("\n" + "="*60)
    print("📦 INSTALLING DEPENDENCIES")
    print("="*60)

    requirements_file = "requirements_multi_provider.txt"

    if not os.path.exists(requirements_file):
        logger.error(f"Requirements file not found: {requirements_file}")
        return False

    try:
        logger.info("Installing packages...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", requirements_file],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            logger.info("✅ All dependencies installed successfully!")
            return True
        else:
            logger.error(f"Installation failed: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"Error installing dependencies: {e}")
        return False


def check_env_file():
    """Check if .env file exists"""
    print("\n" + "="*60)
    print("🔧 CHECKING CONFIGURATION")
    print("="*60)

    if os.path.exists(".env"):
        logger.info("✅ .env file found")
        return True
    else:
        logger.warning("⚠️  .env file not found")
        if os.path.exists(".env.template"):
            logger.info("📋 Template file available at: .env.template")
            logger.info("   Copy it to .env and add your API keys")
        return False


def test_providers():
    """Test all configured providers"""
    print("\n" + "="*60)
    print("🧪 TESTING PROVIDERS")
    print("="*60)

    try:
        # Import after dependencies are installed
        from api_providers import ProviderManager

        manager = ProviderManager()
        status = manager.get_status()

        # Display results
        print("\n📝 Script Generation Providers:")
        script_available = False
        for provider in status["script_providers"]:
            if provider["connected"]:
                print(f"  ✅ {provider['name']} - Ready (Priority: {provider['priority']})")
                script_available = True
            elif provider["available"]:
                print(f"  ⚠️  {provider['name']} - Configured but connection failed")
            else:
                print(f"  ❌ {provider['name']} - Not configured")

        print("\n🎨 Image Generation Providers:")
        image_available = False
        for provider in status["image_providers"]:
            if provider["connected"]:
                print(f"  ✅ {provider['name']} - Ready (Priority: {provider['priority']})")
                image_available = True
            elif provider["available"]:
                print(f"  ⚠️  {provider['name']} - Configured but connection failed")
            else:
                print(f"  ❌ {provider['name']} - Not configured")

        print("\n🎤 Voice Generation Providers:")
        voice_available = False
        for provider in status["voice_providers"]:
            if provider["connected"]:
                print(f"  ✅ {provider['name']} - Ready (Priority: {provider['priority']})")
                voice_available = True
            elif provider["available"]:
                print(f"  ⚠️  {provider['name']} - Configured but connection failed")
            else:
                print(f"  ❌ {provider['name']} - Not configured")

        # Summary
        print("\n" + "="*60)
        print("📊 SUMMARY")
        print("="*60)

        all_ready = script_available and image_available and voice_available

        if all_ready:
            print("✅ System ready! All categories have at least one working provider.")
            return True
        else:
            print("⚠️  System not fully configured:")
            if not script_available:
                print("   - Need at least one script generation provider")
                print("     Recommended: GROQ_API_KEY (free)")
            if not image_available:
                print("   - Need at least one image generation provider")
                print("     Recommended: REPLICATE_API_KEY (very cheap)")
            if not voice_available:
                print("   - Need at least one voice generation provider")
                print("     Recommended: Keep ElevenLabs or add GOOGLE_TTS_API_KEY")
            return False

    except ImportError as e:
        logger.error(f"Could not import providers module: {e}")
        logger.info("Make sure dependencies are installed")
        return False
    except Exception as e:
        logger.error(f"Error testing providers: {e}")
        return False


def show_quick_start_guide():
    """Display quick start instructions"""
    print("\n" + "="*60)
    print("🚀 QUICK START GUIDE")
    print("="*60)
    print("""
To get started with FREE/cheap providers:

1. Get a Groq API key (FREE):
   • Visit: https://console.groq.com/
   • Sign up and get your API key
   • Add to .env: GROQ_API_KEY=your_key_here

2. Get a Replicate API key (Very cheap - ~$0.003/image):
   • Visit: https://replicate.com/account/api-tokens
   • Sign up and get your API token
   • Add to .env: REPLICATE_API_KEY=your_key_here

3. For voice, either:
   a) Keep your existing ElevenLabs key, OR
   b) Get Google TTS API key (FREE tier):
      • Visit: https://console.cloud.google.com/
      • Enable Text-to-Speech API
      • Create API key
      • Add to .env: GOOGLE_TTS_API_KEY=your_key_here

4. Run the test again:
   python setup_providers.py

5. Once all providers are ready, run AutoMagic:
   python automagic.py --now
    """)
    print("="*60)


def main():
    """Main setup flow"""
    print("\n" + "="*70)
    print("   🎬 AUTOMAGIC - MULTI-PROVIDER SETUP")
    print("="*70)

    # Step 1: Install dependencies
    if not install_dependencies():
        logger.error("Setup failed at dependency installation")
        return

    # Step 2: Check .env
    env_exists = check_env_file()

    # Step 3: Test providers
    if env_exists:
        providers_ready = test_providers()

        if not providers_ready:
            show_quick_start_guide()
    else:
        logger.info("\n⚠️  Cannot test providers without .env file")
        show_quick_start_guide()

    print("\n" + "="*70)
    print("Setup script completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
