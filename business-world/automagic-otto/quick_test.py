#!/usr/bin/env python3
"""Quick test to check if automagic.py imports without errors"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing automagic.py import...")
    import automagic
    print("✓ Import successful!")
    
    # Test class instantiation
    print("Testing VideoProduction class...")
    video_prod = automagic.VideoProduction()
    print("✓ VideoProduction class instantiated successfully!")
    
    print("\n=== All basic tests passed! ===")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ General error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
