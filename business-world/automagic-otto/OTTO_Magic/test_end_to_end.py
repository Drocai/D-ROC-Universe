#!/usr/bin/env python3
"""
End-to-end test for OTTO_Magic workflow
"""
import os
import sys
from pathlib import Path

# Add the core modules to path
sys.path.append(str(Path(__file__).parent))

def test_full_workflow():
    """Test the complete video creation workflow with mock data"""
    print("🎬 Testing full OTTO_Magic workflow...")
    
    # Import after setting path
    from core.workflows.main_workflow import video_creation_workflow
    
    try:
        # Test with custom brief to bypass API dependencies
        topic = "Future of AI"
        custom_brief = "Create an inspiring video about how AI will transform creativity in the next decade"
        
        print(f"Topic: {topic}")
        print(f"Custom Brief: {custom_brief}")
        
        # This should create a complete video using placeholders where APIs fail
        video_creation_workflow(topic, custom_brief)
        
        # Check if video was created
        video_dir = Path("final_videos")
        if video_dir.exists():
            videos = list(video_dir.glob("*.mp4"))
            if videos:
                latest_video = max(videos, key=lambda x: x.stat().st_mtime)
                print(f"✅ Full workflow successful! Video created: {latest_video}")
                return True
        
        print("❌ Full workflow failed: No video output found")
        return False
        
    except Exception as e:
        print(f"❌ Full workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run end-to-end test"""
    print("🚀 Starting OTTO_Magic End-to-End Test...\n")
    
    # Create necessary directories
    Path("generated_assets/visuals").mkdir(parents=True, exist_ok=True)
    Path("generated_assets/audio").mkdir(parents=True, exist_ok=True)
    Path("final_videos").mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("OTTO_Magic End-to-End Workflow Test")
    print("="*60)
    
    success = test_full_workflow()
    
    print("\n" + "="*60)
    print("END-TO-END TEST SUMMARY")
    print("="*60)
    
    if success:
        print("🎉 SUCCESS: OTTO_Magic end-to-end workflow is working!")
        print("\nThe system can now:")
        print("• Generate visual content (with placeholder when APIs fail)")
        print("• Generate audio content (with placeholder)")
        print("• Assemble final videos using FFmpeg")
        print("• Handle the complete workflow from start to finish")
    else:
        print("❌ FAILED: End-to-end workflow needs fixes")

if __name__ == "__main__":
    main()
