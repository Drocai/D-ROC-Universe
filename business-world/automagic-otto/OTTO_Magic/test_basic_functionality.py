#!/usr/bin/env python3
"""
Simple test script to verify OTTO_Magic basic functionality
"""
import os
import sys
from pathlib import Path

# Add the core modules to path
sys.path.append(str(Path(__file__).parent))

def test_visual_generation():
    """Test visual generation with a mock brief"""
    print("🧪 Testing visual generation...")
    
    from core.generation.visual_generator import generate_visuals
    
    # Create a mock brief
    mock_brief = {
        "theme": "AI Technology",
        "visual_prompt": "A futuristic AI robot working with data visualizations",
        "personality": "innovative",
        "affirmation_text": "Technology enhances human creativity"
    }
    
    try:
        visual_path = generate_visuals(mock_brief)
        if visual_path and visual_path.exists():
            print(f"✅ Visual generation successful: {visual_path}")
            return True
        else:
            print("❌ Visual generation failed: No output file")
            return False
    except Exception as e:
        print(f"❌ Visual generation failed: {e}")
        return False

def test_audio_generation():
    """Test audio generation with a mock brief"""
    print("🧪 Testing audio generation...")
    
    from core.generation.audio_generator import generate_voiceover
    
    # Create a mock brief
    mock_brief = {
        "theme": "AI Technology",
        "affirmation_text": "Technology enhances human creativity and opens new possibilities.",
        "personality": "innovative"
    }
    
    try:
        audio_path = generate_voiceover(mock_brief)
        if audio_path and Path(audio_path).exists():
            print(f"✅ Audio generation successful: {audio_path}")
            return True
        else:
            print("❌ Audio generation failed: No output file")
            return False
    except Exception as e:
        print(f"❌ Audio generation failed: {e}")
        return False

def test_video_assembly():
    """Test video assembly with real generated assets"""
    print("🧪 Testing video assembly...")
    
    from core.pipelines.video_assembler import assemble_video
    from core.generation.visual_generator import generate_visuals
    from core.generation.audio_generator import generate_voiceover
    
    # Generate real assets first
    mock_brief = {
        "theme": "AI Technology",
        "visual_prompt": "A simple AI concept illustration", 
        "affirmation_text": "Technology enhances human creativity.",
        "personality": "innovative"
    }
    
    try:
        # Generate visual asset
        visual_path = generate_visuals(mock_brief)
        if not visual_path:
            print("❌ Failed to generate visual for video assembly test")
            return False
            
        # Generate audio asset  
        audio_path = generate_voiceover(mock_brief)
        if not audio_path:
            print("❌ Failed to generate audio for video assembly test")
            return False
        
        # Now test video assembly with real files
        video_path = assemble_video(visual_path, audio_path, None, mock_brief)
        if video_path and Path(video_path).exists():
            print(f"✅ Video assembly successful: {video_path}")
            return True
        else:
            print("❌ Video assembly failed: No output file")
            return False
    except Exception as e:
        print(f"❌ Video assembly failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting OTTO_Magic basic functionality tests...\n")
    
    # Create necessary directories
    Path("generated_assets/visuals").mkdir(parents=True, exist_ok=True)
    Path("generated_assets/audio").mkdir(parents=True, exist_ok=True)
    Path("final_videos").mkdir(parents=True, exist_ok=True)
    
    tests = [
        ("Visual Generation", test_visual_generation),
        ("Audio Generation", test_audio_generation),
        ("Video Assembly", test_video_assembly)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running {test_name} Test")
        print('='*50)
        result = test_func()
        results.append((test_name, result))
        print()
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! OTTO_Magic basic functionality is working.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
