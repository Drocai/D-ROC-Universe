#!/usr/bin/env python3
"""
Simple test script for OTTO_Magic to verify core functionality without external APIs.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to path so imports work
sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()

def test_basic_functionality():
    """Test basic workflow components without external API calls."""
    print("🔍 Testing OTTO_Magic basic functionality...")
    
    # Test 1: Create a simple brief manually
    print("\n1. Creating test brief...")
    test_brief = {
        "theme": "The Future of AI",
        "personality": "The Philosopher", 
        "mood": "contemplative",
        "affirmation_text": "Artificial intelligence represents humanity's greatest leap toward understanding consciousness itself.",
        "visual_prompt": "A serene landscape with floating geometric patterns representing AI consciousness",
        "voice_profile": "pNInz6obpgDQGcFmaJgB"
    }
    print(f"✅ Brief created: {test_brief['theme']}")
    
    # Test 2: Test visual generation (mock)
    print("\n2. Testing visual generation...")
    try:
        from core.generation.visual_generator import _create_placeholder_image
        visual_path = _create_placeholder_image("Test AI Image", Path("generated_assets/visuals"))
        if visual_path and visual_path.exists():
            print(f"✅ Visual created: {visual_path}")
        else:
            print("❌ Visual generation failed")
    except Exception as e:
        print(f"❌ Visual generation error: {e}")
    
    # Test 3: Test video assembly with FFmpeg
    print("\n3. Testing video assembly...")
    try:
        from core.pipelines.video_assembler import assemble_video
        if visual_path and visual_path.exists():
            video_path = assemble_video(visual_path, None, None, test_brief)
            if video_path and video_path.exists():
                print(f"✅ Video assembled: {video_path}")
            else:
                print("❌ Video assembly failed")
        else:
            print("❌ Skipping video assembly - no visual")
    except Exception as e:
        print(f"❌ Video assembly error: {e}")
    
    # Test 4: Check FFmpeg availability
    print("\n4. Testing FFmpeg availability...")
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg is available")
        else:
            print("❌ FFmpeg not found")
    except Exception as e:
        print(f"❌ FFmpeg test error: {e}")
    
    print("\n🎯 Basic functionality test completed!")

if __name__ == "__main__":
    test_basic_functionality()
