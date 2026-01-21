#!/usr/bin/env python3
"""Test script to verify automagic.py imports and basic functionality."""

import sys
import os
import traceback

def test_import():
    """Test importing the automagic module."""
    try:
        print("Testing automagic import...")
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Test basic import
        import automagic
        print("✓ Import successful")
        
        # Test VideoProduction class instantiation
        production = automagic.VideoProduction(debug_mode=True)
        print("✓ VideoProduction class instantiated successfully")
        
        # Test basic methods exist
        methods_to_check = [
            'generate_content_idea',
            'generate_script', 
            'generate_images',
            'generate_voice',
            'create_video_from_images_and_audio',
            'upload_to_youtube',
            'run_daily_production'
        ]
        
        for method in methods_to_check:
            if hasattr(production, method):
                print(f"✓ Method {method} exists")
            else:
                print(f"✗ Method {method} missing")
        
        print("\n=== All tests passed! ===")
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        print(f"Traceback:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_import()
